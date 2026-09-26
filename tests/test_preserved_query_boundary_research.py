"""Replay the supplied independent audit without replacing the live scope audit."""
from pathlib import Path
import subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class PreservedQueryBoundaryResearch(unittest.TestCase):
    def test_authentic_additions(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'audits/query_boundary_checkpoint_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=300)
if __name__=='__main__':unittest.main()
