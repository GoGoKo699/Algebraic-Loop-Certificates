"""Verify retained compatibility evidence without installed native tools."""
import copy
import json
import unittest

from research.completion_v1.verify_qualification import (
    QUALIFICATION, artifact_reader, check_sat_assignment, decode_json,
    validate_case, validate_provenance, verify_qualification,
)


class CompletionQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = decode_json((QUALIFICATION / "MANIFEST.json").read_bytes())
        cls.read = staticmethod(artifact_reader(QUALIFICATION, cls.manifest["artifacts"]))

    def test_all_smoke_proofs_and_counterexamples(self):
        result = verify_qualification()
        self.assertEqual([row["status"] for row in result["cases"]],
                         ["accepted", "accepted", "rejected", "rejected"])
        self.assertEqual(result["negative_assignments_checked"], 2)
        self.assertEqual(result["proofs_replayed"], 23)

    def loaded_case(self):
        case = copy.deepcopy(self.manifest["cases"][0])
        return (case, decode_json(self.read(case["worker_result"])),
                decode_json(self.read(case["supervisor_result"])))

    def validate_modified(self, case, record, supervisor, replacements=None):
        replacements = dict(replacements or {})
        # Keep the redundant journal consistent so a modified-record test
        # reaches the actual semantic/sequence check, not just byte agreement.
        replacements[case["id"] + "/data/JOURNAL.json"] = json.dumps(record).encode()
        read = lambda name: replacements[name] if name in replacements else self.read(name)
        return validate_case(case, record, supervisor, read)

    def test_incomplete_false_or_resource_limited_completion_rejects(self):
        mutations = (
            lambda case, record, supervisor: record["phases"].pop(),
            lambda case, record, supervisor: record["phases"][6]["process"].update(exit_code=10),
            lambda case, record, supervisor: record["obligations"][0].update(status="sat"),
            lambda case, record, supervisor: record.update(status="accepted", model_sha256="0" * 64),
            lambda case, record, supervisor: supervisor.update(status="resource_limit", reason="deadline"),
            lambda case, record, supervisor: supervisor.update(observed_violations=["artifact_limit"]),
            lambda case, record, supervisor: supervisor["cleanup"].update(complete=False),
            lambda case, record, supervisor: case.update(expected_rejected_obligation="Reset"),
        )
        for index, mutation in enumerate(mutations):
            case, record, supervisor = self.loaded_case()
            mutation(case, record, supervisor)
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                self.validate_modified(case, record, supervisor)

    def test_missing_proof_and_false_negative_assignment_reject(self):
        case, record, supervisor = self.loaded_case()
        with self.assertRaises(ValueError):
            self.validate_modified(case, record, supervisor, {"exporter/data/Reset.lrat": b""})
        # A native SAT label alone is insufficient: the supplied assignment
        # must satisfy the independently supplied CNF.
        with self.assertRaises(ValueError):
            check_sat_assignment(b"p cnf 1 1\n1 0\n", b"s SATISFIABLE\nv -1 0\n")

    def test_substituted_solver_or_checker_build_rejects(self):
        for name in ("ric3", "certifaiger"):
            manifest = copy.deepcopy(self.manifest)
            manifest["binary_sha256"][name] = "0" * 64
            with self.subTest(binary=name), self.assertRaises(ValueError):
                validate_provenance(manifest, self.read)


if __name__ == "__main__":
    unittest.main()
