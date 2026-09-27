"""Record-validation unit tests; these are NOT substitutes for native replay."""
import os
import subprocess
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research.completion_v1 import qualify_native as q


class QualificationRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("model", "witness"):
            (self.root / (name + ".aag")).write_text(name)

    @unittest.skipUnless(os.name == "posix", "Native executable mode is a POSIX contract")
    def test_staged_executable_keeps_permission_and_runs(self):
        source, destination = self.root / "built-tool", self.root / "staged-tool"
        source.write_text("#!/bin/sh\nexit 0\n")
        source.chmod(0o755)
        q.copy_executable(source, destination)
        self.assertEqual(source.read_bytes(), destination.read_bytes())
        self.assertTrue(os.access(destination, os.X_OK))
        subprocess.run([str(destination)], check=True, timeout=5)

    @unittest.skipUnless(os.name == "posix", "Native executable mode is a POSIX contract")
    def test_nonexecutable_build_output_is_rejected(self):
        source = self.root / "not-executable"
        source.write_text("not a tool")
        source.chmod(0o644)
        with self.assertRaises(ValueError):
            q.copy_executable(source, self.root / "destination")

    def record(self, rejection=None):
        names = q.OBLIGATIONS if rejection is None else q.OBLIGATIONS[:q.OBLIGATIONS.index(rejection) + 1]
        result = {"status": "accepted" if rejection is None else "rejected",
                  "input_sha256": {n: q.sha(self.root / (n + ".aag")) for n in ("model", "witness")},
                  "obligations": [], "stages": []}
        def stage(name, code):
            result["stages"].append({"name": name, "exit_code": code, "timed_out": False})
        stage("generate", 0)
        stage("split", 0)
        for name in names:
            stage(name + "_cnf", 0)
            stage(name + "_solve", 10 if name == rejection else 20)
            row = {"name": name, "status": "sat" if name == rejection else "unsat_replayed"}
            if name == rejection:
                (self.root / (name + "_solve.stdout.txt")).write_text("s SATISFIABLE\n")
            else:
                stage(name + "_replay", 20)
                for suffix, field in ((".cnf", "cnf_sha256"), (".lrat", "proof_sha256")):
                    path = self.root / (name + suffix)
                    path.write_text("synthetic record-test placeholder; not a proof\n")
                    row[field] = q.sha(path)
            result["obligations"].append(row)
        return result

    def write(self, record):
        (self.root / "RESULTS.json").write_text(json.dumps(record))

    def test_positive_record_routes_every_obligation_to_replay(self):
        self.write(self.record())
        with patch.object(q, "check_lrat", return_value={"status": "verified_unsat"}) as replay:
            result = q.inspect_case(self.root)
        self.assertEqual(replay.call_count, 9)
        self.assertEqual(len(result["independent_replays"]), 9)

    def test_all_negative_control_positions(self):
        for rejection in ("Safety", "Reset", "Inductive"):
            self.write(self.record(rejection))
            with patch.object(q, "check_lrat", return_value={"status": "verified_unsat"}) as replay:
                result = q.inspect_case(self.root, rejection)
            self.assertEqual(replay.call_count, q.OBLIGATIONS.index(rejection))
            self.assertEqual(result["status"], "rejected")

    def test_missing_obligation(self):
        record = self.record()
        record["obligations"].pop()
        self.write(record)
        with self.assertRaises(ValueError):
            q.inspect_case(self.root)

    def test_safe_message_cannot_replace_proof(self):
        record = self.record()
        record["stages"][4]["exit_code"] = 0
        self.write(record)
        with self.assertRaises(ValueError):
            q.inspect_case(self.root)

    def test_changed_input_is_rejected(self):
        self.write(self.record())
        (self.root / "model.aag").write_text("different model")
        with self.assertRaises(ValueError):
            q.inspect_case(self.root)

    def test_changed_proof_is_rejected_before_replay(self):
        self.write(self.record())
        (self.root / "Reset.lrat").write_text("changed")
        with self.assertRaises(ValueError):
            q.inspect_case(self.root)

    def test_independent_replay_failure_is_not_qualified(self):
        self.write(self.record())
        with patch.object(q, "check_lrat", side_effect=ValueError("invalid proof")):
            with self.assertRaises(ValueError):
                q.inspect_case(self.root)

    def test_timeout_is_not_acceptance(self):
        record = self.record()
        record["stages"][0]["timed_out"] = True
        self.write(record)
        with self.assertRaises(ValueError):
            q.inspect_case(self.root)

    def test_counterfeit_control_acceptance_is_rejected(self):
        self.write(self.record())
        with self.assertRaises(ValueError):
            q.inspect_case(self.root, "Safety")


if __name__ == "__main__":
    unittest.main()
