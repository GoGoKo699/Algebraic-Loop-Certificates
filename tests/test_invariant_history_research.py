"""Independent finite controls for the scoped invariant/history result."""

from pathlib import Path
import subprocess
import sys
import unittest


class InvariantHistoryResearch(unittest.TestCase):
    def test_characterization_and_premise_controls(self):
        root = Path(__file__).resolve().parents[1]
        subprocess.run([sys.executable, "-m", "research.invariant_history_v1.verify"],
                       cwd=root, check=True)
