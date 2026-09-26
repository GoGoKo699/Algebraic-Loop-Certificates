"""Additive reduction/observation audit; no new primary certificate format."""
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]


class QueryScopeResearch(unittest.TestCase):
    def test_query_scope_controls(self):
        prefix=[sys.executable]+(['-O'] if not __debug__ else [])
        subprocess.run(prefix+[str(ROOT/'research/query_scope_v1/verify.py')],
                       cwd=ROOT,check=True,timeout=300)


if __name__=='__main__':
    unittest.main()
