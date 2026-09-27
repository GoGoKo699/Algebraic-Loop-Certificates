"""Additive controlled comparison; existing source and query APIs unchanged."""
from pathlib import Path
import subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class PrimarySplittingAudit(unittest.TestCase):
    def test_matched_reduction_layer(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'audits/primary_splitting_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=300)
if __name__=='__main__':unittest.main()
