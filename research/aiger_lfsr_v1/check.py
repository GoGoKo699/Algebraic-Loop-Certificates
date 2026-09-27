"""Exact, fail-closed checker for the documented reseeding/period AAG wrapper.

No producer, orbit enumeration, factorization, solver, or external service.
Boolean DAG rewriting uses identities only; failure to recognize is inconclusive.
"""

from dataclasses import dataclass


class Rejected(ValueError):
    pass


class BooleanDag:
    """Interned node IDs avoid exponentially recursive tuple hashes.

    Literal 2*k refers to node k; its complement is 2*k+1. Every stored
    node key contains only integer IDs, never recursive Python expressions.
    A deterministic work budget also bounds flattening of large conjunctions.
    """

    def __init__(self):
        self.nodes = [("const", ())]
        self.ids = {self.nodes[0]: 0}
        self.work = 0

    def tick(self, count=1):
        self.work += count
        if self.work > 2_000_000:
            raise Rejected("Boolean normalization work limit")

    def node(self, kind, children):
        key = (kind, children)
        if key not in self.ids:
            self.ids[key] = 2 * len(self.nodes)
            self.nodes.append(key)
        return self.ids[key]

    def var(self, name):
        return self.node("var", name)

    @staticmethod
    def neg(x):
        return x ^ 1

    def xor(self, *args):
        parity, terms, stack = 0, set(), list(args)
        while stack:
            self.tick()
            lit = stack.pop(); parity ^= lit & 1; x = lit & ~1
            if x == 0:
                continue
            kind, children = self.nodes[x // 2]
            if kind == "xor":
                self.tick(len(children)); stack.extend(children)
            elif x in terms:
                terms.remove(x)
            else:
                terms.add(x)
        if not terms:
            return parity
        if len(terms) == 1:
            return next(iter(terms)) ^ parity
        return self.node("xor", tuple(sorted(terms))) ^ parity

    def conj(self, *args):
        terms, stack = set(), list(args)
        while stack:
            self.tick()
            x = stack.pop()
            if x == 0:
                return 0
            if x == 1:
                continue
            kind, children = self.nodes[x // 2]
            if kind == "and" and not x & 1:
                self.tick(len(children)); stack.extend(children)
            elif x ^ 1 in terms:
                return 0
            else:
                terms.add(x)
        if not terms:
            return 1
        if len(terms) == 1:
            return next(iter(terms))
        # !(a & b) & !(!a & !b) == a XOR b.
        if len(terms) == 2:
            a, b = sorted(terms)
            ka, ca = self.nodes[a // 2]; kb, cb = self.nodes[b // 2]
            if (a & 1 and b & 1 and ka == kb == "and" and
                    len(ca) == len(cb) == 2 and {x ^ 1 for x in ca} == set(cb)):
                return self.xor(*ca)
        return self.node("and", tuple(sorted(terms)))

    def disj(self, *args):
        return self.conj(*(x ^ 1 for x in args)) ^ 1


@dataclass(frozen=True)
class Aag:
    n: int
    inputs: tuple
    latches: tuple
    output: int
    gates: tuple


def parse(raw):
    if not isinstance(raw, bytes) or len(raw) > 100_000:
        raise Rejected("input must be at most 100000 bytes")
    try:
        lines = raw.decode("ascii").splitlines()
        header = lines[0].split()
        if len(header) != 6 or header[0] != "aag":
            raise Rejected("only the six-token ASCII AIGER header is supported")
        def numbers(line, lengths):
            pieces = line.split()
            if len(pieces) not in lengths or any(not s.isdigit() for s in pieces):
                raise Rejected("invalid integer record")
            return tuple(map(int, pieces))
        m, n, l, o, a = numbers(" ".join(header[1:]), {5})
        if not 2 <= n <= 64 or l != 2 * n + 1 or o != 1 or m != n + l + a or a > 5000:
            raise Rejected("unsupported wrapper dimensions")
        pos = 1
        inputs = []
        for i in range(n):
            v, = numbers(lines[pos], {1}); pos += 1
            if v != 2 * (i + 1):
                raise Rejected("noncanonical input literals")
            inputs.append(v)
        latches = []
        for i in range(l):
            v = numbers(lines[pos], {2, 3}); pos += 1
            if v[0] != 2 * (n + i + 1) or (len(v) == 3 and v[2] != 0):
                raise Rejected("latches must be consecutive and zero initialized")
            if v[1] > 2 * m + 1:
                raise Rejected("invalid next-state literal")
            latches.append(v[:2])
        output, = numbers(lines[pos], {1}); pos += 1
        if output > 2 * m + 1:
            raise Rejected("invalid output literal")
        gates = []
        for i in range(a):
            lhs, r0, r1 = numbers(lines[pos], {3}); pos += 1
            if lhs != 2 * (n + l + i + 1) or r0 >= lhs or r1 >= lhs:
                raise Rejected("gate numbering, literal, or acyclicity violation")
            gates.append((lhs, r0, r1))
        # Metadata has no semantics. Reject non-symbol records before comments.
        seen = set()
        while pos < len(lines) and lines[pos] != "c":
            rec = lines[pos].split(maxsplit=1); pos += 1
            if len(rec) != 2 or len(rec[0]) < 2 or not rec[0][1:].isdigit():
                raise Rejected("invalid symbol table")
            kind, idx = rec[0][0], int(rec[0][1:])
            limit = {"i": n, "l": l, "o": o}.get(kind)
            if limit is None or idx >= limit or (kind, idx) in seen:
                raise Rejected("invalid or duplicate symbol")
            seen.add((kind, idx))
        return Aag(n, tuple(inputs), tuple(latches), output, tuple(gates))
    except (UnicodeError, IndexError, ValueError) as exc:
        if isinstance(exc, Rejected):
            raise
        raise Rejected("malformed AAG") from exc


def replay(aag, taps):
    n = aag.n
    if type(taps) is not int or not 0 < taps < 1 << n:
        raise Rejected("invalid tap mask")
    dag = BooleanDag()
    neg, xor, conj, disj = dag.neg, dag.xor, dag.conj, dag.disj
    u = tuple(dag.var(f"u{i:02}") for i in range(n))
    r = tuple(dag.var(f"r{i:02}") for i in range(n))
    s = tuple(dag.var(f"s{i:02}") for i in range(n))
    c = dag.var("c")
    nodes = {0: 0}
    nodes.update(zip(aag.inputs, u))
    nodes.update((lhs, value) for (lhs, _), value in zip(aag.latches, r + s + (c,)))
    def literal(k):
        value = nodes[k & ~1]
        return neg(value) if k & 1 else value
    for lhs, r0, r1 in aag.gates:
        nodes[lhs] = conj(literal(r0), literal(r1))
    ar = (xor(*(r[i] for i in range(n) if taps >> i & 1)),) + r[:-1]
    z = conj(*(neg(x) for x in u))
    nonzero_s = neg(conj(*(neg(x) for x in s)))
    match = conj(nonzero_s, *(neg(xor(x, y)) for x, y in zip(ar, s)))
    expected_r = tuple(disj(conj(z, a), conj(neg(z), b)) for a, b in zip(ar, u))
    expected_s = tuple(disj(conj(z, a), conj(neg(z), b)) for a, b in zip(s, u))
    expected_c = conj(neg(c), z, neg(match))
    expected_bad = disj(conj(z, c, match), conj(nonzero_s, *(neg(x) for x in ar)))
    if tuple(literal(rhs) for _, rhs in aag.latches) != expected_r + expected_s + (expected_c,):
        raise Rejected("next-state wrapper did not match")
    if literal(aag.output) != expected_bad:
        raise Rejected("bad-state detector did not match")


def compose(a, b):
    """Row bit masks for the GF(2) matrix product a*b."""
    rows = []
    for mask in a:
        row = 0
        while mask:
            low = mask & -mask
            row ^= b[low.bit_length() - 1]
            mask ^= low
        rows.append(row)
    return tuple(rows)


def power(a, exponent):
    result = tuple(1 << i for i in range(len(a)))
    while exponent:
        if exponent & 1:
            result = compose(result, a)
        a = compose(a, a)
        exponent >>= 1
    return result


def check(raw, taps, odd_exponent):
    """Accept only if raw circuit matches wrapper and A^odd_exponent = I.

    The circuit bytes are the independently trusted problem; taps/exponent are
    untrusted certificate fields. A rejection is not an unsafe verdict.
    """
    if type(odd_exponent) is not int or not 0 < odd_exponent < 1 << 4096 or not odd_exponent & 1:
        raise Rejected("a positive odd exponent of at most 4096 bits is required")
    aag = parse(raw)
    replay(aag, taps)
    matrix = (taps,) + tuple(1 << (i - 1) for i in range(1, aag.n))
    if power(matrix, odd_exponent) != tuple(1 << i for i in range(aag.n)):
        raise Rejected("odd exponent does not annihilate the matrix")
    return {"accepted": True, "bits": aag.n, "odd_exponent": odd_exponent}
