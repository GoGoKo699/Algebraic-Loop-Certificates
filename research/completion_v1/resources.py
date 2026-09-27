"""Linux resource supervisor for the bounded certificate experiment.

Contract
--------
``run_workflow`` launches a *fresh* Python supervisor and the supplied worker.
The worker must read the original source only after launch and keep every
generated file (including temporary files) beneath ``artifact_root``. The
supervisor and worker inherit one-CPU affinity, a hard per-process address-space
limit, and a hard per-file size limit. These are not aggregate RAM limits.
The monotonic deadline starts on entry to ``run_workflow``, before source reads,
and covers the worker, its orchestration, and all native stages. Setup/builds
belong outside this call. Only a zero worker exit with no detected violation
gets ``status='completed'``; this is NOT a scientific certificate verdict.

The supervisor is a Linux child subreaper. It finds descendants through /proc,
so a native tool's ``setsid`` does not escape cleanup. It kills and reaps them
on timeout, detected violation, worker exit, and ordinary supervisor exceptions.
An fd-access permission denial is ignored only after a fresh /proc stat check
confirms the same process has exited or vanished; live denials fail closed.
This is a non-hostile research harness, not a security sandbox: programs must
not deliberately change affinity, alter limits, or write outside the trial.

Storage is a conservative ACCEPTANCE CAP, not an instantaneous filesystem quota.
All regular trial files, including metadata and bounded raw logs, count. Open
deleted trial files count when visible through descendant /proc fd entries.
Every observed excess invalidates the run permanently, even after deletion.
Inherited RLIMIT_FSIZE limits each individual file; a sampled aggregate monitor
and final scan enforce the aggregate acceptance cap. A short-lived aggregate
peak between samples can be missed and overshoot has no guaranteed byte bound.
Reports expose the sampling interval and largest observed gap. Do not describe
this as a hard aggregate disk quota. Symlinks and special files are rejected.

``run_stage`` is for the supervised worker: it records the command before
launch, bounds each captured stream, optionally retains exact raw prefixes,
and records process exit and elapsed/child CPU observations. It has no fresh
per-stage timeout; the enclosing workflow deadline remains authoritative.
An output-limit result must stop the worker. Unexpected native exits and
allocation failures are NOT automatically classified as memory exhaustion.
"""

from __future__ import annotations

import argparse
import ctypes
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import resource
import selectors
import signal
import stat
import subprocess
import sys
import time


@dataclass(frozen=True)
class Limits:
    wall_seconds: float = 30.0
    address_space_bytes: int = 1024 * 1024 * 1024
    artifact_bytes: int = 64 * 1024 * 1024
    output_bytes: int = 1024 * 1024
    poll_seconds: float = 0.01
    cpu: int | None = None

    def validate(self):
        for name in ("wall_seconds", "poll_seconds"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"invalid {name}")
        for name in ("address_space_bytes", "artifact_bytes", "output_bytes"):
            value = getattr(self, name)
            if type(value) is not int or value <= 0:
                raise ValueError(f"invalid {name}")
        if self.output_bytes > 8 * 1024 * 1024:
            raise ValueError("output capture exceeds harness control-plane bound")
        if self.cpu is not None and (type(self.cpu) is not int or self.cpu < 0):
            raise ValueError("invalid CPU")


def _command(command):
    if not isinstance(command, (list, tuple)) or not command or any(not isinstance(x, str) or not x or "\0" in x for x in command):
        raise ValueError("command must be a nonempty sequence of nonempty strings")
    return list(command)


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _append(path, record):
    if path is not None:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()


class _Capture:
    def __init__(self, cap, path=None):
        self.cap = cap
        self.count = 0
        self.data = bytearray()
        self.path = str(Path(path).resolve()) if path is not None else None
        self.handle = open(path, "xb") if path is not None else None

    def feed(self, data):
        self.count += len(data)
        keep = data[:max(0, self.cap - len(self.data))]
        self.data.extend(keep)
        if self.handle is not None:
            self.handle.write(keep)
            self.handle.flush()

    def close(self):
        if self.handle is not None:
            self.handle.close()

    def fields(self, name):
        return {name: self.data.decode("utf-8", errors="replace"),
                name + "_bytes": self.count,
                name + "_truncated": self.count > self.cap,
                name + "_path": self.path}


