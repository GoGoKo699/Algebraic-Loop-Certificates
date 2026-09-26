import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
PROBLEM=str(ROOT/'examples/fibonacci_f7/problem.json')
CERT=str(ROOT/'examples/fibonacci_f7/certificate.json')


class CommandLineTests(unittest.TestCase):
    def call(self, arguments, optimized=False):
        return subprocess.run([sys.executable]+(['-O'] if optimized else [])+['-m','alc']+arguments,
                              cwd=ROOT,capture_output=True,text=True,timeout=15)

    def test_verified_query_and_optimized_python(self):
        args=['query','--problem',PROBLEM,'--certificate',CERT,'--from',str(10**30),
              '--through',str(10**30+100),'--schedule','3','4']
        normal=self.call(args);optimized=self.call(args,True)
        self.assertEqual(normal.returncode,0,normal.stdout+normal.stderr)
        self.assertEqual(normal.stdout,optimized.stdout)
        out=json.loads(normal.stdout)
        self.assertEqual(out['window']['count'],6)
        self.assertEqual(out['intersection_with_supplied_schedule'],{'first':11,'period':16})

    def test_produce_then_verify_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            path=str(Path(d)/'candidate.json')
            p=self.call(['produce','--problem',PROBLEM,'--output',path])
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            v=self.call(['verify','--problem',PROBLEM,'--certificate',path])
            self.assertEqual(v.returncode,0,v.stdout+v.stderr)
            again=self.call(['produce','--problem',PROBLEM,'--output',path])
            self.assertEqual(again.returncode,3)

    def test_step_limit_does_not_write_certificate(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'no.json'
            r=self.call(['produce','--problem',PROBLEM,'--output',str(path),'--max-steps','1'])
            self.assertEqual(r.returncode,4)
            self.assertEqual(json.loads(r.stdout)['status'],'inconclusive')
            self.assertFalse(path.exists())

    def test_wrong_target_rejected_before_query(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'problem.json';p=json.loads(Path(PROBLEM).read_text());p['target']=[0,0]
            path.write_text(json.dumps(p))
            r=self.call(['query','--problem',str(path),'--certificate',CERT,'--through','100'])
            self.assertEqual(r.returncode,1)
            self.assertNotIn('window',json.loads(r.stdout))
