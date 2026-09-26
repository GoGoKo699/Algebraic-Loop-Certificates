"""Additive target-free prime-power compiler gate; stable APIs unchanged."""
from pathlib import Path
import subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class PrimePowerCompilationResearch(unittest.TestCase):
    def test_exact_source_compiler(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'research/prime_power_compilation_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=300)
if __name__=='__main__':unittest.main()