def _register_streams(proc):
    sel = selectors.DefaultSelector()
    for name in ("stdout", "stderr"):
        stream = getattr(proc, name)
        os.set_blocking(stream.fileno(), False)
        sel.register(stream, selectors.EVENT_READ, name)
    return sel


def _drain(sel, captures, timeout):
    for key, _ in sel.select(max(0, timeout)):
        try:
            data = os.read(key.fd, 65536)
        except BlockingIOError:
            continue
        if data:
            captures[key.data].feed(data)
        else:
            sel.unregister(key.fileobj)
            key.fileobj.close()


def run_stage(command, *, cwd=None, env=None, record_path=None,
              output_limit_bytes=1024 * 1024, stdout_path=None, stderr_path=None):
    """Run one stage INSIDE the supervised worker; inspect exit_code separately.

    CPU fields are deltas of RUSAGE_CHILDREN, so the worker must run stages
    sequentially and must not concurrently reap unrelated children. They include
    descendant CPU only when wait accounting propagates it to the stage parent.
    The supervisor additionally reports CPU for the whole reaped process tree.
    """
    command = _command(command)
    if type(output_limit_bytes) is not int or not 0 < output_limit_bytes <= 8 * 1024 * 1024:
        raise ValueError("invalid output capture bound")
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    record = {"command": command, "cwd": str(Path(cwd or os.getcwd()).resolve()),
              "started_utc": _utc()}
    _append(record_path, {"event": "start", **record})
    captures = {}
    proc = None
    sel = None
    try:
        captures["stdout"] = _Capture(output_limit_bytes, stdout_path)
        captures["stderr"] = _Capture(output_limit_bytes, stderr_path)
        try:
            proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            record.update(status="launch_error", exit_code=None, error=str(exc))
        else:
            sel = _register_streams(proc)
            overflow = False
            while sel.get_map() or proc.poll() is None:
                _drain(sel, captures, 0.01)
                if any(c.count > c.cap for c in captures.values()):
                    overflow = True
                    proc.kill()
                    # A grandchild may still hold a pipe open. The workflow
                    # supervisor owns its cleanup; do not hang this worker.
                    break
            record.update(status="output_limit" if overflow else "completed",
                          exit_code=proc.wait())
            record["resource_signal"] = ("file_size_limit"
                                         if record["exit_code"] == -signal.SIGXFSZ else None)
    finally:
        if sel is not None:
            for key in list(sel.get_map().values()):
                key.fileobj.close()
            sel.close()
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        for capture in captures.values():
            capture.close()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    record.update(wall_seconds=time.monotonic() - start,
                  cpu_user_seconds=after.ru_utime - before.ru_utime,
                  cpu_system_seconds=after.ru_stime - before.ru_stime)
    for name, capture in captures.items():
        record.update(capture.fields(name))
    _append(record_path, {"event": "finish", **record})
    return record


def _processes():
    result = {}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            fields = (entry / "stat").read_text().rsplit(")", 1)[1].split()
            result[int(entry.name)] = (int(fields[1]), int(fields[19]), fields[0])
        except (FileNotFoundError, ProcessLookupError):
            pass
    return result


def _descendants(root):
    processes = _processes()
    found = {}
    parents = {root}
    while parents:
        children = {pid for pid, info in processes.items() if info[0] in parents and pid not in found}
        found.update({pid: processes[pid] for pid in children})
        parents = children
    return found


def _self_proc_pid():
    # Some containers mount a parent namespace's /proc. Its identifiers differ
    # from getpid()/waitpid()/kill() in our namespace.
    return int(Path("/proc/self/stat").read_text().split(" ", 1)[0])


def _namespace_pids(proc_pid):
    for line in Path(f"/proc/{proc_pid}/status").read_text().splitlines():
        if line.startswith("NSpid:"):
            return [int(x) for x in line.split()[1:]]
    raise RuntimeError("/proc does not expose the NSpid mapping")


