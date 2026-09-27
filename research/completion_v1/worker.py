"""One isolated, source-bound completion-study workflow.

The supervisor, not this worker, must impose the shared total deadline, CPU
affinity, inherited address-space limit, process-tree termination and aggregate
artifact budget. Run this module in a fresh process for every trial. Its own
phase clock excludes Python startup; the supervisor's clock includes startup,
imports, all source I/O, construction and native proof checks.

Both witness routes receive the same original ASCII model. Certifaiger receives
that separately retained original, never a solver-transformed model. Acceptance
requires all nine fixed obligations to return UNSAT and successful native LRAT
replay. This is orchestration of the existing trusted translations/checkers, not
an independent proof checker. The structural route has a different output and
trust contract and is labelled separately. Unsupported hints are construction
failures. Crashes and failed proof replay are errors, never timeout evidence.

JOURNAL.json is replaced atomically before and after every phase; STAGES.jsonl
also records each command before launch. A killed worker leaves an incomplete
journal for the supervisor to classify. Bounded raw stdout/stderr prefixes and
all partial native artifacts are retained. RESULT.json exists only after the
worker finishes bookkeeping; no directory containing worker evidence is reused.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import time


OBLIGATIONS = ("Reset", "Transition", "Safety", "Liveness", "Base", "Inductive",
               "Decrease", "Closure", "Consistent")
NATIVE_TOOLS = ("certifaiger", "aigsplit", "aigtocnf", "cadical", "lrat-trim")
OUTPUT_LIMIT = 1 << 20


class StopWorkflow(Exception):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason
        super().__init__(reason)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def cpu_usage():
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + children.ru_utime, own.ru_stime + children.ru_stime


class Workflow:
    def __init__(self, args, stage_runner=None):
        self.args = args
        self.out = args.output.resolve()
        self.tools = args.tools.resolve() if args.tools is not None else None
        self.model = args.model.resolve()
        self.stage_runner = stage_runner
        self.started = time.perf_counter()
        self.record = {
            "schema": 1, "route": args.route, "status": "incomplete",
            "started_utc": utc_now(), "phases": [], "obligations": [],
            "model_source": str(self.model),
            "output_contract": ("source-aware structural decision" if args.route == "structural"
                                else "source-bound Certifaiger witness with nine LRAT checks"),
            "timing_scope": "Worker phase clock excludes startup; use supervisor total wall time.",
        }
        if args.witness is not None:
            self.record["control_witness_source"] = str(args.witness.resolve())
        if args.mutation is not None:
            self.record["control_mutation"] = args.mutation
        if args.route in ("exporter", "structural"):
            self.record["hints"] = {"width": args.width, "taps": args.taps}
            if args.route == "exporter":
                self.record["hints"]["odd_multiple"] = args.odd_multiple

    def save(self):
        self.record["worker_wall_seconds"] = time.perf_counter() - self.started
        atomic_json(self.out / "JOURNAL.json", self.record)

    def phase(self, name, function, argv=None):
        start, cpu_start = time.perf_counter(), cpu_usage()
        row = {"name": name, "status": "running", "started_utc": utc_now(),
               "start_offset_seconds": start - self.started}
        if argv is not None:
            row["argv"] = [str(item) for item in argv]
        self.record["phases"].append(row)
        self.record["active_phase"] = name
        self.save()
        try:
            result = function()
            row["status"] = "completed"
            return result
        except BaseException as error:
            row["status"] = "failed"
            row["exception"] = type(error).__name__
            raise
        finally:
            cpu_end = cpu_usage()
            row["wall_seconds"] = time.perf_counter() - start
            row["cpu_user_seconds"] = cpu_end[0] - cpu_start[0]
            row["cpu_system_seconds"] = cpu_end[1] - cpu_start[1]
            self.record.pop("active_phase", None)
            self.save()

    def command(self, name, argv):
        command = [str(item) for item in argv]

        def invoke():
            if self.stage_runner is None:
                from research.completion_v1.resources import run_stage
                runner = run_stage
            else:
                runner = self.stage_runner
            result = runner(command, cwd=self.out,
                            record_path=self.out / "STAGES.jsonl",
                            stdout_path=self.out / (name + ".stdout.txt"),
                            stderr_path=self.out / (name + ".stderr.txt"),
                            output_limit_bytes=OUTPUT_LIMIT)
            # The raw bounded prefixes live in files; avoid duplicating them in
            # every growing journal snapshot.
            self.record["phases"][-1]["process"] = {
                key: value for key, value in result.items() if key not in ("stdout", "stderr")}
            if result["status"] == "launch_error":
                raise StopWorkflow("blocked", "Could not launch " + name)
            if result["status"] == "output_limit":
                raise StopWorkflow("unknown", "bounded command output limit: " + name)
            if result["status"] != "completed":
                raise StopWorkflow("error", "Unexpected command status: " + name)
            if result.get("resource_signal") == "file_size_limit":
                self.record["resource_cause"] = "file_size_limit"
                raise StopWorkflow("unknown", "Native process hit the inherited file-size limit: " + name)
            if result["exit_code"] is None or result["exit_code"] < 0:
                raise StopWorkflow("error", "Native process terminated unexpectedly: " + name)
            return result

        return self.phase(name, invoke, command)

    def require_exit(self, name, argv, expected=0, failure_status="blocked"):
        result = self.command(name, argv)
        if result["exit_code"] != expected:
            raise StopWorkflow(failure_status, "Unexpected exit code at " + name)
        return result

    def preflight(self):
        if not self.model.is_file():
            raise StopWorkflow("blocked", "Original model file is missing")
        if self.args.route != "structural":
            names = NATIVE_TOOLS + (("ric3",) if self.args.route == "ric3" else ())
            if self.tools is None or any(not (self.tools / name).is_file() or
                                         not os.access(self.tools / name, os.X_OK) for name in names):
                raise StopWorkflow("blocked", "A required native executable is missing")
        if self.args.route in ("exporter", "structural"):
            if self.args.width is None or self.args.taps is None:
                raise StopWorkflow("unsupported", "Explicit width and taps are required")
        if self.args.route == "exporter" and self.args.odd_multiple is None:
            raise StopWorkflow("unsupported", "Explicit odd multiple is required")
        if self.args.mutation is not None and self.args.route != "exporter":
            raise StopWorkflow("unsupported", "Mutation is only supported for exporter controls")
        if self.args.route == "witness-control" and (self.args.witness is None or
                                                      not self.args.witness.is_file()):
            raise StopWorkflow("blocked", "Control witness is missing")

    def copy_source(self):
        shutil.copyfile(self.model, self.out / "model.aag")
        # The frozen published source family is below the checker's 100 kB
        # boundary. Bound this read even if a caller supplies the wrong file.
        with (self.out / "model.aag").open("rb") as stream:
            raw = stream.read(100_001)
        if len(raw) > 100_000:
            raise StopWorkflow("blocked", "Model exceeds the fixed source-family size limit")
        self.record["model_sha256"] = hashlib.sha256(raw).hexdigest()
        self.record["model_bytes"] = len(raw)
        return raw

    def construct(self, raw):
        from research.aiger_lfsr_v1.check import Rejected, parse
        from research.odd_order_witness_v1.produce import Unsupported, produce
        try:
            if parse(raw).n != self.args.width:
                raise StopWorkflow("unsupported", "Width hint does not match the original source")
            witness, metadata = produce(raw, self.args.taps, self.args.odd_multiple,
                                        mutation=self.args.mutation)
        except (Rejected, Unsupported) as error:
            raise StopWorkflow("unsupported", str(error)) from error
        with (self.out / "witness.aag").open("xb") as stream:
            stream.write(witness)
        atomic_json(self.out / "CONSTRUCTION.json", metadata)
        self.record["construction"] = metadata

    def structural(self, raw):
        from research.aiger_lfsr_v1.check import Rejected, parse, replay
        from research.aiger_lfsr_v1.source_aware import odd_order
        try:
            model = parse(raw)
            if model.n != self.args.width:
                raise StopWorkflow("unsupported", "Width hint does not match the original source")
            replay(model, self.args.taps)
            if not odd_order(model.n, self.args.taps):
                raise StopWorkflow("unsupported", "Direct squarefree odd-order condition does not hold")
        except (Rejected, ValueError) as error:
            raise StopWorkflow("unsupported", str(error)) from error

    def native_checks(self):
        tool = lambda name: self.tools / name
        self.require_exit("generate", [tool("certifaiger"), "model.aag", "witness.aag", "check.aig"])
        self.require_exit("split", [tool("aigsplit"), "-n", "check.aig", "obligation_"])
        if not all((self.out / (name + ".aig")).is_file() for name in OBLIGATIONS):
            raise StopWorkflow("blocked", "Expected set of nine native obligations is absent")
        for name in OBLIGATIONS:
            obligation = {"name": name, "status": "incomplete"}
            self.record["obligations"].append(obligation)
            self.require_exit(name + "_cnf", [tool("aigtocnf"), name + ".aig", name + ".cnf"])
            result = self.command(name + "_solve", [tool("cadical"), "--quiet", "--unsat", "--lrat",
                                                    "--no-binary", "--no-factor", name + ".cnf", name + ".lrat"])
            if result["exit_code"] == 10:
                obligation["status"] = "sat"
                raise StopWorkflow("rejected", "SAT counterexample to " + name)
            if result["exit_code"] != 20:
                raise StopWorkflow("error", "UNSAT not established for " + name)
            self.require_exit(name + "_replay", [tool("lrat-trim"), name + ".cnf", name + ".lrat"],
                              expected=20, failure_status="error")
            obligation["status"] = "unsat_replayed"
            self.save()

    def witness_metadata(self):
        witness = self.out / "witness.aag"
        digest = hashlib.sha256()
        with witness.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1 << 16), b""):
                digest.update(chunk)
        self.record["witness_sha256"] = digest.hexdigest()
        self.record["witness_bytes"] = witness.stat().st_size

    def execute(self):
        self.out.mkdir(parents=True, exist_ok=True)
        # A supervisor may pre-create the empty working directory. It may not
        # reuse a directory containing evidence from any earlier invocation.
        if any(self.out.iterdir()):
            raise ValueError("Refusing to overwrite a nonempty worker output directory")
        self.save()
        try:
            self.phase("preflight", self.preflight)
            raw = self.phase("read_original", self.copy_source)
            if self.args.route == "structural":
                self.phase("structural_decision", lambda: self.structural(raw))
                self.record["status"] = "structural_accepted"
            else:
                if self.args.route == "exporter":
                    self.phase("construct", lambda: self.construct(raw))
                elif self.args.route == "witness-control":
                    self.phase("copy_control", lambda: shutil.copyfile(
                        self.args.witness, self.out / "witness.aag"))
                else:
                    result = self.require_exit("ric3", [self.tools / "ric3", "check", "model.aag",
                                                        "--cert", "witness.aag", "--ui", "false", "ic3",
                                                        "--rseed", "0"],
                                               failure_status="error")
                    verdicts = [line.strip() for line in result["stdout"].splitlines()
                                if line.strip() in ("UNSAT", "SAT", "UNKNOWN")]
                    if verdicts == ["UNKNOWN"]:
                        raise StopWorkflow("unknown", "rIC3 reported UNKNOWN without an observed resource cause")
                    if verdicts == ["SAT"]:
                        raise StopWorkflow("error", "rIC3 reported SAT on the designated safety case")
                    if verdicts != ["UNSAT"]:
                        raise StopWorkflow("blocked", "Missing or ambiguous rIC3 result line")
                if not (self.out / "witness.aag").is_file():
                    raise StopWorkflow("blocked", "Witness-producing route did not create a witness")
                self.phase("witness_metadata", self.witness_metadata)
                self.native_checks()
                self.record["status"] = "accepted"
        except StopWorkflow as error:
            self.record.update(status=error.status, reason=error.reason)
        except MemoryError:
            self.record.update(status="unknown", reason="Python MemoryError; allocation-failure cause is not attributed")
        except Exception as error:
            self.record.update(status="error", reason=type(error).__name__ + ": " + str(error))
        self.record["finished_utc"] = utc_now()
        self.save()
        atomic_json(self.out / "RESULT.json", self.record)
        return self.record


def argument_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route", required=True, choices=("exporter", "ric3", "structural", "witness-control"))
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--tools", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--taps", type=lambda text: int(text, 0))
    parser.add_argument("--odd-multiple", type=lambda text: int(text, 0))
    parser.add_argument("--witness", type=Path)
    parser.add_argument("--mutation", choices=("global_bound", "skip_repeated3"))
    return parser


def main():
    result = Workflow(argument_parser().parse_args()).execute()
    print(json.dumps({"status": result["status"], "reason": result.get("reason")}), flush=True)


if __name__ == "__main__":
    main()
