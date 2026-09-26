"""Exact finite p-module arithmetic and deterministic source normalization.

Rows of an endomorphism use different moduli. This is not ordinary matrix
arithmetic over a field or one common matrix ring. No factor/search routines.
"""
from dataclasses import dataclass


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def valuation(x, p, e):
    if x == 0:
        return e
    count = 0
    while x % p == 0:
        x //= p; count += 1
    return count


def product(A, B, mods):
    cols = tuple(zip(*B))
    return tuple(tuple(sum(x*y for x,y in zip(row,col)) % q for col in cols)
                 for row,q in zip(A,mods))


def apply(A, x, mods):
    return tuple(sum(u*v for u,v in zip(row,x)) % q for row,q in zip(A,mods))


def difference(A, B, mods):
    return tuple(tuple((x-y) % q for x,y in zip(ar,br)) for ar,br,q in zip(A,B,mods))


def power(A, exponent, mods):
    if type(exponent) is not int or exponent < 0:
        raise ValueError('Nonnegative integer exponent required.')
    result = eye(len(A))
    while exponent:
        if exponent & 1: result = product(result,A,mods)
        exponent >>= 1
        if exponent: A = product(A,A,mods)
    return result


def endomorphism(A, mods):
    return all(A[i][j]*mods[j] % mods[i] == 0
               for i in range(len(mods)) for j in range(len(mods)))


def diagonalize(G,p,e):
    """Compute U G V = diag(p**s_i,0), tracking U inverse exactly.

    Only a minimum-valuation pivot's UNIT factor is inverted. Operations are
    deterministic, polynomial-size exact operations over Z/p**e Z.
    """
    N=p**e; n=len(G)
    R=[list(r) for r in G];U=[list(r) for r in eye(n)]
    V=[list(r) for r in eye(n)];Ui=[list(r) for r in eye(n)]
    vals=[]
    for t in range(n):
        positions=[(valuation(R[i][j],p,e),i,j) for i in range(t,n) for j in range(t,n) if R[i][j]]
        if not positions: break
        s,i,j=min(positions)
        R[t],R[i]=R[i],R[t];U[t],U[i]=U[i],U[t]
        for row in Ui:row[t],row[i]=row[i],row[t]
        for M in (R,V):
            for row in M:row[t],row[j]=row[j],row[t]
        divisor=p**s; unit=R[t][t]//divisor; inv=pow(unit,-1,N)
        R[t]=[x*inv%N for x in R[t]];U[t]=[x*inv%N for x in U[t]]
        for row in Ui:row[t]=row[t]*unit%N
        for i in range(n):
            if i==t:continue
            if R[i][t] % divisor:raise ArithmeticError('Pivot divisibility failure.')
            q=R[i][t]//divisor
            if q:
                R[i]=[(x-q*y)%N for x,y in zip(R[i],R[t])]
                U[i]=[(x-q*y)%N for x,y in zip(U[i],U[t])]
                for row in Ui:row[t]=(row[t]+q*row[i])%N
        for j in range(n):
            if j==t:continue
            if R[t][j] % divisor:raise ArithmeticError('Row pivot divisibility failure.')
            q=R[t][j]//divisor
            if q:
                for M in (R,V):
                    for row in M:row[j]=(row[j]-q*row[t])%N
        vals.append(s)
    U,V,Ui,R=tuple(map(tuple,U)),tuple(map(tuple,V)),tuple(map(tuple,Ui)),tuple(map(tuple,R))
    mods=(N,)*n
    if product(U,Ui,mods)!=eye(n) or product(Ui,U,mods)!=eye(n):
        raise ArithmeticError('Tracked coordinate inverse failed.')
    if product(product(U,G,mods),V,mods)!=R:
        raise ArithmeticError('Diagonalization replay failed.')
    expected=tuple(tuple(p**vals[i] if i==j and i<len(vals) else 0 for j in range(n)) for i in range(n))
    if R!=expected:raise ArithmeticError('Result is not diagonal.')
    return U,V,Ui,tuple(vals)


