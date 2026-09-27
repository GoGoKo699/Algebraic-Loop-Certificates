"""Compact character/Taylor comparator for the complete prime-field contract.

The existing serialized source evidence is rechecked, not trusted or compiled
by the original compiler. Basic field/polynomial arithmetic and primality
verification are shared. Cyclic coordinates, coverage verification, Taylor
normal form, and binomial-digit query logic are written here. No call to the
old compiled-orbit, separating-invariant, or unipotent membership routines.
This is an audit implementation of classical algebra, not a retrieved solver.
"""
from dataclasses import dataclass
from math import comb, gcd, lcm
from alc.schema import Problem, DEFAULT_LIMITS, Invalid, keys, integer, matrix, vector, digest
from alc.checker import prime_proofs, factorization, product, identity
from research.complete_orbits_v1 import algebra as field


def solve_columns(columns, target, p):
    """Independent reduced-row-echelon solve; return None for inconsistency."""
    n, k = len(target), len(columns)
    rows = [[columns[j][i] % p for j in range(k)]+[target[i] % p] for i in range(n)]
    pivots = []
    r = 0
    for j in range(k):
        at = next((i for i in range(r,n) if rows[i][j]), None)
        if at is None: continue
        rows[r],rows[at] = rows[at],rows[r]
        inv = pow(rows[r][j],-1,p)
        rows[r] = [inv*v % p for v in rows[r]]
        for i in range(n):
            if i == r: continue
            multiple = rows[i][j]
            rows[i] = [(a-multiple*b) % p for a,b in zip(rows[i],rows[r])]
        pivots.append(j);r += 1
        if r == n: break
    if any(not any(row[:k]) and row[k] for row in rows): return None
    result = [0]*k
    for i,j in enumerate(pivots): result[j] = rows[i][k]
    return tuple(result)


def source_coordinates(problem):
    n,p = len(problem.A),problem.p
    T = tuple(row+(c,) for row,c in zip(problem.A,problem.c))+((0,)*n+(1,),)
    columns=[];v=problem.initial+(1,)
    for _ in range(n+2):
        relation=solve_columns(columns,v,p)
        if relation is not None:
            mu=tuple((-x)%p for x in relation)+(1,)
            k=len(columns)
            row_columns=tuple(zip(*columns))
            left=tuple(solve_columns(row_columns,tuple(int(i==j) for i in range(k)),p) for j in range(k))
            if any(x is None for x in left): raise ArithmeticError('Cyclic basis lost independence.')
            return tuple(columns),mu,left
        columns.append(v)
        v=tuple(sum(x*y for x,y in zip(row,v))%p for row in T)
    raise ArithmeticError('Cyclic dimension exceeded.')


def canonical_poly(raw,p,bound,label,limits,monic=False):
    if type(raw) is not list or len(raw)>bound+1: raise Invalid(label+': degree bound')
    f=tuple(integer(x,label,0,p-1,limits) for x in raw)
    if f and f[-1]==0: raise Invalid(label+': trailing zero')
    if monic and (len(f)<2 or f[-1]!=1): raise Invalid(label+': monic positive degree required')
    return f


def evaluate(poly,alpha,f,p):
    result=()
    for c in reversed(poly): result=field.add(field.mmul(result,alpha,f,p),(c,),p)
    return result


def check_coverage(factorizations, edges):
    """Independent union-find per prime-power support; no old coverage call."""
    values=[dict(v) for v in factorizations]
    primes={q for v in values for q in v}
    for q in primes:
        for level in {v.get(q,0) for v in values}-{0}:
            vertices=[i for i,v in enumerate(values) if v.get(q,0)>=level]
            parents={i:i for i in vertices}
            def root(i):
                while parents[i]!=i:
                    parents[i]=parents[parents[i]];i=parents[i]
                return i
            for i,j in edges:
                if i in parents and j in parents:
                    parents[root(i)]=root(j)
            if vertices and len({root(i) for i in vertices})!=1: return False
    return True


