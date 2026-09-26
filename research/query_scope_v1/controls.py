"""Independent reductions and observation checks for a query-scope audit.

This is diagnostic/reduction code, not a new certificate format or a production
partial-observation solver. Sparse bit vectors below are explicit GF(2) vectors.
No source table or hidden oracle is used by the universal clock construction.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from math import isqrt, prod


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def odd_primes(n: int) -> tuple[int, ...]:
    if type(n) is not int or n < 1:
        raise ValueError('At least one variable required.')
    out: list[int] = []
    q = 3
    while len(out) < n:
        if all(q % j for j in range(2, isqrt(q)+1)):
            out.append(q)
        q += 2
    return tuple(out)


def crt_coprime(moduli: tuple[int, ...], residues: tuple[int, ...]) -> int:
    if len(moduli) != len(residues):
        raise ValueError('One residue per modulus required.')
    out, scale = 0, 1
    for p, r in zip(moduli, residues):
        out += scale * ((r-out) * pow(scale, -1, p) % p)
        scale *= p
    return out


@dataclass(frozen=True)
class Block:
    variables: tuple[int, ...]
    period: int
    offset: int


@dataclass(frozen=True)
class ClockSource:
    """A source depending only on n, not on any later CNF formula.

    One cyclic-permutation block for each nonempty subset of <=3 variables.
    One extra fixed-zero coordinate provides a canonical inconsistent target.
    A fixed involution S replaces singleton coordinate 0 by x_0+x_1. Dynamics
    are S P S^{-1}; guard queries then fix individual coordinates, not sums.
    The object is an explicit sparse representation of a binary matrix.
    """
    primes: tuple[int, ...]
    blocks: tuple[Block, ...]
    dimension: int

    @classmethod
    def build(cls, n: int) -> 'ClockSource':
        ps = odd_primes(n)
        blocks: list[Block] = []
        offset = 0
        for arity in range(1, min(3, n)+1):
            for variables in combinations(range(n), arity):
                length = prod(ps[i] for i in variables)
                blocks.append(Block(variables, length, offset))
                offset += length
        return cls(ps, tuple(blocks), offset+1)

    @property
    def period(self) -> int:
        return prod(self.primes)

    @property
    def dummy(self) -> int:
        return self.dimension-1

    def valid_vector(self, state: int) -> int:
        if type(state) is not int or not 0 <= state < (1 << self.dimension):
            raise ValueError('Packed binary vector out of range.')
        return state

    def conjugate(self, state: int) -> int:
        self.valid_vector(state)
        for block in self.blocks:
            if len(block.variables) == 1 and (state >> (block.offset+1)) & 1:
                state ^= 1 << block.offset
        return state

    def at(self, time: int) -> int:
        if type(time) is not int or time < 0:
            raise ValueError('Nonnegative time required.')
        raw = sum(1 << (b.offset + time % b.period) for b in self.blocks)
        return self.conjugate(raw)

    def step(self, state: int, reverse: bool = False) -> int:
        raw = self.conjugate(state)
        out = raw & (1 << self.dummy)
        for b in self.blocks:
            mask = (1 << b.period)-1
            part = (raw >> b.offset) & mask
            if reverse:
                part = (part >> 1) | ((part & 1) << (b.period-1))
            else:
                part = ((part << 1) & mask) | (part >> (b.period-1))
            out |= part << b.offset
        return self.conjugate(out)

    def point_member(self, state: int) -> bool:
        """Ordinary source-aware point test: one-hot blocks and CRT consistency.

        Polynomial in this explicit representation size; no finite-field logs.
        This is a classical comparator specific to the constructed easy sources.
        """
        raw = self.conjugate(state)
        if raw & (1 << self.dummy):
            return False
        residues: dict[int, int] = {}
        for b in self.blocks:
            bits = (raw >> b.offset) & ((1 << b.period)-1)
            if not bits or bits & (bits-1):
                return False
            pos = bits.bit_length()-1
            if len(b.variables) == 1:
                residues[b.variables[0]] = pos
            elif any(pos % self.primes[i] != residues[i] for i in b.variables):
                return False
        return True

    def matrix_source(self) -> dict:
        """Materialize the explicit dense matrix for deliberately small controls."""
        columns = [self.step(1 << j) for j in range(self.dimension)]
        return {'schema': 'alc.orbit-source.v1',
                'field': {'kind': 'prime', 'modulus': 2},
                'matrix': [[(columns[j] >> i) & 1 for j in range(self.dimension)]
                           for i in range(self.dimension)],
                'offset': [0]*self.dimension,
                'initial': [(self.at(0) >> i) & 1 for i in range(self.dimension)]}

    def summary(self) -> dict:
        return {'variables': len(self.primes), 'primes': list(self.primes),
                'dimension': self.dimension, 'point_period': self.period,
                'blocks': [{'variables': list(b.variables), 'period': b.period,
                            'offset': b.offset} for b in self.blocks],
                'conjugation': 'singleton coordinate 0 := x_0 XOR x_1; other coordinates unchanged',
                'dummy_coordinate': self.dummy}


def normalize_clause(clause, n: int) -> tuple[int, ...] | None:
    """None means tautology; () means the false empty clause."""
    if not isinstance(clause, (tuple, list)) or len(clause) > 3:
        raise ValueError('At most three literals per clause required.')
    if any(type(v) is not int or not 1 <= abs(v) <= n for v in clause):
        raise ValueError('Nonzero literal in variable range required.')
    values = set(clause)
    if any(-v in values for v in values):
        return None
    return tuple(sorted(values, key=abs))


def guard_for(source: ClockSource, clauses) -> tuple[tuple[int, int], ...]:
    """Polynomial reduction from <=3-CNF to a PARTIAL COORDINATE TARGET.

    The source never changes. Clauses change only these selected bit values.
    The output contains no CNF evaluator or existentially chosen auxiliary bits.
    """
    n = len(source.primes)
    lookup = {b.variables: b for b in source.blocks}
    constraints = {lookup[(i,)].offset: 1 for i in range(n)}
    for clause in clauses:
        normalized = normalize_clause(clause, n)
        if normalized is None:
            continue
        if not normalized:
            return ((source.dummy, 1),)
        if len(normalized) == 1:
            literal = normalized[0]
            index = lookup[(abs(literal)-1,)].offset+1
            value = int(literal > 0)
        else:
            variables = tuple(abs(v)-1 for v in normalized)
            bad_residues = tuple(int(v < 0) for v in normalized)
            bad_time = crt_coprime(tuple(source.primes[i] for i in variables), bad_residues)
            index, value = lookup[variables].offset+bad_time, 0
        if index in constraints and constraints[index] != value:
            return ((source.dummy, 1),)
        constraints[index] = value
    return tuple(sorted(constraints.items()))


def guard_holds(state: int, guard: tuple[tuple[int, int], ...]) -> bool:
    return all((state >> index) & 1 == bit for index, bit in guard)


def formula_holds(assignment: tuple[int, ...], clauses) -> bool:
    return all(any(bool(assignment[abs(v)-1]) == (v > 0) for v in clause)
               for clause in clauses)


def closed_observation(A, L, p):
    """Return B with L A = B L, or None if observations do not evolve autonomously.

    L must have independent rows. This diagnostic uses existing exact solving;
    it does not add a certificate schema or treat None as unreachability.
    """
    from research.complete_orbits_v1 import algebra as alg
    k, d = len(L), len(A)
    if not 1 <= k <= d or any(len(row) != d for row in L):
        raise ValueError('A full-row-rank observation matrix is required.')
    columns = tuple(zip(*L))
    if any(alg.solve_columns(columns, tuple(int(i == j) for i in range(k)), p) is None
           for j in range(k)):
        raise ValueError('Dependent observation rows.')
    rows = [tuple(sum(L[i][t]*A[t][j] for t in range(d)) % p for j in range(d))
            for i in range(k)]
    B = tuple(alg.solve_columns(L, row, p) for row in rows)
    if any(row is None for row in B):
        return None
    return B
