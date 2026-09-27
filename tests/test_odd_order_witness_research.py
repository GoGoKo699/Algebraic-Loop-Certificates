"""Check seed-dependent periods at the preserved external witness interface."""

import subprocess
import sys
import unittest
from pathlib import Path


class OddOrderWitnessResearch(unittest.TestCase):
    def test_odd_order_witness_checkpoint(self):
        root = Path(__file__).resolve().parents[1]
        subprocess.run([sys.executable, "-m", "research.odd_order_witness_v1.verify"],
                       cwd=root, check=True)
