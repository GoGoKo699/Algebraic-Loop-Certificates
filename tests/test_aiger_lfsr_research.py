"""Replay source-bound proofs of the original input-dependent AAG circuits."""
import subprocess
import sys
import unittest
from pathlib import Path


class AigerLfsrResearch(unittest.TestCase):
    def test_raw_circuit_proofs_and_independent_controls(self):
        root = Path(__file__).resolve().parents[1]
        subprocess.run([sys.executable, '-m', 'research.aiger_lfsr_v1.verify'],
                       cwd=root, check=True)

    def test_preserved_native_comparison(self):
        root = Path(__file__).resolve().parents[1]
        subprocess.run([sys.executable, 'research/aiger_lfsr_v1/verify_native.py'],
                       cwd=root, check=True)
