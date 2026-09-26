"""Proof-boundary, parser and deliberately false-certificate regression tests."""
import ast
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from alc.schema import Invalid, ResourceLimit, Limits, Problem, load
from alc.checker import advance, prime_proofs, verify
from alc.producer import Builder, assemble, produce

ROOT = Path(__file__).resolve().parents[1]


def example():
    return load(ROOT/'examples/fibonacci_f7/problem.json'), load(ROOT/'examples/fibonacci_f7/certificate.json')


class CertificateBoundaries(unittest.TestCase):
    def test_examples(self):
        for directory in (ROOT/'examples').iterdir():
            if directory.is_dir() and (directory/'certificate.json').exists():
                verify(load(directory/'problem.json'), load(directory/'certificate.json'))

    def test_mutations_are_rejected(self):
        p, c = example()
        mutations = []
        def add(field, value):
            x = deepcopy(c); x[field] = value; mutations.append(x)
        add('first', 12); add('first', c['first']+c['period'])
        add('first', -1); add('first', True); add('period', 0)
        add('period', 32); add('period_factors', [])
        add('period_factors', [[2,3]])
        add('period_factors', [[2,2],[2,2]])
        add('period_factors', [[2,100000]])
        add('inverse_matrix', [[1,0],[0,1]])
        add('prime_proofs', []); add('problem_sha256', '0'*64)
        add('kind', 'unreachable'); add('unexpected', 1)
        add('period', 1.0)
        x=deepcopy(c);x['prime_proofs'][-1]['witness']=1;mutations.append(x)
        x=deepcopy(c);x['prime_proofs'][-1]['factors']=[];mutations.append(x)
        for i, m in enumerate(mutations):
            with self.subTest(mutation=i):
                with self.assertRaises(Invalid): verify(p, m)

    def test_composite_factor_exploit_is_not_accepted(self):
        p, c = example(); problem = Problem.parse(p)
        stats={'power_checks':0,'matrix_vector_products':0,'matrix_squares':0}
        # A deficient checker trusting factors 4 and 8 could accept period 32:
        self.assertEqual(advance(problem,32,stats),problem.initial)
        self.assertNotEqual(advance(problem,32//4,stats),problem.initial)
        self.assertNotEqual(advance(problem,32//8,stats),problem.initial)
        c['period']=32; c['period_factors']=[[4,1],[8,1]]
        with self.assertRaises(Invalid):verify(p,c)

    def test_nonminimal_with_genuine_factors(self):
        p,c=example(); c['period']=32;c['period_factors']=[[2,5]]
        with self.assertRaisesRegex(Invalid,'not the least'):verify(p,c)

    def test_problem_is_independently_bound(self):
        p,c=example();p['target']=[1,0]
        with self.assertRaisesRegex(Invalid,'does not match'):verify(p,c)
        # Rebinding a false claim is not sufficient either.
        c['problem_sha256']=Problem.parse(p).fingerprint
        with self.assertRaisesRegex(Invalid,'does not hit'):verify(p,c)

    def test_characteristic_and_domain(self):
        p,c=example();p['field']['modulus']=9;c['problem_sha256']=Problem.parse(p).fingerprint
        with self.assertRaisesRegex(Invalid,'modulus'):verify(p,c)
        p,c=example();p['field']['kind']='extension'
        with self.assertRaises(Invalid):verify(p,c)
        for value in (-1,7,True,1.0):
            p,c=example();p['initial'][0]=value
            with self.assertRaises(Invalid):verify(p,c)
        p,c=example();p['matrix'][0].append(0)
        with self.assertRaises(Invalid):verify(p,c)
        p,c=example();p['extra']=0
        with self.assertRaises(Invalid):verify(p,c)

    def test_singular_input_and_producer_limit(self):
        p=Problem(3,((0,),),(0,),(1,),(0,)).as_dict()
        with self.assertRaises(Invalid):produce(p)
        p,c=example();result=produce(p,max_steps=12)
        self.assertEqual(result['status'],'inconclusive')
        self.assertNotIn('certificate',result)
        self.assertFalse(result['certified'])

    def test_declared_resource_limits(self):
        p,c=example()
        with self.assertRaises(ResourceLimit):verify(p,c,Limits(max_dimension=1))
        with self.assertRaises(ResourceLimit):verify(p,c,Limits(max_prime_records=1))
        c['period']=1<<1024
        with self.assertRaises(ResourceLimit):verify(p,c)
        with self.assertRaises(ResourceLimit):Builder(factor_budget=0).prove(7)

    def test_prime_proofs_are_exact(self):
        for p in (2,3,5,7,11,17,101,257,65537):
            b=Builder();b.prove(p);stats={'modular_power_checks':0}
            proven=prime_proofs([b.records[q] for q in sorted(b.records)],Limits(),stats)
            self.assertIn(p,proven)
        b=Builder();b.prove(7)
        records=[b.records[q] for q in sorted(b.records)]
        # Composite certificate record with p=9 and complete factors for p-1.
        for a in range(1,9):
            trial=deepcopy(records[:1])+[{'p':9,'witness':a,'factors':[[2,3]]}]
            with self.assertRaises(Invalid):prime_proofs(trial,Limits(),{'modular_power_checks':0})

    def test_point_period_not_matrix_order(self):
        p=load(ROOT/'examples/fixed_point/problem.json')
        c=load(ROOT/'examples/fixed_point/certificate.json')
        h=verify(p,c)
        self.assertEqual(h.period,1)
        self.assertEqual(p['matrix'],[[2,0],[0,1]])  # matrix order is 2 in F3.

    def test_affine_zero_initial_state_is_not_assumed_fixed(self):
        p=load(ROOT/'examples/affine_f5/problem.json')
        c=load(ROOT/'examples/affine_f5/certificate.json')
        h=verify(p,c)
        self.assertEqual((h.first,h.period),(3,5))

    def test_checker_does_not_import_producer(self):
        code=(ROOT/'alc/checker.py').read_text()
        tree=ast.parse(code)
        imports=[node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
        self.assertNotIn('producer',imports)
        self.assertFalse(any(isinstance(node,ast.Assert) for node in ast.walk(tree)))


class ParserBoundaries(unittest.TestCase):
    def test_rejected_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'x.json'
            for text in ('{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}','[1,2]','{'):
                path.write_text(text)
                with self.subTest(text=text):
                    with self.assertRaises(Invalid):load(path)
            path.write_bytes(b'\xff')
            with self.assertRaises(Invalid):load(path)
            path.write_text('{"large":"'+'a'*100+'"}')
            with self.assertRaises(ResourceLimit):load(path,Limits(max_bytes=20))


if __name__=='__main__':unittest.main()
