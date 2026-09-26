"""Additive research gate; primary certificate formats remain unchanged."""
from pathlib import Path
import subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class SeparatingInvariantResearch(unittest.TestCase):
    def test_inductive_predicate_contract(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'research/separating_invariants_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=240)
if __name__=='__main__':unittest.main()
