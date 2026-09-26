"""Explicit experimental regression; no primary certificate-schema expansion."""
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ModularLiftingResearch(unittest.TestCase):
    def test_precision_composition(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'research/modular_lifting_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=960)
if __name__=='__main__':unittest.main()
