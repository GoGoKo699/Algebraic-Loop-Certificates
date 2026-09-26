"""Additive direct modular proof checks; primary API remains unchanged."""
from pathlib import Path
import subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class DirectModularResearch(unittest.TestCase):
    def test_exact_research_contract(self):
        subprocess.run([sys.executable,str(ROOT/'research/direct_modular_hits_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=360)
if __name__=='__main__':unittest.main()