@dataclass(frozen=True)
class CyclicModule:
    p:int
    e:int
    U:tuple
    V:tuple
    Ui:tuple
    valuations:tuple
    moduli:tuple
    action:tuple
    initial:tuple
    krylov:tuple

    def coordinates(self,y):
        N=self.p**self.e; n=len(self.U);k=len(self.moduli)
        z=apply(self.U,y,(N,)*n)
        if any(z[i] for i in range(k,n)):return None
        if any(z[i]%(self.p**s) for i,s in enumerate(self.valuations)):return None
        return tuple(z[i]//(self.p**s) for i,s in enumerate(self.valuations))

    def coefficients(self,z):
        padded=tuple(z)+(0,)*(len(self.U)-len(z))
        return apply(self.V,padded,(self.p**self.e,)*len(self.U))

    def polynomial_action(self,coefficients):
        """Evaluate h(C) on this finite module, not on an arbitrary complement."""
        k=len(self.moduli);B=tuple((0,)*k for _ in range(k))
        for coefficient in reversed(coefficients):
            B=product(B,self.action,self.moduli)
            B=tuple(tuple((v+coefficient*int(i==j))%self.moduli[i] for j,v in enumerate(row))
                    for i,row in enumerate(B))
        return B


def build_module(A,c,a,p,e):
    N=p**e;d=len(A);D=d+1
    T=tuple(tuple(r)+(v,) for r,v in zip(A,c))+((0,)*d+(1,),)
    v=tuple(a)+(1,);cols=[];cur=v
    for _ in range(D):cols.append(cur);cur=apply(T,cur,(N,)*D)
    G=tuple(zip(*cols))
    U,V,Ui,vals=diagonalize(G,p,e);k=len(vals)
    mods=tuple(p**(e-s) for s in vals)
    # Q sends the i-th mixed-order generator to U^{-1} p^s_i e_i.
    Q=tuple(tuple(Ui[i][j]*p**vals[j]%N for j in range(k)) for i in range(D))
    UTQ=product(product(U,T,(N,)*D),Q,(N,)*D)
    if any(x for row in UTQ[k:] for x in row):raise ArithmeticError('Cyclic module is not invariant.')
    C=[]
    for i,s in enumerate(vals):
        divisor=p**s
        if any(x%divisor for x in UTQ[i]):raise ArithmeticError('Module-action division invalid.')
        C.append(tuple((x//divisor)%mods[i] for x in UTQ[i]))
    C=tuple(C)
    if not endomorphism(C,mods):raise ArithmeticError('Invalid mixed-module homomorphism.')
    temporary=CyclicModule(p,e,U,V,Ui,vals,mods,C,(),G)
    initial=temporary.coordinates(v)
    if initial is None:raise ArithmeticError('Initial point missing from its module.')
    return CyclicModule(p,e,U,V,Ui,vals,mods,C,initial,G)


def ceil_log(n,p):
    a=0;value=1
    while value<n:value*=p;a+=1
    return a


def p_order(u,mods,p,e):
    """Find the exact p-power order under the checked residue-unipotent promise."""
    I=eye(len(mods));cur=u;r=1;a=0
    bound=e+ceil_log(len(mods),p)
    while cur!=I:
        if a>=bound:raise ValueError('Not a p-element within the finite-module bound.')
        cur=power(cur,p,mods);r*=p;a+=1
    return a,r


def p_log(u,B,mods,p,a):
    """Decide B in <u>, extracting p-adic digits with no p-sized search.

    u has certified exact order p**a. The order-p digit comes either from a
    residue-field nilpotent matrix or the first nonzero module-precision layer.
    Every extracted digit and the final candidate are replayed exactly.
    """
    k=len(mods);I=eye(k);r=p**a
    if a==0:return (0 if B==I else None), 'identity', 0
    w=power(u,r//p,mods);residue_mods=(p,)*k
    wb=tuple(tuple(v%p for v in row) for row in w)
    mode='residue_nilpotent' if wb!=I else 'precision_digit'
    if mode=='residue_nilpotent':
        K=difference(wb,I,residue_mods);pre=I;top=K
        for _ in range(k):
            nxt=product(top,K,residue_mods)
            if not any(v for row in nxt for v in row):break
            pre,top=top,nxt
        else:raise ValueError('Order-p residue was not unipotent.')
        i,j=next((i,j) for i in range(k) for j in range(k) if top[i][j])
        denominator=top[i][j]
    else:
        K=difference(w,I,mods)
        choices=[(valuation(v,p,mods[i].bit_length()),i,j) for i,row in enumerate(K) for j,v in enumerate(row) if v]
        if not choices:raise ValueError('Claimed order-p generator is identity.')
        layer,i,j=min(choices)
        if layer<1:raise ValueError('Wrong precision branch.')
        divisor=p**layer;denominator=(K[i][j]//divisor)%p
    z=0;place=1;steps=0
    for jdigit in range(a):
        residual=product(B,power(u,(-z)%r,mods),mods)
        V=power(residual,p**(a-1-jdigit),mods);steps+=1
        if mode=='residue_nilpotent':
            vb=tuple(tuple(v%p for v in row) for row in V)
            term=product(pre,difference(vb,I,residue_mods),residue_mods)
            numerator=term[i][j]
        else:
            value=difference(V,I,mods)[i][j]
            if value%divisor:return None,mode,steps
            numerator=(value//divisor)%p
        digit=numerator*pow(denominator,-1,p)%p
        if power(w,digit,mods)!=V:return None,mode,steps
        z+=place*digit;place*=p
    return (z if power(u,z,mods)==B else None),mode,steps
