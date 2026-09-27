"""A fixed existing workload, including native C translation controls."""
import subprocess
import sys
import unittest
from pathlib import Path


class NativeLfsrGate(unittest.TestCase):
    def test_preserved_native_and_matched_certificates(self):
        root = Path(__file__).resolve().parents[1]
        subprocess.run([sys.executable, 'audits/native_lfsr_v1/verify.py'],
                       cwd=root, check=True)
