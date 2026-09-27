"""Versioned supervisor with independent raw-artifact and metadata budgets.

The frozen v1 process controls, stage runner and cleanup are reused directly.
Aggregate storage acceptance changes: raw artifacts and allowlisted
metadata/log formats each have their own sampled 64 MiB default budget. Their
sum may reach 128 MiB; this is not a new instantaneous aggregate filesystem
quota. Metadata is a finite set of root-relative worker/control filenames;
unknown names, temporary directories and every observable open deleted file
count as raw. Every observed excess remains a violation after deletion.
Metadata or captured-output exhaustion is an execution issue, not a raw-artifact
coverage loss. Concurrent violations are all retained, with metadata/output
issues taking precedence in the supervisor reason.

One CPU, 1 GiB per-process address space, the inherited 64 MiB per-file limit,
1 MiB per captured stream, and the 30-second total workflow deadline retain the
v1 defaults. Polling and exit-transition retries remain charged to that clock.
This is a cooperative research harness, not a hostile-code security sandbox.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import sys
import time

# The supervisor is launched by absolute filename under isolated Python (-I).
# Its repository-local dependency therefore must not depend on caller cwd or
# PYTHONPATH. No module is rewritten or monkeypatched to reuse the frozen code.
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research.completion_v1.resources import (
    Limits as _V1Limits, _Capture, _cleanup, _command,
    _configure, _descendants, _descriptors_closed, _drain, _reap, _register_streams, _self_proc_pid,
    _utc, run_stage,
)


@dataclass(frozen=True)
class Limits(_V1Limits):
    metadata_bytes: int = 64 * 1024 * 1024

    def validate(self):
        super().validate()
        if type(self.metadata_bytes) is not int or self.metadata_bytes <= 0:
            raise ValueError("invalid metadata_bytes")


_OBLIGATIONS = ("Reset", "Transition", "Safety", "Liveness", "Base", "Inductive",
                "Decrease", "Closure", "Consistent")
_STAGES = ("ric3", "generate", "split") + tuple(
    name + "_" + phase for name in _OBLIGATIONS for phase in ("cnf", "solve", "replay"))
METADATA_PATHS = frozenset(
    ["workflow.stdout", "workflow.stderr", "data/STAGES.jsonl"]
    + ["data/" + name + suffix
       for name in ("JOURNAL", "CONSTRUCTION", "RESULT")
       for suffix in (".json", ".json.tmp")]
    + ["data/" + name + "." + stream + ".txt"
       for name in _STAGES for stream in ("stdout", "stderr")])


def _is_raw(relative_path):
    """Classify a trial-root-relative path using the finite metadata allowlist.

    Absolute paths, arbitrary JSON/log filenames and tmp/** are raw. Atomic
    copies of the three known JSON records are metadata only while present.
    Open deleted files bypass this classifier and always count as raw.
    """
    return Path(relative_path).as_posix() not in METADATA_PATHS


def _artifact_size(root, descendants):
    total = 0
    raw = 0
    seen = set()
    root = Path(root)
    for folder, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(folder) / name
            try:
                info = path.lstat()
            except FileNotFoundError:
                continue
            if stat.S_ISDIR(info.st_mode):
                continue
            if not stat.S_ISREG(info.st_mode):
                raise ValueError(f"non-regular trial artifact: {path.relative_to(root)}")
            total += info.st_size
            if _is_raw(path.relative_to(root)):
                raw += info.st_size
            seen.add((info.st_dev, info.st_ino))
    deleted = 0
    for pid, process in descendants.items():
        try:
            entries = list(Path(f"/proc/{pid}/fd").iterdir())
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError:
            if _descriptors_closed(pid, process[1]):
                continue
            raise
        for entry in entries:
            try:
                target = os.readlink(entry)
                if not target.startswith(str(root) + os.sep):
                    continue
                info = entry.stat()
            except (FileNotFoundError, ProcessLookupError):
                continue
            except PermissionError:
                if _descriptors_closed(pid, process[1]):
                    continue
                raise
            identity = (info.st_dev, info.st_ino)
            if stat.S_ISREG(info.st_mode) and identity not in seen:
                total += info.st_size
                if target.endswith(" (deleted)"):
                    raw += info.st_size
                    deleted += info.st_size
                elif _is_raw(Path(target).relative_to(root)):
                    raw += info.st_size
                seen.add(identity)
    return total, deleted, raw


# Infrastructure failures cannot be repaired by a later final storage scan.
# Within resource observations, execution issues outrank coverage-eligible caps.
_LIMIT_PRIORITY = {"deadline": 0, "file_size_limit": 1, "artifact_limit": 2,
                   "output_limit": 3, "metadata_limit": 4}


def _limited(report, reason):
    if reason not in report["observed_violations"]:
        report["observed_violations"].append(reason)
    if report["status"] == "infrastructure_error" and report["reason"] is not None:
        return
    if report["status"] == "process_error" and report["reason"] == "descendant_leak":
        return
    previous = report["reason"] if report["status"] == "resource_limit" else None
    if previous is None or _LIMIT_PRIORITY[reason] > _LIMIT_PRIORITY[previous]:
        report.update(status="resource_limit", reason=reason)


def _observe_storage(report, limits, total, deleted, raw):
    """Record one scanner observation; test each independent cap, including ties."""
    if not 0 <= raw <= total or not 0 <= deleted <= total:
        raise ValueError("inconsistent storage observation")
    metadata = total - raw
    report.update(all_trial_files_bytes=total, raw_artifact_bytes=raw,
                  metadata_bytes=metadata)
    for key, value in (("artifact_peak_observed_bytes", total),
                       ("raw_artifact_peak_observed_bytes", raw),
                       ("metadata_peak_observed_bytes", metadata),
                       ("open_deleted_peak_observed_bytes", deleted)):
        report[key] = max(report[key], value)
    raw_excess = raw > limits.artifact_bytes
    metadata_excess = metadata > limits.metadata_bytes
    if raw_excess:
        _limited(report, "artifact_limit")
    if metadata_excess:
        _limited(report, "metadata_limit")
    return raw_excess or metadata_excess


def _supervise(config):
    limits = Limits(**config["limits"])
    limits.validate()
    start = config["start_monotonic"]
    deadline = start + limits.wall_seconds
    artifact_root = Path(config["artifact_root"])
    report = {"schema": "alc-bounded-workflow-v2", "command": config["command"],
              "cwd": config["cwd"], "artifact_root": str(artifact_root),
              "started_utc": config["started_utc"], "limits": asdict(limits),
              "status": "infrastructure_error", "reason": None, "exit_code": None,
              "artifact_policy": "independent sampled raw-artifact and metadata acceptance caps",
              "instantaneous_aggregate_quota": False,
              "observed_violations": [],
              "artifact_peak_observed_bytes": 0, "open_deleted_peak_observed_bytes": 0,
              "raw_artifact_peak_observed_bytes": 0, "metadata_peak_observed_bytes": 0,
              "max_poll_gap_seconds": 0.0}
    proc = None
    sel = None
    captures = {}
    previous_poll = None
    try:
        report["cpu"] = _configure(limits)
        for name in ("stdout", "stderr"):
            captures[name] = _Capture(limits.output_bytes, artifact_root / f"workflow.{name}")
        if _observe_storage(report, limits, *_artifact_size(artifact_root, {})):
            pass
        elif time.monotonic() >= deadline:
            _limited(report, "deadline")
        else:
            env = os.environ.copy()
            env.update(config.get("env") or {})
            temporary = artifact_root / "tmp"
            temporary.mkdir(exist_ok=True)
            env.update(TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary),
                       ALC_BOUNDED_WORKER="1")
            proc = subprocess.Popen(config["command"], cwd=config["cwd"], env=env,
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sel = _register_streams(proc)
            while True:
                now = time.monotonic()
                if previous_poll is not None:
                    report["max_poll_gap_seconds"] = max(report["max_poll_gap_seconds"], now - previous_poll)
                previous_poll = now
                descendants = _descendants(_self_proc_pid())
                storage_excess = _observe_storage(report, limits, *_artifact_size(artifact_root, descendants))
                output_excess = any(c.count > c.cap for c in captures.values())
                deadline_excess = time.monotonic() >= deadline
                if output_excess:
                    _limited(report, "output_limit")
                if deadline_excess:
                    _limited(report, "deadline")
                if storage_excess or output_excess or deadline_excess:
                    break
                exit_code = proc.poll()
                if exit_code is not None:
                    report["exit_code"] = exit_code
                    _reap()
                    live = {pid: data for pid, data in _descendants(_self_proc_pid()).items() if data[2] != "Z"}
                    if live:
                        report.update(status="process_error", reason="descendant_leak")
                        break
                    if not sel.get_map():
                        report.update(status="completed" if exit_code == 0 else "process_error",
                                      reason=None if exit_code == 0 else "worker_exit")
                        if exit_code == -signal.SIGXFSZ:
                            _limited(report, "file_size_limit")
                        break
                _drain(sel, captures, min(limits.poll_seconds, max(0, deadline - time.monotonic())))
    except (Exception, KeyboardInterrupt) as exc:
        report.update(status="infrastructure_error", reason=type(exc).__name__, error=str(exc))
    finally:
        work_end = time.monotonic()
        if previous_poll is not None:
            report["max_poll_gap_seconds"] = max(report["max_poll_gap_seconds"], work_end - previous_poll)
        if report["status"] == "completed" and work_end > deadline:
            _limited(report, "deadline")
        report["cleanup"] = _cleanup(proc)
        if not report["cleanup"]["complete"]:
            report.update(status="infrastructure_error", reason="descendant_cleanup_failed")
        if proc is not None:
            report["exit_code"] = proc.poll()
        if sel is not None:
            # Drain already-written bytes without extending the tool lifetime.
            while sel.get_map():
                _drain(sel, captures, 0)
                if sel.get_map() and not sel.select(0):
                    break
            for key in list(sel.get_map().values()):
                key.fileobj.close()
            sel.close()
        for name, capture in captures.items():
            capture.close()
            report.update(capture.fields(name))
        try:
            observed = _artifact_size(artifact_root, {})
            report["artifact_final_bytes"] = observed[0]
            _observe_storage(report, limits, *observed)
        except (OSError, ValueError) as exc:
            report.update(status="infrastructure_error", reason="artifact_scan_failed", error=str(exc))
        if any(c.count > c.cap for c in captures.values()):
            _limited(report, "output_limit")
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        own = resource.getrusage(resource.RUSAGE_SELF)
        report.update(wall_seconds=work_end - start,
                      cleanup_seconds=time.monotonic() - work_end,
                      cpu_user_seconds=usage.ru_utime + own.ru_utime,
                      cpu_system_seconds=usage.ru_stime + own.ru_stime,
                      child_cpu_user_seconds=usage.ru_utime,
                      child_cpu_system_seconds=usage.ru_stime)
    return report


def run_workflow(command, *, cwd, artifact_root, limits=Limits(), env=None):
    """Launch a fresh isolated supervisor; its report is not a SAFE verdict.

    All generated files belong below the pre-existing artifact_root. The caller
    writes this returned report after timing, so the report itself is excluded
    from measured totals. Environment entries are overrides. Trials require
    Linux and should run without unrelated CPU activity. The current/peak
    counters describe sampled bytes, not an instantaneous filesystem quota.
    """
    start = time.monotonic()
    started_utc = _utc()
    limits.validate()
    command = _command(command)
    artifact_root = Path(artifact_root).resolve(strict=True)
    if not artifact_root.is_dir():
        raise ValueError("artifact_root must be a directory")
    config = {"command": command, "cwd": str(Path(cwd).resolve(strict=True)),
              "artifact_root": str(artifact_root), "limits": asdict(limits),
              "env": env, "start_monotonic": start, "started_utc": started_utc}
    supervisor = subprocess.Popen([sys.executable, "-I", str(Path(__file__).resolve()), "--supervise"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = supervisor.communicate(json.dumps(config).encode(),
                                                timeout=limits.wall_seconds + 5)
    except subprocess.TimeoutExpired:
        supervisor.terminate()
        try:
            supervisor.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            supervisor.kill()
            supervisor.communicate()
        raise RuntimeError("resource supervisor failed to finish cleanup; trial is invalid")
    if supervisor.returncode != 0:
        raise RuntimeError(f"resource supervisor failed ({supervisor.returncode}): {stderr[:4096]!r}")
    return json.loads(stdout)


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supervise", action="store_true", required=True)
    parser.parse_args()

    def interrupted(_signum, _frame):
        raise KeyboardInterrupt("supervisor interrupted")

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    config = json.load(sys.stdin)
    json.dump(_supervise(config), sys.stdout, sort_keys=True, allow_nan=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    _main()
