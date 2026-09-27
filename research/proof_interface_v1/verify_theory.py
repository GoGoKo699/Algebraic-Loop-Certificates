"""Independent exhaustive small controls for THEORY.md; no AAG checker imports."""

from collections import deque
import json


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def make_step(n, update):
    mask = (1 << n) - 1
    def step(state, u):
        r, s, c = state & mask, (state >> n) & mask, state >> (2*n)
        ar = update(r)
        match = s != 0 and ar == s
        bad = bool((u == 0 and c and match) or (s != 0 and ar == 0))
        if u:
            return u | (u << n), bad
        return ar | (s << n) | (int(not c and not match) << (2*n)), bad
    return step


def orbit_data(n, update):
    size = 1 << n
    images = [update(r) for r in range(size)]
    if len(set(images)) != size:
        return None
    result = {}
    for s in range(size):
        phase, r = {}, s
        while r not in phase:
            phase[r] = len(phase)
            r = update(r)
        require(r == s, "permutation orbit did not close")
        result[s] = phase
    return result


def reach_and_safe(n, step):
    """Forward reachability and independently backward universal safety."""
    states, inputs = 1 << (2*n+1), 1 << n
    edges = [[step(q,u) for u in range(inputs)] for q in range(states)]
    reach, todo = {0}, deque([0])
    while todo:
        q = todo.popleft()
        for nxt, _ in edges[q]:
            if nxt not in reach:
                reach.add(nxt); todo.append(nxt)
    reverse = [[] for _ in range(states)]
    unsafe = set()
    for q in range(states):
        for nxt, bad in edges[q]:
            reverse[nxt].append(q)
            if bad:
                unsafe.add(q)
    todo = deque(unsafe)
    while todo:
        q = todo.popleft()
        for pred in reverse[q]:
            if pred not in unsafe:
                unsafe.add(pred); todo.append(pred)
    return reach, set(range(states)) - unsafe


def predicted_sets(n, phases):
    mask = (1 << n) - 1
    reach, safe = set(), set()
    for q in range(1 << (2*n+1)):
        r, s, c = q & mask, (q >> n) & mask, q >> (2*n)
        if s == 0:
            safe.add(q)
            if r == 0:
                reach.add(q)
        elif r != 0:
            if r not in phases[s]:
                safe.add(q)
            elif c == phases[s][r] % 2:
                safe.add(q); reach.add(q)
    return reach, safe


def advance(n, update, vector, exponent):
    """Independent column-matrix fast powering for shifted oracle queries."""
    columns = [update(1 << i) for i in range(n)]
    def apply(values, v):
        out=0
        for i in range(n):
            if v >> i & 1:
                out ^= values[i]
        return out
    while exponent:
        if exponent & 1:
            vector=apply(columns,vector)
        columns=[apply(columns,v) for v in columns]
        exponent >>= 1
    return vector


def run():
    matrix_counts = []
    singular_controls = 0
    for n in (1,2,3):
        mask = (1 << n)-1
        odd_count = 0
        for mat in range(1 << (n*n)):
            def update(r):
                return sum(((((mat >> (i*n)) & mask) & r).bit_count() % 2) << i for i in range(n))
            phases = orbit_data(n,update)
            if phases is None:
                seed = next(s for s in range(1,1 << n) if update(s) == 0)
                step = make_step(n,update)
                seeded, initial_bad = step(0,seed)
                require(not initial_bad and step(seeded,0)[1], "singular kernel control did not fail")
                singular_controls += 1
                continue
            if any(len(p) % 2 == 0 for p in phases.values()):
                continue
            got = reach_and_safe(n,make_step(n,update))
            require(got == predicted_sets(n,phases), "exact set characterization failed")
            odd_count += 1
        matrix_counts.append({"bits":n,"odd_order_matrices":odd_count})
    primitive = []
    dlp_pairs = extended_state_checks = extended_edges = 0
    for n,taps in ((2,3),(3,6),(4,12)):
        size, M = 1 << n, (1 << n)-1
        def update(r):
            return ((r << 1) & M) | ((r & taps).bit_count() % 2)
        phases = orbit_data(n,update)
        require(all(len(phases[s]) == M for s in range(1,size)), "test map not primitive")
        step = make_step(n,update)
        reach,safe = reach_and_safe(n,step)
        require((reach,safe) == predicted_sets(n,phases), "primitive set characterization failed")
        def powered(s,t):
            for _ in range(t):
                s=update(s)
            return s
        def H(q,t):
            r,s,c=q&M,(q>>n)&M,q>>(2*n)
            return (r == s == t == 0) or (s != 0 and t < M and r == powered(s,t) and c == t%2)
        def extended_step(q,t,u):
            r,s=q&M,(q>>n)&M
            m = s != 0 and update(r) == s
            new_t = 0 if u != 0 or s == 0 or m else (t+1) % size
            q1,bad=step(q,u)
            return q1,new_t,bad
        require(H(0,0), "history initiation")
        for q in range(1<<(2*n+1)):
            r,s,c=q&M,(q>>n)&M,q>>(2*n)
            for t in range(size):
                expected=(r==s==t==0) or (s!=0 and r!=0 and t==phases[s][r] and c==t%2)
                require(H(q,t)==expected,"history predicate includes wrong phase")
                extended_state_checks += 1
                if H(q,t):
                    for u in range(size):
                        q1,t1,bad=extended_step(q,t,u)
                        require(not bad and H(q1,t1),"history induction or safety failed")
                        extended_edges += 1
        for s in range(1,size):
            for r in range(1,size):
                base_parity=0 if (r | (s<<n)) in reach else 1
                lower,upper=0,M
                while upper-lower>1:
                    threshold=(lower+upper)//2
                    k=M-threshold
                    shifted=advance(n,update,r,k)
                    shifted_parity=0 if (shifted | (s<<n)) in reach else 1
                    at_least=shifted_parity ^ base_parity ^ (k%2)
                    require(at_least == (phases[s][r]>=threshold),"phase-wrap comparison failed")
                    if at_least:lower=threshold
                    else:upper=threshold
                require(lower==phases[s][r],"exact parity-to-DLP reduction failed")
                dlp_pairs += 1
        primitive.append({"bits":n,"reachable_states":len(reach),"universally_safe_states":len(safe)})
    # Weak ghost contract counterexample: A=I,M=3,t=1,r=s=1,c=1.
    n=2;r=s=t=c=1;odd_multiple=3
    q=r|(s<<n)|(c<<(2*n))
    require(t<odd_multiple and r==s and c==t%2, "weak predicate not satisfied")
    require(make_step(n,lambda x:x)(q,0)[1], "weak odd-multiple witness did not fail")
    return {"odd_matrix_exact_sets":matrix_counts,"singular_kernel_controls":singular_controls,
            "primitive_exact_sets":primitive,"discrete_log_pairs":dlp_pairs,
            "extended_state_checks":extended_state_checks,"extended_invariant_edges":extended_edges,
            "odd_multiple_ghost_counterexample":True}


if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
