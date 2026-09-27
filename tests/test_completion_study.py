"""Protect frozen provenance and conservative study stopping decisions."""

import copy
from contextlib import redirect_stdout
from dataclasses import asdict
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from research.completion_v1 import study
from research.completion_v1.resources import Limits


ORIGINAL_ROOT = study.ROOT


class CompletionStudy(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root = self.base / "repository"
        for relative in study.SOURCES:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ORIGINAL_ROOT / relative, target)
        for case in study.case_records():
            target = self.root / case["model"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ORIGINAL_ROOT / case["model"], target)
        self.here = self.root / "research/completion_v1"
        self.tools = self.base / "tools"
        self.tools.mkdir()
        for name in study.TOOLS:
            (self.tools / name).write_text("qualified test bytes for " + name)
        self.hashes = {name: study.sha(self.tools / name) for name in study.TOOLS}
        qualification = self.here / "qualification/MANIFEST.json"
        qualification.parent.mkdir()
        qualification.write_text(json.dumps({"binary_sha256": self.hashes}))
        self.root_patch = patch.object(study, "ROOT", self.root)
        self.here_patch = patch.object(study, "HERE", self.here)
        self.root_patch.start()
        self.here_patch.start()
        self.record = {
            "schema": 1, "kind": "fixed_completion_study_before_measurement",
            "source_files_sha256": {p: study.sha(self.root / p) for p in study.SOURCES},
            "qualification_manifest_sha256": study.sha(qualification),
            "binary_sha256": self.hashes,
            "python": {"executable": sys.executable, "version": sys.version,
                       "sha256": study.sha(Path(sys.executable))},
            "limits": asdict(Limits(cpu=min(os.sched_getaffinity(0)))),
            "environment_overrides": {"PYTHONHASHSEED": "0", "LC_ALL": "C", "RUST_LOG": "info"},
            "cases": study.case_records(), "order": study.trial_order(), "seed": 0,
        }
        self.freeze = self.base / "PROTOCOL_FREEZE.json"
        self.save_freeze(self.record)

    def tearDown(self):
        self.here_patch.stop()
        self.root_patch.stop()
        self.temporary.cleanup()

    def save_freeze(self, record):
        self.freeze.write_text(json.dumps(record))

    def test_freeze_rejects_changed_policy_sources_inputs_and_executables(self):
        self.assertEqual(study.validate_freeze(self.freeze, self.tools), self.record)
        for field in ("limits", "order"):
            changed = copy.deepcopy(self.record)
            if field == "limits":
                changed["limits"]["wall_seconds"] += 1
            else:
                changed["order"].reverse()
            self.save_freeze(changed)
            with self.subTest(field=field), self.assertRaises(ValueError):
                study.validate_freeze(self.freeze, self.tools)
        self.save_freeze(self.record)
        for label, path in (("worker", self.root / "research/completion_v1/worker.py"),
                            ("binary", self.tools / "ric3"),
                            ("input", self.root / self.record["cases"][0]["model"])):
            original = path.read_bytes()
            path.write_bytes(original + b"\nchanged\n")
            with self.subTest(label=label), self.assertRaises(ValueError):
                study.validate_freeze(self.freeze, self.tools)
            path.write_bytes(original)
        # An edited freeze must not silently turn a replacement executable into
        # a qualified one merely by copying its new hash into that freeze.
        (self.tools / "ric3").write_text("unqualified replacement")
        changed = copy.deepcopy(self.record)
        changed["binary_sha256"]["ric3"] = study.sha(self.tools / "ric3")
        self.save_freeze(changed)
        with self.assertRaises(ValueError):
            study.validate_freeze(self.freeze, self.tools)

    def test_existing_freeze_refuses_before_replaying_qualification(self):
        with patch("research.completion_v1.verify_qualification.verify_qualification") as verify:
            with self.assertRaises(ValueError):
                study.freeze(self.tools, self.freeze)
            verify.assert_not_called()

    def execute_mock(self, name, observation, result, *, journal=None, files=None):
        record = copy.deepcopy(self.record)
        record["order"] = [
            {"id": "first", "width": 2, "trial": 1, "route": "exporter"},
            {"id": "second", "width": 2, "trial": 1, "route": "ric3"},
        ]
        calls = []

        def run(command, *, cwd, artifact_root, env, limits):
            calls.append(command)
            data = artifact_root / "data"
            data.mkdir()
            selected = result if len(calls) == 1 else {"route": "ric3", "status": "accepted"}
            if selected is not None:
                (data / "RESULT.json").write_text(json.dumps(selected))
            else:
                selected_journal = journal if journal is not None else {"status": "incomplete"}
                (data / "JOURNAL.json").write_text(json.dumps(selected_journal))
            if len(calls) == 1:
                for filename, contents in (files or {}).items():
                    (data / filename).write_text(contents)
            return observation if len(calls) == 1 else {"status": "completed", "reason": None}

        output = self.base / name
        with patch.object(study, "validate_freeze", return_value=record), \
                patch("research.completion_v1.resources.run_workflow", side_effect=run), \
                redirect_stdout(io.StringIO()):
            try:
                study.execute(self.freeze, self.tools, output)
            except ValueError:
                suspended = True
            else:
                suspended = False
        return output, calls, suspended

    def test_only_attributed_budget_exhaustion_continues_the_fixed_sequence(self):
        for reason in ("deadline", "artifact_limit"):
            with self.subTest(reason=reason):
                output, calls, suspended = self.execute_mock(
                    "limited-" + reason, {"status": "resource_limit", "reason": reason}, None)
                self.assertFalse(suspended)
                self.assertEqual(len(calls), 2)
                self.assertFalse((output / "SUSPENDED.json").exists())
                self.assertTrue((output / "first/ARTIFACTS.json").is_file())
        cases = (
            ({"status": "resource_limit", "reason": "trial_storage_limit"}, None),
            ({"status": "resource_limit", "reason": "output_limit"}, None),
            ({"status": "infrastructure_error", "reason": "descendant_cleanup_failed"}, None),
            ({"status": "completed"}, {"route": "exporter", "status": "rejected"}),
            ({"status": "completed"}, {"route": "exporter", "status": "unsupported"}),
            ({"status": "completed"}, {"route": "exporter", "status": "unknown",
                                       "reason": "Python MemoryError; allocation-failure cause is not attributed"}),
            ({"status": "completed"}, {"route": "exporter", "status": "structural_accepted"}),
            ({"status": "completed"}, {"route": "structural", "status": "accepted"}),
        )
        for index, (observation, result) in enumerate(cases):
            with self.subTest(index=index):
                output, calls, suspended = self.execute_mock("suspended-" + str(index), observation, result)
                self.assertTrue(suspended)
                self.assertEqual(len(calls), 1)
                self.assertTrue((output / "SUSPENDED.json").is_file())
                self.assertTrue((output / "first/ARTIFACTS.json").is_file())

    def test_a_later_resource_limit_never_hides_a_retained_execution_failure(self):
        for reason in ("deadline", "artifact_limit"):
            for status in ("rejected", "error", "unknown"):
                with self.subTest(reason=reason, worker=status):
                    output, calls, suspended = self.execute_mock(
                        "mixed-" + reason + "-" + status,
                        {"status": "resource_limit", "reason": reason,
                         "observed_violations": [reason]},
                        {"route": "exporter", "status": status,
                         "reason": "Retained failure without an attributable budget cause"})
                    self.assertTrue(suspended)
                    self.assertEqual(len(calls), 1)
                    self.assertTrue((output / "SUSPENDED.json").is_file())
                    self.assertTrue((output / "first/ARTIFACTS.json").is_file())
            with self.subTest(reason=reason, mixed_violation="output_limit"):
                output, calls, suspended = self.execute_mock(
                    "mixed-" + reason + "-output",
                    {"status": "resource_limit", "reason": reason,
                     "observed_violations": [reason, "output_limit"]}, None)
                self.assertTrue(suspended)
                self.assertEqual(len(calls), 1)
                self.assertTrue((output / "SUSPENDED.json").is_file())

    def test_incomplete_journal_preserves_scientific_failure_at_the_deadline(self):
        journals = (
            {"status": "incomplete", "obligations": [{"name": "Safety", "status": "sat"}]},
            {"status": "incomplete", "phases": [{
                "name": "Safety_solve", "status": "completed",
                "process": {"status": "completed", "exit_code": 10}}]},
            {"status": "error", "reason": "Native proof replay failed"},
        )
        for index, journal in enumerate(journals):
            with self.subTest(journal=index):
                output, calls, suspended = self.execute_mock(
                    "journal-failure-" + str(index),
                    {"status": "resource_limit", "reason": "deadline",
                     "observed_violations": ["deadline"]}, None, journal=journal)
                self.assertTrue(suspended)
                self.assertEqual(len(calls), 1)
                self.assertTrue((output / "SUSPENDED.json").is_file())
                self.assertTrue((output / "first/ARTIFACTS.json").is_file())
        # A stage interrupted before any contradictory result is an ordinary
        # observed deadline outcome and must not suspend the fixed order.
        output, calls, suspended = self.execute_mock(
            "journal-pure-deadline",
            {"status": "resource_limit", "reason": "deadline",
             "observed_violations": ["deadline"]}, None,
            journal={"status": "incomplete", "route": "exporter",
                     "phases": [{"name": "Safety_solve", "status": "running"}]})
        self.assertFalse(suspended)
        self.assertEqual(len(calls), 2)
        self.assertFalse((output / "SUSPENDED.json").exists())

    def test_definitive_retained_logs_precede_the_final_journal_update(self):
        failed_finish = json.dumps({"event": "finish", "command": ["/tools/cadical"],
                                    "status": "completed", "exit_code": 10}) + "\n"
        successful_finish = json.dumps({"event": "finish", "command": ["/tools/lrat-trim"],
                                        "status": "completed", "exit_code": 20}) + "\n"
        partial = '{"event": "finish", "command": ['
        cases = (
            ({"Safety_solve.stdout.txt": "s SATISFIABLE\n"}, True),
            ({"ric3.stdout.txt": "SAT\n"}, True),
            ({"ric3.stdout.txt": "UNKNOWN\n"}, True),
            ({"STAGES.jsonl": failed_finish}, True),
            ({"STAGES.jsonl": failed_finish + partial}, True),
            ({"STAGES.jsonl": successful_finish + partial}, False),
        )
        for index, (files, expected_suspension) in enumerate(cases):
            with self.subTest(logs=index):
                output, calls, suspended = self.execute_mock(
                    "log-window-" + str(index),
                    {"status": "resource_limit", "reason": "deadline",
                     "observed_violations": ["deadline"]}, None, files=files)
                self.assertEqual(suspended, expected_suspension)
                self.assertEqual(len(calls), 1 if expected_suspension else 2)
                self.assertEqual((output / "SUSPENDED.json").exists(), expected_suspension)
                self.assertTrue((output / "first/ARTIFACTS.json").is_file())
        # An output capture violation cannot be hidden by a simultaneous file
        # size signal, even when the aggregate raw-artifact limit was observed.
        combined = json.dumps({"event": "finish", "command": ["/tools/cadical"],
                               "status": "output_limit", "exit_code": -25,
                               "resource_signal": "file_size_limit"}) + "\n"
        output, calls, suspended = self.execute_mock(
            "mixed-stage-output-and-file-limit",
            {"status": "resource_limit", "reason": "artifact_limit",
             "observed_violations": ["artifact_limit"]}, None,
            files={"STAGES.jsonl": combined})
        self.assertTrue(suspended)
        self.assertEqual(len(calls), 1)
        self.assertTrue((output / "SUSPENDED.json").is_file())


if __name__ == "__main__":
    unittest.main()
