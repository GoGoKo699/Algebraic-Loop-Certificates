"""Compile one prime-power source into an exact all-target membership predicate.

Pure research namespace. Exact mixed-module normalization plus one independently
checked residue-field source certificate. No factor search or producer import.
"""
from dataclasses import dataclass
from alc.schema import DEFAULT_LIMITS,Invalid,ResourceLimit,integer,keys,matrix,vector,digest
from alc.checker import prime_proofs
from research.compiled_orbits_v1.checker import compile_orbit
from . import module as mod


def parse_source(document,limits=DEFAULT_LIMITS):
    keys(document,{'schema','modulus','prime','exponent','matrix','offset','initial'},'prime-power source')
    if document['schema']!='alc.prime-power-source.v1':raise Invalid('Wrong source schema.')
    N=integer(document['modulus'],'modulus',2,limits=limits)
    p=integer(document['prime'],'prime',2,limits=limits)
    e=integer(document['exponent'],'exponent',1,limits.max_integer_bits,limits)
    if e*(p.bit_length()-1)>limits.max_integer_bits:
        raise ResourceLimit('Prime-power bit length exceeds configured bound.')
    if e*(p.bit_length()-1)>N.bit_length() or p**e!=N:
        raise Invalid('Explicit modulus does not equal the claimed prime power.')
    raw=document['matrix']
    if type(raw) is not list or not raw:raise Invalid('Nonempty square matrix required.')
    d=len(raw)
    # The current unmodified field producer has a 32-coordinate default. One
    # coordinate of headroom accommodates the affine cyclic module.
    if d>=limits.max_dimension:raise ResourceLimit('Current source limit reserves one affine coordinate.')
    A=matrix(raw,d,N,'matrix',limits)
    c=vector(document['offset'],d,N,'offset',limits)
    a=vector(document['initial'],d,N,'initial',limits)
    return p,e,N,A,c,a


def residue_source(M):
    k=len(M.moduli);p=M.p
    return {'schema':'alc.orbit-source.v1','field':{'kind':'prime','modulus':p},
            'matrix':[[v%p for v in row] for row in M.action],
            'offset':[0]*k,'initial':[x%p for x in M.initial]}


@dataclass(frozen=True)
class CompiledPrimePower:
    binding:str
    p:int
    e:int
    state_dimension:int
    module:object
    residue:object
    semisimple_order:int
    p_generator:tuple
    p_exponent:int
    period:int
    limits:object

    def query(self,state):
        N=self.p**self.e
        b=vector(state,self.state_dimension,N,'queried state',self.limits)+(1,)
        coords=self.module.coordinates(b)
        def answer(member,reason,mode=None,digits=0):
            return {'source_sha256':self.binding,'verified':True,
                    'status':'reachable' if member else 'unreachable','reason':reason,
                    'point_period':self.period,'first_hit_computed':False,
                    'p_digit_mode':mode,'p_digits_checked':digits}
        if coords is None:return answer(False,'outside_cyclic_module')
        field=self.residue.query([x%self.p for x in coords])
        if field['status']!='reachable':return answer(False,'residue_orbit_obstruction')
        coefficients=self.module.coefficients(coords)
        B=self.module.polynomial_action(coefficients)
        if mod.apply(B,self.module.initial,self.module.moduli)!=coords:
            raise ArithmeticError('Target endomorphism did not replay its state.')
        if not mod.endomorphism(B,self.module.moduli):
            raise ArithmeticError('Target map violates mixed-modulus relations.')
        powered=mod.power(B,self.semisimple_order,self.module.moduli)
        z,mode,digits=mod.p_log(self.p_generator,powered,self.module.moduli,self.p,self.p_exponent)
        return answer(z is not None,'complete_prime_power_orbit' if z is not None else 'p_primary_obstruction',mode,digits)


def compile_source(document,certificate,limits=DEFAULT_LIMITS):
    p,e,N,A,c,a=parse_source(document,limits);d=len(A)
    keys(certificate,{'schema','source_sha256','prime_proofs','inverse_matrix','residue_certificate'},'prime-power compilation')
    if certificate['schema']!='alc.compiled-prime-power.v1':raise Invalid('Wrong compilation schema.')
    binding=digest(document)
    if certificate['source_sha256']!=binding:raise Invalid('Wrong source binding.')
    proved=prime_proofs(certificate['prime_proofs'],limits,{'modular_power_checks':0})
    if p not in proved:raise Invalid('Prime parameter is not proved prime.')
    inv=matrix(certificate['inverse_matrix'],d,N,'inverse witness',limits)
    if mod.product(A,inv,(N,)*d)!=mod.eye(d) or mod.product(inv,A,(N,)*d)!=mod.eye(d):
        raise Invalid('Invalid ring inverse witness.')
    M=mod.build_module(A,c,a,p,e)
    source=residue_source(M)
    field=compile_orbit(source,certificate['residue_certificate'],limits)
    # M is cyclic under A, so its reduction has a cyclic generating vector.
    # In particular the field point period is the residue matrix order.
    r0=field.point_period;m=r0
    while m%p==0:m//=p
    u=mod.power(M.action,m,M.moduli)
    try:alpha,ppart=mod.p_order(u,M.moduli,p,e)
    except ValueError as exc:raise Invalid('False residue/unipotent source obligation.') from exc
    period=m*ppart
    if period>N**d:raise Invalid('Computed point period exceeds state count.')
    return CompiledPrimePower(binding,p,e,d,M,field,m,u,alpha,period,limits)
