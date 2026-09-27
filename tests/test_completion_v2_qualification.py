"""Replay the amended compatibility evidence and reject semantic corruption."""
import copy
import json
import unittest

from research.completion_v2.verify_qualification import (
    LIMIT, QUALIFICATION, artifact_reader, decode_json, validate_case,
    validate_provenance, validate_retained_storage, verify_qualification,
)


class CompletionV2Qualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = decode_json((QUALIFICATION / "MANIFEST.json").read_bytes())
        cls.read = staticmethod(artifact_reader(QUALIFICATION, cls.manifest["artifacts"]))

    def loaded_case(self, index=0):
        case = copy.deepcopy(self.manifest["cases"][index])
        return (case, decode_json(self.read(case["worker_result"])),
                decode_json(self.read(case["supervisor_result"])))

    def validate_modified(self, case, record, supervisor, replacements=None):
        replacements = dict(replacements or {})
        replacements[case["id"] + "/data/JOURNAL.json"] = json.dumps(record).encode()
        read = lambda name: replacements[name] if name in replacements else self.read(name)
        return validate_case(case, record, supervisor, read)

    def test_all_smoke_proofs_and_counterexamples(self):
        result = verify_qualification()
        self.assertEqual([row["status"] for row in result["cases"]],
                         ["accepted", "accepted", "rejected", "rejected"])
        self.assertEqual([row["proofs_replayed"] for row in result["cases"]], [9, 9, 5, 0])
        self.assertEqual([row["rejected_obligation"] for row in result["cases"]],
                         [None, None, "Inductive", "Reset"])
        self.assertEqual(result["negative_assignments_checked"], 2)
        self.assertEqual(result["proofs_replayed"], 23)
        self.assertEqual(result["checked_artifact_files"], 300)

    def test_old_schema_exhausted_components_and_inconsistent_accounting_reject(self):
        mutations = (
            lambda report: report.update(schema="alc-bounded-workflow-v1"),
            lambda report: report["limits"].update(metadata_bytes=2 * LIMIT),
            lambda report: report.update(raw_artifact_peak_observed_bytes=LIMIT + 1),
            lambda report: report.update(metadata_peak_observed_bytes=LIMIT + 1),
            lambda report: report.update(metadata_bytes=report["metadata_bytes"] + 1),
            lambda report: report.update(metadata_peak_observed_bytes=0),
            lambda report: report.update(open_deleted_peak_observed_bytes=
                                         report["raw_artifact_peak_observed_bytes"] + 1),
            lambda report: report.update(observed_violations=["metadata_limit"]),
            lambda report: report.update(status="resource_limit", reason="artifact_limit"),
        )
        for index, mutation in enumerate(mutations):
            case, record, supervisor = self.loaded_case()
            mutation(supervisor)
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                self.validate_modified(case, record, supervisor)

    def test_report_validation_accepts_two_independent_components(self):
        # Exercise the amended accounting rule independently of artifact binding:
        # a total above one component's budget is permitted when each stays below
        # its own cap. No native measurement is synthesized by this unit test.
        case, record, supervisor = self.loaded_case()
        half_total = LIMIT // 2 + 1
        supervisor.update(raw_artifact_bytes=half_total,
                          raw_artifact_peak_observed_bytes=half_total,
                          metadata_bytes=half_total,
                          metadata_peak_observed_bytes=half_total,
                          all_trial_files_bytes=2 * half_total,
                          artifact_final_bytes=2 * half_total,
                          artifact_peak_observed_bytes=2 * half_total)
        self.assertEqual(self.validate_modified(case, record, supervisor)["status"], "accepted")

    def test_unknown_log_names_and_temporary_metadata_names_remain_raw(self):
        case = {"id": "exporter", "supervisor_result": "exporter/SUPERVISOR.json"}
        artifacts = {
            "exporter/data/JOURNAL.json": {"raw_bytes": 11},
            "exporter/data/Inductive_solve.stdout.txt": {"raw_bytes": 13},
            "exporter/data/unexpected.json": {"raw_bytes": 17},
            "exporter/tmp/JOURNAL.json": {"raw_bytes": 19},
            "exporter/workflow.stdout": {"raw_bytes": 23},
            "exporter/data/Reset.cnf": {"raw_bytes": 29},
            "exporter/SUPERVISOR.json": {"raw_bytes": 1000},
        }
        expected = {"all_trial_files_bytes": 112, "raw_artifact_bytes": 65, "metadata_bytes": 47}
        validate_retained_storage(case, expected, artifacts)
        # A suffix-only split incorrectly moves the two unknown names to metadata.
        wrong = dict(expected, raw_artifact_bytes=29, metadata_bytes=83)
        with self.assertRaisesRegex(ValueError, "finite path classification"):
            validate_retained_storage(case, wrong, artifacts)

    def test_native_proof_and_negative_control_corruption_still_reject(self):
        case, record, supervisor = self.loaded_case()
        with self.assertRaises(ValueError):
            self.validate_modified(case, record, supervisor, {"exporter/data/Reset.lrat": b""})
        case, record, supervisor = self.loaded_case(3)
        case["mutation"]["latch_index"] = 1
        with self.assertRaisesRegex(ValueError, "Changed rIC3 reset corruption"):
            self.validate_modified(case, record, supervisor)
        case, record, supervisor = self.loaded_case(2)
        with self.assertRaises(ValueError):
            self.validate_modified(case, record, supervisor,
                                   {"exporter_bad/data/Inductive_solve.stdout.txt":
                                    b"s SATISFIABLE\nv 0\n"})

    def test_previous_binary_identity_and_build_dossier_are_preserved(self):
        for name in ("ric3", "certifaiger"):
            manifest = copy.deepcopy(self.manifest)
            manifest["binary_sha256"][name] = "0" * 64
            with self.subTest(binary=name), self.assertRaisesRegex(ValueError, "previous qualified tools"):
                validate_provenance(manifest, self.read)
        manifest = copy.deepcopy(self.manifest)
        manifest["prior_qualification_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Previous qualification manifest binding"):
            validate_provenance(manifest, self.read)
        manifest = copy.deepcopy(self.manifest)
        manifest["source_files_sha256"]["research/completion_v1/worker.py"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Previously qualified worker or helper"):
            validate_provenance(manifest, self.read)
        # Alter a build record not otherwise used to parse proof verdicts, while
        # retaining the same executable identity. The historical dossier still binds it.
        read = lambda name: b"changed help\n" if name == "build/check-help.txt" else self.read(name)
        with self.assertRaisesRegex(ValueError, "Previous build dossier bytes changed"):
            validate_provenance(self.manifest, read)


if __name__ == "__main__":
    unittest.main()
