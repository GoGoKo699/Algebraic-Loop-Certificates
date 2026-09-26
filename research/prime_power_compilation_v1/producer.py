"""Bounded source-only proof producer. Hard algebra occurs in ONE field compiler.

Module normalization is polynomial, not a hidden table of residue states.
The existing field producer remains a reference, not a new fast DLP algorithm.
"""
from alc.schema import ResourceLimit,digest
from research.compiled_orbits_v1.producer import produce as field_produce
from research.modular_lifting_v1.producer import inverse_over_ring
from .checker import parse_source,residue_source
from .module import build_module


def produce(document,max_work=1000000):
    if type(max_work) is not int or max_work<0:raise ValueError('Nonnegative work budget required.')
    try:
        p,e,N,A,c,a=parse_source(document)
        if max_work==0:return {'status':'unknown','reason':'No field-construction budget.'}
        inv=inverse_over_ring(A,N)
        M=build_module(A,c,a,p,e)
        candidate=field_produce(residue_source(M),max_work=max_work-1)
        if candidate['status']!='candidate':return {'status':'unknown','reason':candidate['reason']}
        cert={'schema':'alc.compiled-prime-power.v1','source_sha256':digest(document),
              'prime_proofs':candidate['certificate']['prime_proofs'],
              'inverse_matrix':inv,'residue_certificate':candidate['certificate']}
        return {'status':'candidate','certificate':cert,
                'metrics':{'field_compilations':1,'target_log_calls':0,'trajectory_steps':0,
                           'module_rank':len(M.moduli),'module_exponents':[e-s for s in M.valuations],
                           'base_alignment_log_calls':candidate['metrics']['base_alignment_log_calls'],
                           'budgeted_search_work':1+candidate['metrics']['budgeted_search_work']}}
    except ResourceLimit as exc:return {'status':'unknown','reason':str(exc)}
