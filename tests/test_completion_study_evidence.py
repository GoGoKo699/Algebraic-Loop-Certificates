"""Independent replay and counterfeit checks for the frozen comparison."""
import copy
import json
import io
from pathlib import Path
import tempfile
import tarfile
import unittest

from research.completion_v1.verify_study import (
    DEFAULT_STUDY, HERE, decode_json, digest, is_raw, reassemble_archive, stage_journal, study_directory, summaries, trial_reader,
    validate_trial, verify_study, write_manifest,
)


class CompletionStudyEvidence(unittest.TestCase):
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
        supervisor["stdout"] = values["workflow.stdout"].decode()
        supervisor["stdout_bytes"] = len(values["workflow.stdout"])
        values["SUPERVISOR.json"] = json.dumps(supervisor).encode()
        return validate_trial(self.row, self.case, self.freeze, inventory,
                              lambda name: values[name] if name in values else self.read(name))

    def test_committed_study_replays_without_native_tools(self):
        result = verify_study(self.base)
        self.assertEqual(result, decode_json((HERE / "STUDY_REPORT.json").read_bytes()))
        self.assertEqual(result["planned_trials"], 54)
        self.assertEqual(result["observed_trials"], 32)
        self.assertEqual(len(result["trials"]), 32)
        self.assertEqual(result["proofs_replayed"], 115)
        self.assertEqual(result["sat_assignments_checked"], 0)
        self.assertEqual(result["status"], "suspended")
        self.assertEqual(result["primary_outcome"], "incomplete")
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

    def test_post_run_manifest_is_immutable_and_hashes_files(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "evidence.bin").write_bytes(b"original")
            record = write_manifest(base)
            self.assertEqual(record["files"]["evidence.bin"]["bytes"], 8)
            with self.assertRaises(FileExistsError):
                write_manifest(base)

    def test_archive_cannot_escape_or_alias_evidence(self):
        for names in (("../escape",), ("study/link",), ("study/file", "study/file")):
            with self.subTest(names=names), tempfile.TemporaryDirectory() as directory:
                archive = Path(directory) / "study.tar.xz"
                with tarfile.open(archive, "w:xz") as stream:
                    for name in names:
                        item = tarfile.TarInfo(name)
                        item.size = 1
                        if name == "study/link":
                            item.type = tarfile.SYMTYPE
                            item.linkname = "/tmp/escape"
                        stream.addfile(item, io.BytesIO(b"x"))
                with self.assertRaises(ValueError), study_directory(archive):
                    pass

    def test_transport_segments_bind_each_part_and_whole_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            parts = base / "study.tar.xz.parts"
            parts.mkdir()
            raw = b"exact archive bytes"
            part = parts / "part-000"
            part.write_bytes(raw)
            index = {"schema": "alc-study-archive-parts-v1", "archive_name": "study.tar.xz",
                     "archive_bytes": len(raw), "archive_sha256": digest(raw),
                     "parts": [{"file": "part-000", "bytes": len(raw), "sha256": digest(raw)}]}
            manifest = parts / "manifest.json"
            manifest.write_text(json.dumps(index))
            reassemble_archive(parts, base / "study.tar.xz")
            self.assertEqual((base / "study.tar.xz").read_bytes(), raw)
            (base / "study.tar.xz").unlink()
            part.write_bytes(b"X" + raw[1:])
            with self.assertRaisesRegex(ValueError, "part hash changed"):
                reassemble_archive(parts, base / "study.tar.xz")
            (base / "study.tar.xz").unlink()
            part.write_bytes(raw)
            index["archive_sha256"] = "0" * 64
            manifest.write_text(json.dumps(index))
            with self.assertRaisesRegex(ValueError, "Reassembled archive hash/size changed"):
                reassemble_archive(parts, base / "study.tar.xz")


if __name__ == "__main__":
    unittest.main()
