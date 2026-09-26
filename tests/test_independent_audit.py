"""Keep the independently developed reference in the primary CI test suite."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IndependentAudit(unittest.TestCase):
    def test_cross_implementation(self):
        subprocess.run([sys.executable,str(ROOT/'audits/independent_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=240)


if __name__=='__main__':
    unittest.main()
