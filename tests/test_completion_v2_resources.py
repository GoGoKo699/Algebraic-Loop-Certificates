"""Small process and accounting controls for the prospective storage amendment."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research.completion_v2.resources import (
    Limits, METADATA_PATHS, _artifact_size, _is_raw, _limited,
    _observe_storage, run_workflow,
)


ROOT = Path(__file__).resolve().parents[1]


def observation():
    return {"status": "completed", "reason": None, "observed_violations": [],
            "artifact_peak_observed_bytes": 0, "raw_artifact_peak_observed_bytes": 0,
            "metadata_peak_observed_bytes": 0, "open_deleted_peak_observed_bytes": 0}


class StorageAccounting(unittest.TestCase):
    def test_independent_exact_boundaries_and_priority(self):
        limits = Limits()
        cap = 64 * 1024 ** 2
        report = observation()
        self.assertFalse(_observe_storage(report, limits, cap * 2, 0, cap))
        self.assertEqual(report["metadata_bytes"], cap)
        self.assertEqual(report["status"], "completed")
        self.assertTrue(_observe_storage(report, limits, cap + 2, 0, cap + 1))
        self.assertEqual(report["reason"], "artifact_limit")
        self.assertLess(report["all_trial_files_bytes"], cap * 2)
        self.assertTrue(_observe_storage(report, limits, cap * 2 + 2, 0, cap + 1))
        _limited(report, "deadline")
        self.assertEqual(report["reason"], "metadata_limit")
        self.assertEqual(set(report["observed_violations"]),
                         {"artifact_limit", "metadata_limit", "deadline"})
        self.assertFalse(_observe_storage(report, limits, 0, 0, 0))
        self.assertEqual(report["reason"], "metadata_limit")
        self.assertEqual(report["metadata_peak_observed_bytes"], cap + 1)
        self.assertEqual(report["raw_artifact_peak_observed_bytes"], cap + 1)
        self.assertEqual(report["metadata_bytes"], 0)
        report = observation()
        _limited(report, "artifact_limit")
        _limited(report, "output_limit")
        self.assertEqual(report["reason"], "output_limit")

    def test_only_exact_known_paths_are_metadata(self):
        self.assertEqual(len(METADATA_PATHS), 69)
        for name in METADATA_PATHS:
            self.assertFalse(_is_raw(name), name)
        raw_names = ("unknown.json", "data/unknown.json", "unknown.log",
                     "data/ric3.stdout.log", "data/other.stdout.txt",
                     "tmp/JOURNAL.json", "tmp/workflow.stdout", "data/tmp/RESULT.json",
                     "data/journal.json", "data/JOURNAL.json.old", "nested/data/JOURNAL.json",
                     "/data/JOURNAL.json")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("data/JOURNAL.json", "data/JOURNAL.json.tmp", "workflow.stderr"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"m" * 10)
            for name in raw_names[:-1]:
                self.assertTrue(_is_raw(name), name)
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"r" * 11)
            self.assertTrue(_is_raw(raw_names[-1]))
            total, deleted, raw = _artifact_size(root, {})
            self.assertEqual((total - raw, deleted, raw), (30, 0, 11 * (len(raw_names) - 1)))

    def test_final_storage_scan_cannot_hide_detected_descendant_leak(self):
        report = observation()
        report.update(status="process_error", reason="descendant_leak")
        self.assertTrue(_observe_storage(report, Limits(artifact_bytes=10, metadata_bytes=10),
                                        40, 0, 20))
        self.assertEqual((report["status"], report["reason"]), ("process_error", "descendant_leak"))
        self.assertEqual(set(report["observed_violations"]), {"artifact_limit", "metadata_limit"})

    def test_limits_preserve_defaults_and_validate_metadata(self):
        limits = Limits(cpu=0)
        self.assertEqual((limits.wall_seconds, limits.address_space_bytes,
                          limits.artifact_bytes, limits.metadata_bytes, limits.output_bytes),
                         (30, 1024 ** 3, 64 * 1024 ** 2, 64 * 1024 ** 2, 1024 ** 2))
        for value in (0, -1, True, 1.5, "100"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Limits(metadata_bytes=value).validate()


@unittest.skipUnless(sys.platform == "linux", "Linux resource supervisor")
class CompletionV2Resources(unittest.TestCase):
    def trial(self, code, directory, **limits):
        return run_workflow([sys.executable, "-c", code], cwd=directory,
                            artifact_root=directory, limits=Limits(**limits),
                            env={"PYTHONPATH": str(ROOT)})

    def test_allowed_metadata_has_independent_headroom(self):
        code = "from pathlib import Path; Path('data').mkdir(); Path('proof.lrat').write_bytes(b'r'*15000); Path('data/JOURNAL.json').write_bytes(b'm'*15000)"
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory, artifact_bytes=20000, metadata_bytes=20000)
            self.assertEqual((result["schema"], result["status"]),
                             ("alc-bounded-workflow-v2", "completed"), result)
            self.assertEqual((result["raw_artifact_bytes"], result["metadata_bytes"],
                              result["all_trial_files_bytes"]), (15000, 15000, 30000))
            self.assertEqual(result["observed_violations"], [])
            self.assertFalse(result["instantaneous_aggregate_quota"])

    def test_raw_excess_is_detected_below_combined_storage_budget(self):
        code = "from pathlib import Path; import time; Path('a.lrat').write_bytes(b'r'*12000); Path('b.json').write_bytes(b'r'*12000); time.sleep(10)"
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory, artifact_bytes=20000, metadata_bytes=20000, wall_seconds=2)
            self.assertEqual((result["status"], result["reason"]), ("resource_limit", "artifact_limit"), result)
            self.assertGreater(result["raw_artifact_peak_observed_bytes"], 20000)
            self.assertLess(result["all_trial_files_bytes"], 40000)
            self.assertEqual(result["metadata_bytes"], 0)
            self.assertTrue(result["cleanup"]["complete"])

    def test_metadata_only_and_simultaneous_excess_remain_execution_issues(self):
        for raw in (False, True):
            with self.subTest(raw_excess=raw), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "data").mkdir()
                for name in ("JOURNAL.json", "STAGES.jsonl"):
                    (root / "data" / name).write_bytes(b"m" * 12000)
                if raw:
                    for name in ("a.proof", "b.proof"):
                        (root / name).write_bytes(b"r" * 12000)
                result = self.trial("raise RuntimeError('must not launch')", directory,
                                    artifact_bytes=20000, metadata_bytes=20000)
                self.assertEqual((result["status"], result["reason"]), ("resource_limit", "metadata_limit"), result)
                self.assertIsNone(result["exit_code"])
                expected = {"metadata_limit", "artifact_limit"} if raw else {"metadata_limit"}
                self.assertEqual(set(result["observed_violations"]), expected)
                self.assertEqual(result["metadata_bytes"], 24000)
                self.assertEqual(result["metadata_peak_observed_bytes"], 24000)

    def test_deleted_allowlisted_metadata_is_charged_as_raw(self):
        code = r'''
import os, pathlib, time
pathlib.Path('data').mkdir()
handles=[]
for name in ('data/JOURNAL.json', 'data/RESULT.json.tmp'):
    handle=open(name,'wb'); handle.write(b'x'*12000); handle.flush()
    os.unlink(name); handles.append(handle)
time.sleep(10)
'''
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory, artifact_bytes=20000, metadata_bytes=50000, wall_seconds=2)
            self.assertEqual(result["reason"], "artifact_limit", result)
            self.assertGreater(result["open_deleted_peak_observed_bytes"], 20000)
            self.assertGreater(result["raw_artifact_peak_observed_bytes"], 20000)
            self.assertEqual(result["raw_artifact_bytes"], 0)
            self.assertTrue(result["cleanup"]["complete"])

    def test_worker_and_native_stage_inherit_unchanged_limits(self):
        code = r'''
import json, os, pathlib, resource, sys
from research.completion_v1.resources import run_stage
pathlib.Path('data').mkdir()
child = "import os,resource,json; print(json.dumps({'affinity':sorted(os.sched_getaffinity(0)), 'as':resource.getrlimit(resource.RLIMIT_AS), 'fsize':resource.getrlimit(resource.RLIMIT_FSIZE)}))"
stage = run_stage([sys.executable, '-c', child], record_path='data/STAGES.jsonl', stdout_path='data/ric3.stdout.txt', stderr_path='data/ric3.stderr.txt')
print(json.dumps({'worker_as':resource.getrlimit(resource.RLIMIT_AS), 'stage':stage}))
'''
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial(code, directory)
            self.assertEqual(result["status"], "completed", result)
            worker = json.loads(result["stdout"])
            self.assertEqual(worker["worker_as"], [1024 ** 3] * 2)
            stage = worker["stage"]
            child = json.loads(stage["stdout"])
            self.assertEqual(child["affinity"], [result["cpu"]])
            self.assertEqual(child["as"], [1024 ** 3] * 2)
            self.assertEqual(child["fsize"], [64 * 1024 ** 2] * 2)
            self.assertEqual(result["raw_artifact_bytes"], 0)
            self.assertGreater(result["metadata_bytes"], 0)
            self.assertGreater(result["wall_seconds"], stage["wall_seconds"])

    def test_deadline_cleans_detached_descendants_and_clock_is_shared(self):
        # Setup must precede the deadline being tested, independent of host load.
        # Only this fixture's inner supervisor uses virtual elapsed time; the
        # outer production supervisor retains a real 30-second cleanup watchdog.
        stage = r'''
import json, os, pathlib, sys, time
number = sys.argv[1]
record = {'origin': os.environ['ALC_TEST_WORKFLOW_ORIGIN'],
          'budget': os.environ['ALC_TEST_WORKFLOW_BUDGET']}
ready = pathlib.Path('data/stage-' + number + '.json')
ready.with_suffix('.tmp').write_text(json.dumps(record))
ready.with_suffix('.tmp').replace(ready)
if number == '1':
    while not pathlib.Path('data/clock-ack').exists(): time.sleep(.001)
else:
    while True: time.sleep(.01)
'''
        worker = r'''
import os, pathlib, sys, time
from research.completion_v1.resources import run_stage
pathlib.Path('data').mkdir()
read_fd, write_fd = os.pipe()
pid = os.fork()
if pid == 0:
    os.close(read_fd)
    os.setsid()
    if os.fork(): os._exit(0)
    pathlib.Path('escaped.pid').write_text(str(os.getpid()))
    os.write(write_fd, b'1')
    os.close(write_fd)
    while True: time.sleep(.02)
os.close(write_fd)
if os.read(read_fd, 1) != b'1': raise RuntimeError('Detached child not ready')
os.close(read_fd)
os.waitpid(pid, 0)
''' + f"\nfor number in ('1', '2'):\n    run_stage([sys.executable, '-c', {stage!r}, number], record_path='data/STAGES.jsonl')\n"
        driver = r'''
import time
origin = time.monotonic()
import json, os, pathlib, sys, types
from dataclasses import asdict
from research.completion_v2 import resources
inner = pathlib.Path('inner').resolve()
inner.mkdir()
limits = resources.Limits()
advances = []
offset = 0
stopped_at = None
def monotonic():
    global offset, stopped_at
    if offset == 0 and (inner / 'data/stage-1.json').exists():
        offset = limits.wall_seconds / 2
        advances.append(offset)
        (inner / 'data/clock-ack').write_text('first stage charged')
    elif offset == limits.wall_seconds / 2 and (inner / 'data/stage-2.json').exists():
        offset = limits.wall_seconds
        advances.append(offset)
        stopped_at = time.monotonic() + offset
    # A reset deadline must not eventually pass merely through real-time drift.
    return stopped_at if stopped_at is not None else time.monotonic() + offset
# Replace the module reference, not the shared time module used by cleanup.
resources.time = types.SimpleNamespace(monotonic=monotonic)
''' + f"\ncommand = [sys.executable, '-c', {worker!r}]\n" + r'''
report = resources._supervise({
    'command': command, 'cwd': str(inner), 'artifact_root': str(inner),
    'limits': asdict(limits), 'start_monotonic': origin,
    'started_utc': resources._utc(),
    'env': {'ALC_TEST_WORKFLOW_ORIGIN': str(origin),
            'ALC_TEST_WORKFLOW_BUDGET': str(limits.wall_seconds)}})
print(json.dumps({'report': report, 'advances': advances, 'origin': str(origin)}))
'''
        with tempfile.TemporaryDirectory() as directory:
            watchdog = self.trial(driver, directory)
            self.assertEqual(watchdog["status"], "completed", watchdog)
            self.assertTrue(watchdog["cleanup"]["complete"], watchdog)
            fixture = json.loads(watchdog["stdout"])
            result = fixture["report"]
            budget = result["limits"]["wall_seconds"]
            self.assertEqual(fixture["advances"], [budget / 2, budget])
            self.assertEqual(result["reason"], "deadline", result)
            self.assertTrue(result["cleanup"]["complete"], result)
            self.assertGreaterEqual(result["wall_seconds"], budget)
            inner = Path(directory) / 'inner'
            for number in (1, 2):
                stage_record = json.loads((inner / f'data/stage-{number}.json').read_text())
                self.assertEqual(stage_record, {'origin': fixture['origin'], 'budget': str(budget)})
            events = [json.loads(line) for line in (inner / 'data/STAGES.jsonl').read_text().splitlines()]
            self.assertEqual([event['event'] for event in events], ['start', 'finish', 'start'])
            self.assertEqual(events[1]['exit_code'], 0)
            pid = int((inner / 'escaped.pid').read_text())
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)

    def test_launcher_ignores_caller_directory_and_pythonpath(self):
        with tempfile.TemporaryDirectory() as directory:
            script = "\n".join([
                "import json, os, sys",
                f"sys.path.insert(0, {str(ROOT)!r})",
                "from research.completion_v2.resources import run_workflow",
                "os.environ['PYTHONPATH'] = '/nonexistent/path'",
                "result = run_workflow([sys.executable, '-c', 'print(42)'], cwd=os.getcwd(), artifact_root=os.getcwd())",
                "print(json.dumps(result))",
            ])
            child = subprocess.run([sys.executable, "-I", "-c", script], cwd=directory,
                                   capture_output=True, text=True, check=True)
            result = json.loads(child.stdout)
            self.assertEqual(result["status"], "completed", result)
            self.assertEqual(result["stdout"], "42\n")

    def test_stream_cap_and_nonregular_files_still_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial("import os; os.write(1,b'x'*100000)", directory, output_bytes=1024)
            self.assertEqual(result["reason"], "output_limit", result)
            self.assertEqual((Path(directory) / "workflow.stdout").stat().st_size, 1024)
            self.assertTrue(result["stdout_truncated"])
        with tempfile.TemporaryDirectory() as directory:
            result = self.trial("import os; os.symlink('/etc/passwd','escape.proof')", directory)
            self.assertEqual(result["status"], "infrastructure_error", result)
            self.assertTrue(result["cleanup"]["complete"])


if __name__ == "__main__":
    unittest.main()