def _kill(descendants):
    namespace_depth = len(_namespace_pids("self")) - 1
    for pid, original in descendants.items():
        try:
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            if int(fields[19]) == original[1]:
                namespace_pids = _namespace_pids(pid)
                if len(namespace_pids) <= namespace_depth:
                    raise RuntimeError("descendant is outside supervisor PID namespace")
                os.kill(namespace_pids[namespace_depth], signal.SIGKILL)
        except (FileNotFoundError, ProcessLookupError):
            pass


def _reap():
    while True:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            return
        if pid == 0:
            return


def _cleanup(proc):
    """Kill before waiting; repeat to catch children reparented to subreaper."""
    deadline = time.monotonic() + 2.0
    killed = set()
    while True:
        descendants = _descendants(_self_proc_pid())
        killed.update(pid for pid, data in descendants.items() if data[2] != "Z")
        _kill(descendants)
        # Let Popen collect its own exit status before reaping orphan children.
        if proc is not None:
            try:
                proc.wait(timeout=0.05)
            except subprocess.TimeoutExpired:
                pass
        if proc is None or proc.returncode is not None:
            _reap()
        remaining = _descendants(_self_proc_pid())
        if not remaining:
            return {"complete": True, "terminated_pids": sorted(killed)}
        if time.monotonic() >= deadline:
            return {"complete": False, "terminated_pids": sorted(killed),
                    "remaining_pids": sorted(remaining)}
        time.sleep(0.002)


def _is_raw(path):
    """Unknown extensions count as raw; known control/log formats are separate.

    This classifier cannot weaken the all-files acceptance cap. It only prevents
    metadata/log excess from being reported as a raw-artifact performance loss.
    """
    name = Path(path).name.lower()
    return (Path(name).suffix not in {".json", ".jsonl", ".log", ".stdout", ".stderr"}
            and not name.endswith((".stdout.txt", ".stderr.txt", ".json.tmp")))


def _descriptors_closed(pid, expected_starttime):
    """Confirm an fd-permission race is caused by process exit, not a live denial.

    Linux can deny an unprivileged owner access to /proc/PID/fd after the task
    exits but before it is reaped. A fresh stat read must identify the same
    process in zombie/dead state; a reused PID or inaccessible live task must
    still fail closed. A vanished process also has no remaining descriptors.
    """
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    except (FileNotFoundError, ProcessLookupError):
        return True
    return int(fields[19]) == expected_starttime and fields[0] in {"Z", "X", "x"}


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
            if _is_raw(path):
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
                if _is_raw(target.removesuffix(" (deleted)")):
                    raw += info.st_size
                deleted += info.st_size
                seen.add(identity)
    return total, deleted, raw


