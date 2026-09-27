"""Exact local controls for the bounded native-SMT verification gate."""
from pathlib import Path
import subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class InvariantValidationGate(unittest.TestCase):
    def test_fixed_semantic_controls(self):
        cmd=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(cmd+[str(ROOT/'audits/invariant_validation_v1/verify.py')],cwd=ROOT,check=True,timeout=60)
if __name__=='__main__':unittest.main()
