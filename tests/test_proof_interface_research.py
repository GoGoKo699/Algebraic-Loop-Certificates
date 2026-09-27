"""Replay circuit witnesses, exact phase controls and retained SAT proofs."""

import subprocess
import sys
import unittest
from pathlib import Path


class ProofInterfaceResearch(unittest.TestCase):
    def test_preserved_proof_interface(self):
        root = Path(__file__).resolve().parents[1]
        subprocess.run([sys.executable, "-m", "research.proof_interface_v1.verify"],
                       cwd=root, check=True)
