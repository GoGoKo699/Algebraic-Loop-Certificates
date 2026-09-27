"""Independent adversarial controls for the Linux workflow supervisor.

These are small harness tests, not benchmark observations. They exercise real
processes and kernel limits, including detached descendants and deleted files.
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from research.completion_v1.resources import Limits, _artifact_size, run_workflow


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == "linux", "Linux resource supervisor")
class CompletionResources(unittest.TestCase):
    def trial(self, code, directory, **limits):
        return run_workflow([sys.executable, "-c", code], cwd=directory,
                            artifact_root=directory, limits=Limits(**limits),
                            env={"PYTHONPATH": str(ROOT)})

    def test_worker_and_stage_inherit_limits_with_raw_log_and_command_records(self):
        code = r'''
import json, os, resource, sys
from research.completion_v1.resources import run_stage
child = "import os,resource,json; print(json.dumps({'affinity':sorted(os.sched_getaffinity(0)), 'as':resource.getrlimit(resource.RLIMIT_AS), 'fsize':resource.getrlimit(resource.RLIMIT_FSIZE)}))"
stage = run_stage([sys.executable, '-c', child], record_path='STAGES.jsonl', stdout_path='child.stdout', stderr_path='child.stderr')
print(json.dumps({'worker_as':resource.getrlimit(resource.RLIMIT_AS), 'stage':stage}))
'''
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory)
            self.assertEqual(result["status"], "completed", result)
            self.assertEqual(result["exit_code"], 0)
            self.assertTrue(result["cleanup"]["complete"])
            worker = json.loads(result["stdout"])
            self.assertEqual(worker["worker_as"], [1024 ** 3] * 2)
            stage = worker["stage"]
            self.assertEqual(stage["exit_code"], 0)
            child = json.loads(stage["stdout"])
            self.assertEqual(child["affinity"], [result["cpu"]])
            self.assertEqual(child["as"], [1024 ** 3] * 2)
            self.assertEqual(child["fsize"], [64 * 1024 ** 2] * 2)
            self.assertEqual((Path(directory) / "child.stdout").read_bytes(), stage["stdout"].encode())
            events = [json.loads(line) for line in (Path(directory) / "STAGES.jsonl").read_text().splitlines()]
            self.assertEqual([event["event"] for event in events], ["start", "finish"])
            self.assertEqual(events[0]["command"], stage["command"])
            self.assertGreater(result["wall_seconds"], stage["wall_seconds"])
            self.assertFalse(result["instantaneous_aggregate_quota"])

    def test_total_deadline_is_not_reset_between_stages(self):
        code = r'''
import sys
from research.completion_v1.resources import run_stage
for i in range(3):
    run_stage([sys.executable, '-c', 'import time; time.sleep(.25)'], record_path='STAGES.jsonl')
'''
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory, wall_seconds=0.55)
            self.assertEqual((result["status"], result["reason"]), ("resource_limit", "deadline"), result)
            self.assertTrue(result["cleanup"]["complete"])
            self.assertLess(result["wall_seconds"], 1.5)
            events = [json.loads(line) for line in (Path(directory) / "STAGES.jsonl").read_text().splitlines()]
            self.assertGreater(sum(event["event"] == "start" for event in events),
                               sum(event["event"] == "finish" for event in events))

    def test_double_fork_and_setsid_cannot_outlive_deadline(self):
        code = r'''
import os, pathlib, time
pid = os.fork()
if pid == 0:
    os.setsid()
    if os.fork():
        os._exit(0)
    pathlib.Path('escaped.pid').write_text(str(os.getpid()))
    while True: time.sleep(.02)
os.waitpid(pid, 0)
time.sleep(10)
'''
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory, wall_seconds=0.4)
            self.assertEqual(result["reason"], "deadline", result)
            self.assertTrue(result["cleanup"]["complete"], result)
            pid = int((Path(directory) / "escaped.pid").read_text())
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)

    def test_open_deleted_files_count_toward_aggregate_and_peak_is_retained(self):
        code = r'''
import os, time
handles=[]
for name in ('a.proof', 'b.proof'):
    f=open(name,'wb'); f.write(b'x'*12000); f.flush(); os.unlink(name); handles.append(f)
time.sleep(10)
'''
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory, artifact_bytes=20000, wall_seconds=2)
            self.assertEqual((result["status"], result["reason"]), ("resource_limit", "artifact_limit"), result)
            self.assertGreater(result["raw_artifact_peak_observed_bytes"], 20000)
            self.assertGreater(result["open_deleted_peak_observed_bytes"], 20000)
            self.assertLess(result["raw_artifact_bytes"], 20000)
            self.assertTrue(result["cleanup"]["complete"])

    def test_metadata_excess_is_not_a_raw_artifact_loss(self):
        code = "from pathlib import Path; import time; Path('a.stdout.txt').write_bytes(b'x'*12000); Path('b.json.tmp').write_bytes(b'x'*12000); time.sleep(10)"
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory, artifact_bytes=20000, wall_seconds=2)
            self.assertEqual(result["reason"], "trial_storage_limit", result)
            self.assertEqual(result["raw_artifact_bytes"], 0)
            self.assertGreater(result["all_trial_files_bytes"], 20000)

    def test_bounded_output_and_nonzero_exit_are_not_success_or_guessed_memory_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial("import os; os.write(1,b'x'*100000)", directory,
                                output_bytes=1024)
            self.assertEqual(result["reason"], "output_limit", result)
            self.assertEqual((Path(directory) / "workflow.stdout").stat().st_size, 1024)
            self.assertTrue(result["stdout_truncated"])
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial("raise SystemExit(42)", directory)
            self.assertEqual((result["status"], result["reason"], result["exit_code"]),
                             ("process_error", "worker_exit", 42))

    def test_address_limit_is_real_and_cannot_be_raised_by_child(self):
        code = r'''
import resource
try:
    resource.setrlimit(resource.RLIMIT_AS, (256*1024**2,256*1024**2))
except (ValueError, PermissionError):
    print('hard-limit-retained')
try:
    bytearray(256*1024**2)
except MemoryError:
    print('allocation-denied')
'''
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory, address_space_bytes=128 * 1024 ** 2)
            self.assertEqual(result["status"], "completed", result)
            self.assertEqual(result["stdout"].splitlines(), ["hard-limit-retained", "allocation-denied"])

    def test_symlink_artifact_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial("import os; os.symlink('/etc/passwd','escape.proof')", directory)
            self.assertEqual(result["status"], "infrastructure_error", result)
            self.assertTrue(result["cleanup"]["complete"])

    def test_proc_permission_race_requires_fresh_exit_and_process_identity(self):
        """Root-run tests must also cover unprivileged zombie fd permissions."""
        descendants = {123: (1, 777, "R")}
        cases = [("Z", 777, True), ("X", 777, True),
                 ("R", 777, False), ("Z", 888, False),
                 ("gone", 777, True), ("denied", 777, False)]
        for boundary in ("directory", "readlink", "stat"):
            for state, starttime, should_skip in cases:
                with self.subTest(boundary=boundary, state=state, starttime=starttime), tempfile.TemporaryDirectory() as directory:
                    fields = [state, "1"] + ["0"] * 17 + [str(starttime)]
                    fresh_stat = "123 (worker) " + " ".join(fields)
                    read_error = (FileNotFoundError() if state == "gone" else
                                  PermissionError() if state == "denied" else None)
                    fd = Path("/proc/123/fd/7")
                    with mock.patch.object(Path, "iterdir",
                                           side_effect=PermissionError() if boundary == "directory" else None,
                                           return_value=iter([fd])), \
                         mock.patch.object(Path, "read_text", return_value=fresh_stat, side_effect=read_error), \
                         mock.patch("os.readlink", return_value=directory + "/deleted.proof (deleted)",
                                    side_effect=PermissionError() if boundary == "readlink" else None), \
                         mock.patch.object(Path, "stat", side_effect=PermissionError()):
                        if should_skip:
                            self.assertEqual(_artifact_size(directory, descendants), (0, 0, 0))
                        else:
                            with self.assertRaises(PermissionError):
                                _artifact_size(directory, descendants)


if __name__ == "__main__":
    unittest.main()
