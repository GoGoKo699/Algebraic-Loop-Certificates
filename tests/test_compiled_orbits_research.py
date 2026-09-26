"""Additive exact-source compiler gate; existing certificate formats unchanged."""
from pathlib import Path
import subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class CompiledOrbitResearch(unittest.TestCase):
    def test_complete_source_predicate(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'research/compiled_orbits_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=240)
if __name__=='__main__':unittest.main()
