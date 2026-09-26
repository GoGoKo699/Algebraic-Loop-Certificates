"""Additive regression gate; does not modify the primary certificate format."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]


class CompleteOrbitResearchAudit(unittest.TestCase):
    def test_complete_algebraic_decision_research(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'research/complete_orbits_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=180)


if __name__=='__main__':
    unittest.main()
