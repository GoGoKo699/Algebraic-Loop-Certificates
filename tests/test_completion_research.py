"""Reconcile preserved observations and reject misleading cost records."""

import copy
from decimal import Decimal
from pathlib import Path
import subprocess
import sys
import unittest

from research.completion_v1.audit_costs import decode_json, validate_record


class CompletionResearch(unittest.TestCase):
    def test_preserved_cost_accounting(self):
        root = Path(__file__).resolve().parents[1]
        subprocess.run([sys.executable, "-m", "research.completion_v1.audit_costs", "--check"],
                       cwd=root, check=True)

    def test_incomplete_or_false_completion_records_reject(self):
        root = Path(__file__).resolve().parents[1]
        original = decode_json((root / "research/proof_interface_v1/native/phase02/RESULTS.json").read_bytes())
        binaries = original["binary_sha256"]
        bad_records = []
        record = copy.deepcopy(original)
        record["stages"].pop()
        bad_records.append(record)
        record = copy.deepcopy(original)
        record["obligations"][5]["status"] = "sat"
        bad_records.append(record)
        record = copy.deepcopy(original)
        record["stages"][3]["exit_code"] = 10
        bad_records.append(record)
        record = copy.deepcopy(original)
        record["elapsed_seconds"] = Decimal(0)
        bad_records.append(record)
        record = copy.deepcopy(original)
        record["stages"][0]["elapsed_seconds"] = Decimal("-1")
        bad_records.append(record)
        record = copy.deepcopy(original)
        record["stages"][3]["timed_out"] = True
        bad_records.append(record)
        for index, record in enumerate(bad_records):
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                validate_record(record, binaries)
