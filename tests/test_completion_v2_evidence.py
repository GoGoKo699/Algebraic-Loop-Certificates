"""Independent replay and counterfeit checks for the frozen comparison."""
import copy
import json
import unittest

from research.completion_v2.verify_study import (
    DEFAULT_STUDY, HERE, decode_json, digest, is_raw, stage_journal, study_directory, summaries, trial_reader,
    validate_trial, verify_study,
)


class CompletionV2BudgetEvidence(unittest.TestCase):
    """Small synthetic observations test policy, not benchmark outcomes."""

    def synthetic_stop(self, *, raw_peak=0, metadata_peak=0, reason="deadline", violations=None):
        row = {"id": "n02-t1-exporter", "width": 2, "trial": 1, "route": "exporter"}
        case = {"model": "models/original.aag", "width": 2, "taps": 3, "odd_multiple": 3}
        limits = {"wall_seconds": 30.0, "address_space_bytes": 1 << 30, "artifact_bytes": 64 << 20,
                  "metadata_bytes": 64 << 20, "output_bytes": 1 << 20, "poll_seconds": 0.01, "cpu": 0}
        freeze = {"limits": limits, "python": {"executable": "/python"}}
        supervisor = {
            "schema": "alc-bounded-workflow-v2", "limits": limits, "cpu": 0,
            "artifact_policy": "independent sampled raw-artifact and metadata acceptance caps",
            "instantaneous_aggregate_quota": False, "artifact_root": "/study/n02-t1-exporter",
            "cwd": "/repository", "command": ["/python", "-m", "research.completion_v1.worker",
                "--route", "exporter", "--model", "/repository/models/original.aag", "--tools", "/tools",
                "--output", "/study/n02-t1-exporter/data", "--width", "2", "--taps", "0x3", "--odd-multiple", "3"],
            "wall_seconds": 30.01, "cleanup_seconds": 0.01, "cpu_user_seconds": 0,
            "cpu_system_seconds": 0, "child_cpu_user_seconds": 0, "child_cpu_system_seconds": 0,
            "max_poll_gap_seconds": 0.01, "all_trial_files_bytes": 0, "artifact_final_bytes": 0,
            "raw_artifact_bytes": 0, "metadata_bytes": 0,
            "artifact_peak_observed_bytes": raw_peak + metadata_peak,
            "raw_artifact_peak_observed_bytes": raw_peak, "metadata_peak_observed_bytes": metadata_peak,
            "open_deleted_peak_observed_bytes": raw_peak,
            "stdout": "", "stdout_bytes": 0, "stdout_truncated": False,
            "stderr": "", "stderr_bytes": 0, "stderr_truncated": False,
            "cleanup": {"complete": True}, "status": "resource_limit", "reason": reason,
            "exit_code": -9, "observed_violations": [reason] if violations is None else violations,
        }
        raw = {"SUPERVISOR.json": json.dumps(supervisor).encode(), "workflow.stdout": b"", "workflow.stderr": b""}
        inventory = {name: {"raw_bytes": len(value)} for name, value in raw.items()}
        return validate_trial(row, case, freeze, inventory, raw.__getitem__)

    def test_metadata_excess_overrides_time_and_raw_stops(self):
        for reason, violations in (("metadata_limit", ["metadata_limit"]),
                                   ("metadata_limit", ["deadline", "artifact_limit", "metadata_limit"]),
                                   ("deadline", ["deadline"]),
                                   ("artifact_limit", ["artifact_limit"])):
            with self.subTest(reason=reason, violations=violations):
                result = self.synthetic_stop(raw_peak=(64 << 20) + 1, metadata_peak=(64 << 20) + 1,
                                             reason=reason, violations=violations)
                self.assertEqual(result["status"], "execution_issue")
                self.assertIsNone(result["resource_reason"])

    def test_raw_excess_remains_unknown_with_metadata_below_own_cap(self):
        result = self.synthetic_stop(raw_peak=(64 << 20) + 1, metadata_peak=63 << 20, reason="artifact_limit")
        self.assertEqual(result["status"], "resource_unknown")
        self.assertEqual(result["resource_reason"], "artifact_limit")

    def test_unknown_metadata_like_names_remain_raw(self):
        for name in ("data/unknown.json", "data/unknown.log", "tmp/JOURNAL.json", "data/journal.json",
                     "/data/JOURNAL.json", "data/ric3.stdout.txt.backup"):
            self.assertTrue(is_raw(name), name)
        for name in ("data/JOURNAL.json", "data/JOURNAL.json.tmp", "data/ric3.stdout.txt", "workflow.stdout"):
            self.assertFalse(is_raw(name), name)