def taylor_basis(k,alpha,f,e,p):
    """Columns of h(X) -> h(alpha+Z) mod Z**e by polynomial multiplication.

    No derivatives/factorials are divided by characteristic-dependent values.
    The stored total number of base-field coefficients is polynomial in k.
    """
    columns=[];current=((1,),)+((),)*(e-1)
    for _ in range(k):
        columns.append(current)
        current=tuple(field.add(field.mmul(alpha,current[j],f,p),current[j-1] if j else (),p)
                      for j in range(e))
    return tuple(columns)


def linear_taylor(coefficients,columns,e,p):
    output=[() for _ in range(e)]
    for c,column in zip(coefficients,columns):
        for j in range(e):output[j]=field.add(output[j],field.scale(column[j],c,p),p)
    return tuple(output)


def lucas_binomial(n,j,p):
    """Binomial modulo p; j is bounded by source multiplicity, not by p."""
    answer=1
    while j:
        a,b=n%p,j%p
        if b>a:return 0
        answer=answer*(comb(a,b)%p)%p
        n//=p;j//=p
    return answer


@dataclass(frozen=True)
class CharacterTaylorOrbit:
    problem:object
    binding:str
    basis:tuple
    left_inverse:tuple
    components:tuple
    comparisons:tuple
    digit_component:int
    p_order:int
    period:int
    limits:object

    def query(self,state):
        p=self.problem.p
        y=vector(state,len(self.problem.A),p,'target',self.limits)+(1,)
        coefficients=tuple(sum(a*b for a,b in zip(row,y))%p for row in self.left_inverse)
        replay=tuple(sum(self.basis[j][i]*coefficients[j] for j in range(len(coefficients)))%p
                     for i in range(len(y)))
        def answer(member,reason):
            return {'source_sha256':self.binding,'status':'reachable' if member else 'unreachable',
                    'point_period':self.period,'first_hit_computed':False,'reason':reason}
        if replay!=y:return answer(False,'outside_cyclic_span')
        jets=[];constants=[];normalized=[]
        for f,e,order,alpha,alpha_inverse_powers,columns in self.components:
            row=linear_taylor(coefficients,columns,e,p)
            beta=row[0]
            if field.power(beta,order,f,p)!=(1,):return answer(False,'local_subgroup_obstruction')
            inverse=field.power(beta,order-1,f,p)
            jets.append(row);constants.append(beta)
            normalized.append(tuple(field.mmul(c,inverse,f,p) for c in row))
        for i,j,H,a,b,left_power,right_power in self.comparisons:
            u=evaluate(constants[i],a,H,p);v=evaluate(constants[j],b,H,p)
            if field.power(u,left_power,H,p)!=field.power(v,right_power,H,p):
                return answer(False,'character_relation_obstruction')
        # Coefficient at Z**(p**j) equals the j-th base-p exponent digit,
        # after multiplication by alpha**(p**j). Recover it from one largest block.
        f,e,_,alpha,_,_=self.components[self.digit_component]
        exponent=0;place=1
        while place<e:
            digit_element=field.mmul(normalized[self.digit_component][place],
                                      field.power(alpha,place,f,p),f,p)
            if len(digit_element)>1:return answer(False,'non_base_field_digit')
            digit=digit_element[0] if digit_element else 0
            exponent+=digit*place;place*=p
        # Reading only the prime-power coefficients is insufficient. Check ALL
        # coefficients in ALL blocks against this same characteristic-primary time.
        for index,(f,e,_,alpha,invpowers,_) in enumerate(self.components):
            for j in range(e):
                expected=field.scale(invpowers[j],lucas_binomial(exponent,j,p),p)
                if normalized[index][j]!=expected:
                    return answer(False,'taylor_coefficient_obstruction')
        return answer(True,'character_and_taylor_conditions')


