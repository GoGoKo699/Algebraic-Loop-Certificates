"""Additive full field-source comparator; no public schema change."""
from pathlib import Path
import subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class CharacterTaylorAudit(unittest.TestCase):
    def test_checked_character_taylor_comparison(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'audits/character_taylor_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=300)
if __name__=='__main__':unittest.main()