class CompletionV2StudyEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = decode_json((HERE / "PROTOCOL_FREEZE.json").read_bytes())
        cls.row = cls.freeze["order"][0]
        cls.case = cls.freeze["cases"][0]
        cls.open_study = study_directory()
        cls.base = cls.open_study.__enter__()
        cls.inventory, read = trial_reader(cls.base / cls.row["id"])
        cls.read = staticmethod(read)

    @classmethod
    def tearDownClass(cls):
        cls.open_study.__exit__(None, None, None)

    def changed(self, record_change=None, supervisor_change=None, replacements=None):
        record = decode_json(self.read("data/RESULT.json"))
        supervisor = decode_json(self.read("SUPERVISOR.json"))
        if record_change:
            record_change(record)
        if supervisor_change:
            supervisor_change(supervisor)
        values = {
            "data/RESULT.json": json.dumps(record).encode(),
            "data/JOURNAL.json": json.dumps(record).encode(),
            "SUPERVISOR.json": json.dumps(supervisor).encode(),
            "workflow.stdout": json.dumps({"status": record["status"], "reason": record.get("reason")}).encode() + b"\n",
        }
        values.update(replacements or {})
        # These semantic tests bypass outer hashes deliberately. Keep all byte
        # accounting coherent so a counterfeit reaches the intended rule.
        inventory = copy.deepcopy(self.inventory)
        for name, raw in values.items():
            inventory[name]["raw_bytes"] = len(raw)
        supervisor["all_trial_files_bytes"] = sum(v["raw_bytes"] for k, v in inventory.items() if k != "SUPERVISOR.json")
        supervisor["artifact_final_bytes"] = supervisor["all_trial_files_bytes"]
        supervisor["artifact_peak_observed_bytes"] = max(supervisor["artifact_peak_observed_bytes"], supervisor["artifact_final_bytes"])
        supervisor["raw_artifact_bytes"] = sum(v["raw_bytes"] for k, v in inventory.items() if k != "SUPERVISOR.json" and is_raw(k))
        supervisor["raw_artifact_peak_observed_bytes"] = max(supervisor["raw_artifact_peak_observed_bytes"], supervisor["raw_artifact_bytes"])
        supervisor["metadata_bytes"] = supervisor["all_trial_files_bytes"] - supervisor["raw_artifact_bytes"]
        supervisor["metadata_peak_observed_bytes"] = max(supervisor["metadata_peak_observed_bytes"], supervisor["metadata_bytes"])
        supervisor["artifact_peak_observed_bytes"] = max(supervisor["artifact_peak_observed_bytes"], supervisor["raw_artifact_peak_observed_bytes"], supervisor["metadata_peak_observed_bytes"])
        supervisor["stdout"] = values["workflow.stdout"].decode()
        supervisor["stdout_bytes"] = len(values["workflow.stdout"])
        values["SUPERVISOR.json"] = json.dumps(supervisor).encode()
        return validate_trial(self.row, self.case, self.freeze, inventory,
                              lambda name: values[name] if name in values else self.read(name))

    def test_committed_study_replays_without_native_tools(self):
        result = verify_study(self.base)
        self.assertEqual(result, decode_json((HERE / "STUDY_REPORT.json").read_bytes()))
        self.assertEqual(result["planned_trials"], 54)
        self.assertEqual(result["observed_trials"], 54)
        self.assertEqual(len(result["trials"]), 54)
        self.assertEqual(result["proofs_replayed"], 180)
        self.assertEqual(result["sat_assignments_checked"], 0)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["primary_outcome"], "added_coverage")
        self.assertEqual(result["exporter_exclusive_widths"], [8])
        self.assertEqual(result["ric3_exclusive_widths"], [])
        self.assertFalse(result["structural_reference_is_witness_coverage"])

    def test_missing_obligation_phase_or_source_binding_rejects(self):
        mutations = (
            lambda record: record["obligations"].pop(),
            lambda record: record["phases"].pop(),
            lambda record: record.update(model_sha256="0" * 64),
            lambda record: record.update(witness_sha256="0" * 64),
            lambda record: record["hints"].update(odd_multiple=9),
            lambda record: record["phases"][4].pop("process"),
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                self.changed(record_change=mutation)

    def test_invalid_completed_proof_rejects(self):
        with self.assertRaises(ValueError):
            self.changed(replacements={"data/Reset.lrat": b""})

    def test_setup_failure_cannot_hide_behind_later_deadline(self):
        checked = self.changed(
            record_change=lambda record: record.update(status="unsupported", reason="Invalid structural hints"),
            supervisor_change=lambda supervisor: supervisor.update(
                status="resource_limit", reason="deadline", wall_seconds=30.01,
                observed_violations=["deadline"], exit_code=-9))
        self.assertEqual(checked["status"], "execution_issue")
        self.assertIn("worker unsupported", checked["conflicts"])

    def test_deadline_between_result_and_stdout_stays_unknown(self):
        checked = self.changed(
            supervisor_change=lambda supervisor: supervisor.update(
                status="resource_limit", reason="deadline", wall_seconds=30.01,
                observed_violations=["deadline"], exit_code=-9),
            replacements={"workflow.stdout": b""})
        self.assertEqual(checked["status"], "resource_unknown")
        self.assertEqual(len(checked["proofs_replayed"]), 9)

    def test_unobserved_raw_excess_does_not_establish_artifact_limit(self):
        with self.assertRaises(ValueError):
            self.changed(supervisor_change=lambda supervisor: supervisor.update(
                status="resource_limit", reason="artifact_limit", observed_violations=["artifact_limit"], exit_code=-9))

    def test_changed_policy_and_unfinished_cleanup_do_not_accept(self):
        with self.assertRaises(ValueError):
            self.changed(supervisor_change=lambda supervisor: supervisor["limits"].update(wall_seconds=60))
        checked = self.changed(supervisor_change=lambda supervisor: supervisor["cleanup"].update(complete=False))
        self.assertEqual(checked["status"], "execution_issue")

    def test_separate_budgets_allow_combined_peak_above_old_guard(self):
        checked = self.changed(supervisor_change=lambda supervisor: supervisor.update(
            raw_artifact_peak_observed_bytes=50 << 20, metadata_peak_observed_bytes=50 << 20,
            artifact_peak_observed_bytes=100 << 20))
        self.assertEqual(checked["status"], "accepted")

    def test_resource_signal_cannot_masquerade_as_successful_native_stage(self):
        stages = [decode_json(line) for line in self.read("data/STAGES.jsonl").splitlines()]
        stages[1]["resource_signal"] = "file_size_limit"
        raw = b"".join(json.dumps(stage).encode() + b"\n" for stage in stages)
        checked = self.changed(
            record_change=lambda record: record["phases"][4]["process"].update(resource_signal="file_size_limit"),
            replacements={"data/STAGES.jsonl": raw})
        self.assertEqual(checked["status"], "execution_issue")

    def test_three_of_three_and_structural_separation(self):
        freeze = {"cases": [{"width": 2}]}
        rows = []
        for trial in (1, 2, 3):
            for route, status in (("exporter", "accepted"), ("ric3", "resource_unknown"), ("structural", "structural_accepted")):
                rows.append({"width": 2, "route": route, "trial": trial, "status": status,
                             "wall_seconds": trial if route != "ric3" else 30,
                             "raw_artifact_bytes": 100})
        result = summaries(rows, freeze, True)
        self.assertEqual(result["exporter_exclusive_widths"], [2])
        self.assertIsNone(result["groups"][1]["completed_wall_seconds"])
        self.assertEqual(result["groups"][0]["completed_wall_seconds"], {"median": 2, "min": 1, "max": 3})
        incomplete = summaries(rows, freeze, False)
        self.assertEqual(incomplete["primary_outcome"], "incomplete")
        self.assertEqual(incomplete["exporter_exclusive_widths"], [])
        rows.pop(6)  # Only two accepted exporter trials remain.
        self.assertEqual(summaries(rows, freeze, True)["exporter_exclusive_widths"], [])

    def test_truncated_final_stage_record_is_not_a_verdict(self):
        self.assertEqual(stage_journal(b'{"event":"start"}\n{"event":"finish"'), [{"event": "start"}])
        with self.assertRaises(ValueError):
            stage_journal(b'{"event":"start"}\n{"event":"finish"\n')



if __name__ == "__main__":
    unittest.main()
