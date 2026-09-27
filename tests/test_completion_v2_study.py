"""Keep the amended experiment prospective, separate, and fail closed."""
from contextlib import redirect_stdout
import copy
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

from research.completion_v1 import study as prior_study
from research.completion_v2 import study
from research.completion_v2.resources import Limits

ORIGINAL_ROOT = study.ROOT


class AmendedCompletionStudy(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
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
        self.here = self.root / "research/completion_v2"
        self.tools = self.base / "tools"
        self.tools.mkdir()
        for name in study.TOOLS:
            (self.tools / name).write_text("unchanged qualified test executable " + name)
        self.hashes = {name: study.sha(self.tools / name) for name in study.TOOLS}
        old_qualification = self.root / study.PRIOR_QUALIFICATION
        old_qualification.write_text(json.dumps({"binary_sha256": self.hashes}))
        old_freeze_path = self.root / study.PRIOR_FREEZE
        old_freeze = json.loads(old_freeze_path.read_text())
        old_freeze["binary_sha256"] = self.hashes
        old_freeze["qualification_manifest_sha256"] = study.sha(old_qualification)
        old_freeze_path.write_text(json.dumps(old_freeze))
        qualification = self.here / "qualification/MANIFEST.json"
        qualification.parent.mkdir()
        qualification.write_text(json.dumps({"binary_sha256": self.hashes}))
        for module, name, value in ((study, "ROOT", self.root), (study, "HERE", self.here),
                                    (prior_study, "ROOT", self.root)):
            patcher = patch.object(module, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.record = {
            "schema": 2, "kind": study.KIND,
            "source_files_sha256": {p: study.sha(self.root / p) for p in study.SOURCES},
            "qualification_manifest_sha256": study.sha(qualification),
            "binary_sha256": self.hashes,
            "python": {"executable": sys.executable, "version": sys.version,
                       "sha256": study.sha(Path(sys.executable))},
            "limits": asdict(Limits(cpu=old_freeze["limits"]["cpu"])),
            "environment_overrides": dict(study.ENVIRONMENT),
            "cases": study.case_records(), "order": study.trial_order(), "seed": 0,
            **study.history_bindings(),
        }
        self.freeze = self.base / "PROTOCOL_FREEZE.json"
        self.save_freeze(self.record)

    def save_freeze(self, record):
        self.freeze.write_text(json.dumps(record))

    def test_history_sources_models_and_binaries_are_bound(self):
        self.assertEqual(study.validate_freeze(self.freeze, self.tools), self.record)
        paths = [self.root / study.PRIOR_FREEZE, self.root / study.PRIOR_ARCHIVE,
                 self.root / "research/completion_v2/resources.py",
                 self.root / "research/completion_v2/STORAGE_AMENDMENT.md",
                 self.root / self.record["cases"][0]["model"], self.tools / "ric3"]
        for path in paths:
            original = path.read_bytes()
            path.write_bytes(original + b"\nchanged\n")
            with self.subTest(path=str(path)), self.assertRaises(ValueError):
                study.validate_freeze(self.freeze, self.tools)
            path.write_bytes(original)
        # Rewriting the new freeze's dependency hash cannot authorize modifying
        # the previously frozen worker: the original freeze still binds it.
        worker = "research/completion_v1/worker.py"
        (self.root / worker).write_bytes((self.root / worker).read_bytes() + b"\nchanged\n")
        changed = copy.deepcopy(self.record)
        changed["source_files_sha256"][worker] = study.sha(self.root / worker)
        self.save_freeze(changed)
        with self.assertRaisesRegex(ValueError, "Prior frozen source changed"):
            study.validate_freeze(self.freeze, self.tools)

    def test_only_declared_storage_amendment_and_whole_sequence_are_allowed(self):
        alterations = []
        for key in ("artifact_bytes", "metadata_bytes", "wall_seconds"):
            changed = copy.deepcopy(self.record)
            changed["limits"][key] *= 2
            alterations.append((key, changed))
        for name, value in (("order", self.record["order"][1:]),
                            ("order", list(reversed(self.record["order"]))),
                            ("restart_policy", "resume suspended trials"),
                            ("kind", "fixed_completion_study_before_measurement")):
            changed = copy.deepcopy(self.record)
            changed[name] = value
            alterations.append((name, changed))
        changed = copy.deepcopy(self.record)
        del changed["source_files_sha256"][study.PRIOR_ARCHIVE]
        alterations.append(("missing previous archive", changed))
        changed = copy.deepcopy(self.record)
        changed["prior_study_archive_manifest"]["sha256"] = "0" * 64
        alterations.append(("changed previous archive link", changed))
        for label, record in alterations:
            self.save_freeze(record)
            with self.subTest(change=label), self.assertRaises(ValueError):
                study.validate_freeze(self.freeze, self.tools)
        self.assertEqual(len(study.trial_order()), 54)
        self.assertEqual(study.trial_order(), prior_study.trial_order())

    def test_new_freeze_records_qualification_and_refuses_overwrite(self):
        target = self.base / "fresh-freeze.json"
        summary = {"proofs_checked": 23, "sat_assignments_checked": 2}
        with patch("research.completion_v2.verify_qualification.verify_qualification", return_value=summary) as verify:
            result = study.freeze(self.tools, target)
            self.assertEqual(result["planned_trials"], 54)
            verify.assert_called_once_with()
            record = study.validate_freeze(target, self.tools)
            self.assertEqual(record["qualification_summary"], summary)
            self.assertEqual(record["restart_policy"], study.RESTART_POLICY)
            verify.reset_mock()
            original = target.read_bytes()
            with self.assertRaisesRegex(ValueError, "overwrite"):
                study.freeze(self.tools, target)
            verify.assert_not_called()
            self.assertEqual(target.read_bytes(), original)

    def test_new_freeze_requires_the_originally_qualified_executables(self):
        (self.tools / "ric3").write_text("new executable")
        qualification = self.here / "qualification/MANIFEST.json"
        hashes = dict(self.hashes, ric3=study.sha(self.tools / "ric3"))
        qualification.write_text(json.dumps({"binary_sha256": hashes}))
        with patch("research.completion_v2.verify_qualification.verify_qualification", return_value={}):
            with self.assertRaisesRegex(ValueError, "previously and newly qualified"):
                study.freeze(self.tools, self.base / "changed-binary-freeze.json")

    def execute_mock(self, name, observation, result=None, *, journal=None, files=None):
        record = copy.deepcopy(self.record)
        record["order"] = [
            {"id": "first", "width": 2, "trial": 1, "route": "exporter"},
            {"id": "second", "width": 2, "trial": 1, "route": "ric3"},
        ]
        calls = []

        def run(command, *, cwd, artifact_root, env, limits):
            calls.append(command)
            self.assertEqual(limits.metadata_bytes, 64 << 20)
            self.assertEqual(limits.artifact_bytes, 64 << 20)
            self.assertIn("research.completion_v1.worker", command)
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
                patch("research.completion_v2.resources.run_workflow", side_effect=run), \
                redirect_stdout(io.StringIO()):
            try:
                study.execute(self.freeze, self.tools, output)
            except ValueError:
                suspended = True
            else:
                suspended = False
        return output, calls, suspended

    def test_metadata_never_becomes_an_eligible_resource_outcome(self):
        observations = [
            {"status": "resource_limit", "reason": "metadata_limit"},
            {"status": "resource_limit", "reason": "metadata_limit",
             "observed_violations": ["metadata_limit", "artifact_limit", "deadline"]},
            {"status": "resource_limit", "reason": "artifact_limit",
             "observed_violations": ["artifact_limit", "metadata_limit"]},
            {"status": "resource_limit", "reason": "deadline",
             "observed_violations": ["deadline", "metadata_limit"]},
            {"status": "completed", "reason": "metadata_limit"},
            {"status": "completed", "reason": None, "observed_violations": ["metadata_limit"]},
        ]
        for i, observation in enumerate(observations):
            with self.subTest(observation=observation):
                output, calls, suspended = self.execute_mock(
                    "metadata-" + str(i), observation,
                    {"route": "exporter", "status": "accepted"})
                self.assertTrue(suspended)
                self.assertEqual(len(calls), 1)
                self.assertTrue((output / "first/ARTIFACTS.json").exists())
                self.assertTrue((output / "SUSPENDED.json").exists())

    def test_only_clean_success_or_attributed_raw_and_time_limits_continue(self):
        observations = [
            ({"status": "completed", "reason": None}, {"route": "exporter", "status": "accepted"}),
            ({"status": "resource_limit", "reason": "deadline", "observed_violations": ["deadline"]}, None),
            ({"status": "resource_limit", "reason": "artifact_limit", "observed_violations": ["artifact_limit"]}, None),
        ]
        for i, (observation, result) in enumerate(observations):
            with self.subTest(observation=observation):
                output, calls, suspended = self.execute_mock("allowed-" + str(i), observation, result)
                self.assertFalse(suspended)
                self.assertEqual(len(calls), 2)
                self.assertFalse((output / "SUSPENDED.json").exists())

    def test_retained_failures_outrank_later_deadline_or_raw_limit(self):
        for i, reason in enumerate(("deadline", "artifact_limit")):
            for j, (result, journal, files) in enumerate((
                    ({"route": "exporter", "status": "rejected"}, None, None),
                    (None, {"status": "incomplete", "obligations": [{"status": "sat"}]}, None),
                    (None, None, {"Safety_solve.stdout.txt": "s SATISFIABLE\n"}),
                    (None, None, {"ric3.stdout.txt": "UNKNOWN\n"}),
                    (None, None, {"STAGES.jsonl": json.dumps({"event": "finish", "command": ["/tools/cadical"],
                                                           "status": "completed", "exit_code": 10}) + "\n"}),
            )):
                with self.subTest(reason=reason, failure=j):
                    output, calls, suspended = self.execute_mock(
                        f"failed-{i}-{j}", {"status": "resource_limit", "reason": reason,
                                           "observed_violations": [reason]}, result, journal=journal, files=files)
                    self.assertTrue(suspended)
                    self.assertEqual(len(calls), 1)
                    self.assertTrue((output / "first/ARTIFACTS.json").exists())

    def test_existing_output_is_preserved_and_never_resumed(self):
        output = self.base / "prior-attempt"
        output.mkdir()
        evidence = output / "SUSPENDED.json"
        evidence.write_text("previous evidence")
        with patch.object(study, "validate_freeze", return_value=self.record), \
                patch("research.completion_v2.resources.run_workflow") as run:
            with self.assertRaisesRegex(ValueError, "repeat or overwrite"):
                study.execute(self.freeze, self.tools, output)
            run.assert_not_called()
        self.assertEqual(evidence.read_text(), "previous evidence")
        self.assertEqual(list(output.iterdir()), [evidence])


if __name__ == "__main__":
    unittest.main()
