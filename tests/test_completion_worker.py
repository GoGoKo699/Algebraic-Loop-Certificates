"""Tiny orchestration checks; native acceptance is qualified separately."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research.completion_v1.worker import NATIVE_TOOLS, OBLIGATIONS, Workflow, argument_parser


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "research/odd_order_witness_v1/models/rotation3.aag"


class MockNative:
    """Exercise orchestration exits/artifact presence, not mathematical truth."""

    def __init__(self, failure=None, verdict="UNSAT"):
        self.failure = failure
        self.verdict = verdict
        self.names = []

    def __call__(self, command, *, cwd, record_path, stdout_path, stderr_path,
                 output_limit_bytes):
        name = stdout_path.name.removesuffix(".stdout.txt")
        self.names.append(name)
        stdout, code, status = "", 0, "completed"
        executable = Path(command[0]).name
        if executable == "ric3":
            stdout = self.verdict + "\n"
            if self.failure != "missing_witness":
                (cwd / "witness.aag").write_bytes((cwd / "model.aag").read_bytes())
        elif executable == "certifaiger":
            (cwd / "check.aig").write_bytes(b"mock obligations")
        elif executable == "aigsplit":
            names = OBLIGATIONS[:-1] if self.failure == "missing_obligation" else OBLIGATIONS
            for obligation in names:
                (cwd / (obligation + ".aig")).write_bytes(b"mock obligation")
        elif executable == "aigtocnf":
            (cwd / command[-1]).write_bytes(b"p cnf 1 2\n1 0\n-1 0\n")
        elif executable == "cadical":
            code = 10 if self.failure == "sat" and name == "Safety_solve" else 20
            (cwd / command[-1]).write_bytes(b"3 0 1 2 0\n")
        elif executable == "lrat-trim":
            code = 1 if self.failure == "bad_proof" and name == "Reset_replay" else 20
        if self.failure == "crash" and name == "generate":
            code = -11
        if self.failure == "output_limit" and name == "generate":
            status = "output_limit"
        stdout_path.write_text(stdout)
        stderr_path.write_text("")
        result = {"status": status, "exit_code": code, "command": command,
                "stdout": stdout, "stderr": "", "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path), "stdout_bytes": len(stdout), "stderr_bytes": 0,
                "stdout_truncated": False, "stderr_truncated": False,
                "wall_seconds": 0.0, "cpu_user_seconds": 0.0, "cpu_system_seconds": 0.0}
        if self.failure == "file_size_limit" and name == "generate":
            result.update(exit_code=-25, resource_signal="file_size_limit")
        return result


class CompletionWorker(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.tools = self.base / "tools"
        self.tools.mkdir()
        for name in NATIVE_TOOLS + ("ric3",):
            tool = self.tools / name
            tool.write_text("unused mock tool\n")
            tool.chmod(0o700)

    def tearDown(self):
        self.temporary.cleanup()

    def arguments(self, case, route="exporter", extra=()):
        return argument_parser().parse_args([
            "--route", route, "--model", str(MODEL), "--tools", str(self.tools),
            "--output", str(self.base / case), "--width", "3", "--taps", "4",
            "--odd-multiple", "9", *extra])

    def test_acceptance_requires_all_nine_proofs_and_distinguishes_failures(self):
        runner = MockNative()
        result = Workflow(self.arguments("good"), runner).execute()
        self.assertEqual(result["status"], "accepted")
        self.assertEqual([row["name"] for row in result["obligations"]], list(OBLIGATIONS))
        self.assertTrue(all(row["status"] == "unsat_replayed" for row in result["obligations"]))
        self.assertEqual(runner.names, ["generate", "split"] + [
            name + suffix for name in OBLIGATIONS for suffix in ("_cnf", "_solve", "_replay")])
        self.assertEqual(json.loads((self.base / "good/RESULT.json").read_text()),
                         json.loads((self.base / "good/JOURNAL.json").read_text()))
        for failure, expected in (("sat", "rejected"), ("bad_proof", "error"),
                                  ("missing_obligation", "blocked"), ("crash", "error"),
                                  ("output_limit", "unknown"), ("file_size_limit", "unknown")):
            with self.subTest(failure=failure):
                runner = MockNative(failure=failure)
                result = Workflow(self.arguments(failure), runner).execute()
                self.assertEqual(result["status"], expected)
                self.assertNotIn("Consistent_replay", runner.names)
                if failure == "sat":
                    self.assertNotIn("Safety_replay", runner.names)

    def test_ric3_safe_text_is_required_but_never_sufficient(self):
        for index, (verdict, failure, expected) in enumerate((
                ("UNSAT", None, "accepted"), ("SAT", None, "error"),
                ("UNKNOWN", None, "unknown"), ("UNSAT\nSAT", None, "blocked"),
                ("logged UNSAT without a result", None, "blocked"),
                ("UNSAT", "missing_witness", "blocked"), ("UNSAT", "sat", "rejected"))):
            with self.subTest(verdict=verdict, failure=failure):
                runner = MockNative(failure=failure, verdict=verdict)
                result = Workflow(self.arguments("ric3-" + str(index), "ric3"), runner).execute()
                self.assertEqual(result["status"], expected)
                ric3 = next(row for row in result["phases"] if row["name"] == "ric3")
                self.assertEqual(ric3["argv"][1:],
                                 ["check", "model.aag", "--cert", "witness.aag", "--ui", "false", "ic3",
                                  "--rseed", "0"])

    def test_structural_cli_and_invalid_hints_are_separate_from_witness_acceptance(self):
        command = [sys.executable, "-m", "research.completion_v1.worker", "--route", "structural",
                   "--model", str(MODEL), "--output", str(self.base / "structural"),
                   "--width", "3", "--taps", "4"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["status"], "structural_accepted")
        for index, extra in enumerate((("--width", "4"), ("--taps", "3"), ("--odd-multiple", "7"))):
            with self.subTest(hint=extra):
                runner = MockNative()
                result = Workflow(self.arguments("bad-hint-" + str(index), extra=extra), runner).execute()
                self.assertEqual(result["status"], "unsupported")
                self.assertEqual(runner.names, [])

    def test_existing_evidence_is_never_overwritten(self):
        args = self.arguments("already-present")
        args.output.mkdir()
        marker = args.output / "RESULT.json"
        marker.write_text("earlier evidence")
        with self.assertRaises(ValueError):
            Workflow(args, MockNative()).execute()
        self.assertEqual(marker.read_text(), "earlier evidence")


if __name__ == "__main__":
    unittest.main()
