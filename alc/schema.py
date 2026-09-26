"""Closed JSON data models and bounded input parsing; no algebraic search."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


class Invalid(ValueError):
    """Malformed input or a failed proof obligation; NOT unreachability."""


class ResourceLimit(ValueError):
    """A declared implementation limit was reached; no mathematical conclusion."""


@dataclass(frozen=True)
class Limits:
    max_bytes: int = 1_048_576
    max_dimension: int = 32
    max_integer_bits: int = 1024
    max_prime_records: int = 1024
    max_factors: int = 1024


DEFAULT_LIMITS = Limits()


def keys(value: Any, required: set[str], label: str) -> dict:
    if type(value) is not dict or set(value) != required:
        raise Invalid(f'{label}: expected exactly {sorted(required)}')
    return value


def integer(value: Any, label: str, low: int = 0,
            high: int | None = None, limits: Limits = DEFAULT_LIMITS) -> int:
    if type(value) is not int:  # bool and floating-point values are not integers here.
        raise Invalid(f'{label}: an exact JSON integer is required')
    if value.bit_length() > limits.max_integer_bits:
        raise ResourceLimit(f'{label}: integer bit limit exceeded')
    if value < low or (high is not None and value > high):
        raise Invalid(f'{label}: integer outside the allowed range')
    return value


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path: str | Path, limits: Limits = DEFAULT_LIMITS) -> dict:
    """Read at most max_bytes+1; reject duplicate keys, nonfinite and deep JSON."""
    def pairs(items):
        obj = {}
        for k, v in items:
            if k in obj:
                raise Invalid('duplicate JSON key: ' + k)
            obj[k] = v
        return obj
    def bad_constant(text):
        raise Invalid('nonfinite JSON number: ' + text)
    with Path(path).open('rb') as stream:
        raw = stream.read(limits.max_bytes + 1)
    if len(raw) > limits.max_bytes:
        raise ResourceLimit('JSON byte limit exceeded')
    try:
        obj = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                         parse_constant=bad_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Invalid('invalid UTF-8 or JSON document') from exc
    except ValueError as exc:
        if isinstance(exc, Invalid):
            raise
        raise Invalid('invalid or oversized JSON number') from exc
    if type(obj) is not dict:
        raise Invalid('top-level JSON object required')
    return obj


def dump_new(path: str | Path, obj: Any) -> None:
    """Exclusive creation: never replace a certificate or evidence file."""
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def vector(value: Any, n: int, p: int, label: str, limits: Limits) -> tuple[int, ...]:
    if type(value) is not list or len(value) != n:
        raise Invalid(f'{label}: expected {n} entries')
    return tuple(integer(x, label, 0, p-1, limits) for x in value)


def matrix(value: Any, n: int, p: int, label: str, limits: Limits) -> tuple[tuple[int, ...], ...]:
    if type(value) is not list or len(value) != n:
        raise Invalid(f'{label}: expected {n} rows')
    return tuple(vector(row, n, p, label, limits) for row in value)


@dataclass(frozen=True)
class Problem:
    """x_(t+1)=A*x_t+c over the prime field F_p; t starts at zero."""
    p: int
    A: tuple[tuple[int, ...], ...]
    c: tuple[int, ...]
    initial: tuple[int, ...]
    target: tuple[int, ...]

    @classmethod
    def parse(cls, obj: dict, limits: Limits = DEFAULT_LIMITS) -> 'Problem':
        keys(obj, {'schema', 'field', 'matrix', 'offset', 'initial', 'target'}, 'problem')
        if obj['schema'] != 'alc.problem.v1':
            raise Invalid('unknown problem schema')
        fld = keys(obj['field'], {'kind', 'modulus'}, 'field')
        if fld['kind'] != 'prime':
            raise Invalid('v1 supports prime fields only, not extension fields or overflow rings')
        p = integer(fld['modulus'], 'modulus', 2, limits=limits)
        if type(obj['matrix']) is not list or not obj['matrix']:
            raise Invalid('nonempty square matrix required')
        n = len(obj['matrix'])
        if n > limits.max_dimension:
            raise ResourceLimit('dimension limit exceeded')
        return cls(p, matrix(obj['matrix'], n, p, 'matrix', limits),
                   vector(obj['offset'], n, p, 'offset', limits),
                   vector(obj['initial'], n, p, 'initial', limits),
                   vector(obj['target'], n, p, 'target', limits))

    def as_dict(self) -> dict:
        return {'schema': 'alc.problem.v1', 'field': {'kind': 'prime', 'modulus': self.p},
                'matrix': [list(row) for row in self.A], 'offset': list(self.c),
                'initial': list(self.initial), 'target': list(self.target)}

    @property
    def fingerprint(self) -> str:
        return digest(self.as_dict())