def _configure(limits):
    if sys.platform != "linux":
        raise RuntimeError("the resource supervisor requires Linux /proc and prctl")
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), "PR_SET_CHILD_SUBREAPER failed")
    permitted = os.sched_getaffinity(0)
    cpu = min(permitted) if limits.cpu is None else limits.cpu
    if cpu not in permitted:
        raise ValueError("requested CPU is outside the inherited affinity set")
    os.sched_setaffinity(0, {cpu})
    resource.setrlimit(resource.RLIMIT_AS, (limits.address_space_bytes,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits.artifact_bytes,) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    return cpu


def _supervise(config):
    limits = Limits(**config["limits"])
    limits.validate()
    start = config["start_monotonic"]
    deadline = start + limits.wall_seconds
    artifact_root = Path(config["artifact_root"])
    report = {"schema": "alc-bounded-workflow-v1", "command": config["command"],
              "cwd": config["cwd"], "artifact_root": str(artifact_root),
              "started_utc": config["started_utc"], "limits": asdict(limits),
              "status": "infrastructure_error", "reason": None, "exit_code": None,
              "artifact_policy": "sampled acceptance cap; all regular trial files",
              "instantaneous_aggregate_quota": False,
              "observed_violations": [],
              "artifact_peak_observed_bytes": 0, "open_deleted_peak_observed_bytes": 0,
              "raw_artifact_peak_observed_bytes": 0,
              "max_poll_gap_seconds": 0.0}
    proc = None
    sel = None
    captures = {}
    previous_poll = None
    work_end = None
    def limited(reason):
        if reason not in report["observed_violations"]:
            report["observed_violations"].append(reason)
        if report["status"] != "resource_limit":
            report.update(status="resource_limit", reason=reason)
    try:
        report["cpu"] = _configure(limits)
        for name in ("stdout", "stderr"):
            captures[name] = _Capture(limits.output_bytes, artifact_root / f"workflow.{name}")
        total, _, raw = _artifact_size(artifact_root, {})
        report["artifact_peak_observed_bytes"] = total
        report["raw_artifact_peak_observed_bytes"] = raw
        if total > limits.artifact_bytes:
            limited("artifact_limit" if raw > limits.artifact_bytes else "trial_storage_limit")
        elif time.monotonic() >= deadline:
            limited("deadline")
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
                total, deleted, raw = _artifact_size(artifact_root, descendants)
                report["artifact_peak_observed_bytes"] = max(report["artifact_peak_observed_bytes"], total)
                report["raw_artifact_peak_observed_bytes"] = max(report["raw_artifact_peak_observed_bytes"], raw)
                report["open_deleted_peak_observed_bytes"] = max(report["open_deleted_peak_observed_bytes"], deleted)
                if total > limits.artifact_bytes:
                    limited("artifact_limit" if raw > limits.artifact_bytes else "trial_storage_limit")
                    break
                if any(c.count > c.cap for c in captures.values()):
                    limited("output_limit")
                    break
                if time.monotonic() >= deadline:
                    limited("deadline")
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
                            limited("file_size_limit")
                        break
                _drain(sel, captures, min(limits.poll_seconds, max(0, deadline - time.monotonic())))
    except (Exception, KeyboardInterrupt) as exc:
        report.update(status="infrastructure_error", reason=type(exc).__name__, error=str(exc))
    finally:
        work_end = time.monotonic()
        if report["status"] == "completed" and work_end > deadline:
            limited("deadline")
        report["cleanup"] = _cleanup(proc)
        if not report["cleanup"]["complete"]:
            report.update(status="infrastructure_error", reason="descendant_cleanup_failed")
        if proc is not None:
            report["exit_code"] = proc.poll()
        if sel is not None:
            # Retain already-written pipe data without extending tool lifetime.
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
            total, _, raw = _artifact_size(artifact_root, {})
            report["artifact_final_bytes"] = total
            report["all_trial_files_bytes"] = total
            report["raw_artifact_bytes"] = raw
            report["artifact_peak_observed_bytes"] = max(report["artifact_peak_observed_bytes"], total)
            report["raw_artifact_peak_observed_bytes"] = max(report["raw_artifact_peak_observed_bytes"], raw)
            if total > limits.artifact_bytes and report["status"] != "infrastructure_error":
                limited("artifact_limit" if report["raw_artifact_peak_observed_bytes"] > limits.artifact_bytes else "trial_storage_limit")
        except (OSError, ValueError) as exc:
            report.update(status="infrastructure_error", reason="artifact_scan_failed", error=str(exc))
        if any(c.count > c.cap for c in captures.values()) and report["status"] != "infrastructure_error":
            limited("output_limit")
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
    """Return a JSON-ready supervisor report; never interpret it as SAFE.

    ``artifact_root`` must already exist and must not contain workflow.stdout or
    workflow.stderr. The caller writes the returned final report after timing;
    its bytes are consequently excluded from measured trial artifact totals.
    ``env`` contains overrides, not a replacement environment. The trial should
    be run without unrelated CPU activity; fresh processes do not imply cold
    filesystem caches. Linux is mandatory; unsupported platforms fail closed.
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
    # Ordinary termination requests still run the descendant cleanup finally.
    def interrupted(_signum, _frame):
        raise KeyboardInterrupt("supervisor interrupted")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    config = json.load(sys.stdin)
    json.dump(_supervise(config), sys.stdout, sort_keys=True, allow_nan=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    _main()
