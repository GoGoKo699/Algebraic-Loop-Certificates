"""Independent finite arithmetic/history checks; imports no witness producer."""

from collections import Counter
import json
from math import lcm


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def factor_integer(value):
    """Tiny finite-control data acquisition, not a fast factorization claim."""
    result=[];divisor=2
    while divisor*divisor<=value:
        exponent=0
        while value%divisor==0:
            value//=divisor;exponent+=1
        if exponent:
            result.append((divisor,exponent))
        divisor+=1
    if value>1:
        result.append((value,1))
    return result


def repeat(update, state, count):
    for _ in range(count):
        state=update(state)
    return state


def orbit_tables(n, update):
    size=1<<n
    if len({update(s) for s in range(size)})!=size:
        return None
    tables=[]
    for s in range(size):
        phase={};r=s
        while r not in phase:
            phase[r]=len(phase);r=update(r)
        require(r==s,"permutation did not close")
        tables.append(phase)
    return tables


def selected_period(update, s, M, factors):
    value=1
    for prime,exponent in factors:
        for k in range(1,exponent+1):
            # Deliberately no precomputed kernels or matrix arithmetic.
            if repeat(update,s,M//prime**k)!=s:
                value*=prime
    return value


def step(n, update, q, t, u, counter_bits):
    mask=(1<<n)-1
    r,s,c=q&mask,(q>>n)&mask,q>>(2*n)
    ar=update(r)
    match=s!=0 and ar==s
    bad=bool((u==0 and c and match) or (s!=0 and ar==0))
    new_t=0 if u or not s or match else (t+1)%(1<<counter_bits)
    if u:
        return u|(u<<n),new_t,bad
    return ar|(s<<n)|(int(not c and not match)<<(2*n)),new_t,bad


def H(n,update,q,t,periods):
    mask=(1<<n)-1
    r,s,c=q&mask,(q>>n)&mask,q>>(2*n)
    return (r==s==t==0) or (s!=0 and 0<=t<periods[s] and r==repeat(update,s,t) and c==t%2)


def check_case(n,update,M,tables):
    factors=factor_integer(M)
    periods=[selected_period(update,s,M,factors) for s in range(1<<n)]
    require(periods==[len(table) for table in tables],"fixed-test product wrong")
    require(periods[0]==1,"zero seed period convention")
    require(all(repeat(update,s,M)==s for s in range(1<<n)),"invalid annihilator control")
    L=max(1,M.bit_length())
    edges=0;h_states=0
    require(H(n,update,0,0,periods),"history initialization")
    for s in range(1<<n):
        # Include every possible original r,c and each in-bound phase value.
        for r in range(1<<n):
            for c in (0,1):
                q=r|(s<<n)|(c<<(2*n))
                for t in range(periods[s]+1):
                    expected=(r==s==t==0) or (s!=0 and r in tables[s] and tables[s][r]==t and c==t%2)
                    require(H(n,update,q,t,periods)==expected,"history phase relation wrong")
                    if not expected:
                        continue
                    h_states+=1
                    for u in range(1<<n):
                        q1,t1,bad=step(n,update,q,t,u,L)
                        require(not bad and H(n,update,q1,t1,periods),"history induction or safety failed")
                        edges+=1
    return len(periods),h_states,edges


def run():
    seed_checks=h_states=edges=0
    matrix_counts=[]
    for n in (1,2,3):
        mask=(1<<n)-1;count=0
        for packed in range(1<<(n*n)):
            def update(s):
                return sum(((((packed>>(i*n))&mask)&s).bit_count()%2)<<i for i in range(n))
            tables=orbit_tables(n,update)
            if tables is None or any(len(table)%2==0 for table in tables):
                continue
            order=lcm(*(len(table) for table in tables))
            count+=1
            for excess in (1,9,25):
                a,b,c=check_case(n,update,order*excess,tables)
                seed_checks+=a;h_states+=b;edges+=c
        matrix_counts.append({"bits":n,"odd_order_matrices":count})
    companion=[]
    for n,taps,M in ((3,4,9),(5,17,63),(8,184,255)):
        mask=(1<<n)-1
        def update(s):
            return ((s<<1)&mask)|((s&taps).bit_count()%2)
        tables=orbit_tables(n,update)
        periods=[selected_period(update,s,M,factor_integer(M)) for s in range(1<<n)]
        require(periods==[len(table) for table in tables],"companion selector wrong")
        expected_hist={3:{1:1,3:6},5:{3:3,7:7,21:21},8:{255:255}}[n]
        hist=dict(Counter(periods[1:]))
        require(hist==expected_hist,"planned control period distribution changed")
        companion.append({"bits":n,"taps":taps,"M":M,"nonzero_period_histogram":hist})
    # Width3 rotation: incorrect missing/reclassified factor data.
    n=3;M=9;L=4
    def rotation(s):return ((s<<1)&7)|(s>>2)
    wrong_one=[selected_period(rotation,s,M,[(3,1)]) for s in range(8)]
    require(wrong_one==[1]*8,"omission control was not constructed")
    q=1|(1<<n)  # genuinely seeded, c=0, t=0
    q1,t1,bad=step(n,rotation,q,0,0,L)
    require(H(n,rotation,q,0,wrong_one) and not bad,"omission source state not valid")
    require(not H(n,rotation,q1,t1,wrong_one),"omission did not break induction")
    wrong_nine=[selected_period(rotation,s,M,[(9,1)]) for s in range(8)]
    q=1|(1<<n)|(1<<(2*n));t=3
    require(H(n,rotation,q,t,wrong_nine),"composite control state absent")
    require(not step(n,rotation,q,t,0,L)[2],"composite control must not be immediately bad")
    states_before_failure=0
    for _ in range(3):
        q1,t1,bad=step(n,rotation,q,t,0,L)
        if bad:
            break
        require(H(n,rotation,q,t,wrong_nine),"composite pseudo-phase left H before bad")
        q,t=q1,t1;states_before_failure+=1
    require(bad and states_before_failure==2,"composite control lacked future bad trace")
    return {"matrix_counts":matrix_counts,"annihilator_multipliers":[1,9,25],
            "exact_seed_period_checks":seed_checks,"history_states_checked":h_states,
            "history_input_edges_checked":edges,"companion_controls":companion,
            "missing_repeated_prime_induction_failure":True,
            "composite_factor_future_bad_after_transitions":states_before_failure}


if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