def compile_baseline(source,certificate,limits=DEFAULT_LIMITS):
    """Verify the existing source format without invoking its original compiler."""
    keys(source,{'schema','field','matrix','offset','initial'},'source')
    if source['schema']!='alc.orbit-source.v1':raise Invalid('Wrong source schema.')
    problem=Problem.parse(dict(source,schema='alc.problem.v1',target=source['initial']),limits)
    keys(certificate,{'schema','source_sha256','prime_proofs','inverse_matrix','components','comparisons'},'certificate')
    if certificate['schema']!='alc.compiled-orbit.v1':raise Invalid('Wrong evidence schema.')
    binding=digest(source)
    if certificate['source_sha256']!=binding:raise Invalid('Source binding mismatch.')
    p=problem.p;n=len(problem.A)
    proven=prime_proofs(certificate['prime_proofs'],limits,{'modular_power_checks':0})
    if p not in proven:raise Invalid('Field prime not proved.')
    inverse=matrix(certificate['inverse_matrix'],n,p,'inverse',limits)
    if product(problem.A,inverse,p)!=identity(n) or product(inverse,problem.A,p)!=identity(n):
        raise Invalid('Invalid matrix inverse.')
    basis,mu,left=source_coordinates(problem);k=len(mu)-1
    raw=certificate['components']
    if type(raw) is not list or not 1<=len(raw)<=k:raise Invalid('Complete component list required.')
    expanded=(1,);seen=set();components=[];factorizations=[]
    for c in raw:
        keys(c,{'factor','multiplicity','order','order_factors'},'component')
        f=canonical_poly(c['factor'],p,k,'factor',limits,True)
        if not f[0] or f in seen:raise Invalid('Distinct unit-constant factors required.')
        seen.add(f)
        e=integer(c['multiplicity'],'multiplicity',1,k,limits)
        if len(expanded)-1+(len(f)-1)*e>k or not field.irreducible(f,p):
            raise Invalid('Invalid field factor.')
        for _ in range(e):expanded=field.mul(expanded,f,p)
        m=integer(c['order'],'order',1,p**(len(f)-1)-1,limits)
        factors=factorization(m,c['order_factors'],proven,limits)
        alpha=field.rem((0,1),f,p)
        if field.power(alpha,m,f,p)!=(1,) or any(field.power(alpha,m//q,f,p)==(1,) for q in factors):
            raise Invalid('Not the exact element order.')
        # Invert the source alpha once. Its proven nonzero status is essential.
        alpha_inverse=field.power(alpha,m-1,f,p);powers=[(1,)]
        for _ in range(1,e):powers.append(field.mmul(powers[-1],alpha_inverse,f,p))
        components.append((f,e,m,alpha,tuple(powers),taylor_basis(k,alpha,f,e,p)))
        factorizations.append(c['order_factors'])
    if expanded!=mu:raise Invalid('Incomplete primary factorization.')
    raw_edges=certificate['comparisons'];count=len(components)
    if type(raw_edges) is not list or len(raw_edges)>count*(count-1)//2:
        raise Invalid('Invalid comparison list.')
    edges=set();comparisons=[]
    for c in raw_edges:
        keys(c,{'i','j','algebra_modulus','left_root','right_root','alignment'},'comparison')
        i=integer(c['i'],'i',0,count-1,limits);j=integer(c['j'],'j',i+1,count-1,limits)
        if (i,j) in edges:raise Invalid('Duplicate comparison.')
        edges.add((i,j))
        f,_,m,*_=components[i];g,_,n,*_=components[j];D=gcd(m,n)
        if D==1:raise Invalid('Unneeded coprime comparison.')
        H=canonical_poly(c['algebra_modulus'],p,(len(f)-1)*(len(g)-1),'comparison algebra',limits,True)
        a=canonical_poly(c['left_root'],p,len(H)-2,'left root',limits)
        b=canonical_poly(c['right_root'],p,len(H)-2,'right root',limits)
        if evaluate(f,a,H,p) or evaluate(g,b,H,p):raise Invalid('Invalid field maps.')
        alignment=integer(c['alignment'],'alignment',1,D-1,limits)
        if gcd(alignment,D)!=1:raise Invalid('Nonunit alignment.')
        lpower,rpower=m//D,(n//D)*alignment
        if field.power(a,lpower,H,p)!=field.power(b,rpower,H,p):raise Invalid('False character calibration.')
        comparisons.append((i,j,H,a,b,lpower,rpower))
    if not check_coverage(factorizations,edges):raise Invalid('Incomplete character relations.')
    largest=max(range(count),key=lambda i:components[i][1]);maxe=components[largest][1]
    P=1
    while P<maxe:P*=p
    period=lcm(*(c[2] for c in components))*P
    if period>p**len(problem.A):raise Invalid('Period exceeds state count.')
    return CharacterTaylorOrbit(problem,binding,basis,left,tuple(components),tuple(comparisons),largest,P,period,limits)
