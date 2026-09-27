"""Small independent checker for the observed ASCII positive-hint LRAT subset.

Contract: the caller supplies a trusted DIMACS CNF separately from an untrusted
proof. Original clauses receive IDs 1..m in their serialized order. An addition
has ``id lits 0 positive_hints 0``; a deletion has ``id d live_ids 0``.
Addition IDs increase past all earlier line IDs. Deletion line IDs may repeat
the last ID, as in CaDiCaL output. Deleted clauses cannot be referenced again.
Binary LRAT, negative/RAT hints, tautological added clauses, extension records,
and unknown syntax are rejected. Rejection says nothing about satisfiability.

Soundness: assume the negation of each added clause. Hinted live clauses must
be satisfied, unit, or conflicting in their stated order; a conflicting clause
must be reached. Unit propagation is sound, so the database entails the added
clause. Inducting over additions preserves consequences of the original CNF.
Deletion only weakens the available database. Acceptance requires a checked
empty clause still present at the end (or an original empty clause). The full
proof is parsed even after a contradiction, and all hint IDs are checked.

This does not implement SAT search, RAT, a complete LRAT frontend, or proof
generation. It imports neither a solver nor the source/witness adapters. It
checks only CNF unsatisfiability: Certifaiger's model-to-obligation translation
and AIGER-to-CNF translation remain outside this checker. Python and this code
are trusted; no proof-assistant verification is claimed. Fixed byte, clause,
literal, variable, line and propagation-work caps bound accepted workloads.
"""
from dataclasses import dataclass
import gzip
from pathlib import Path
import re


class LratError(ValueError):
    """Malformed, unsupported, resource-limited, or invalid supplied proof."""


@dataclass(frozen=True)
class Limits:
    max_bytes: int = 64 * 1024 * 1024
    max_variables: int = 100_000
    max_clauses: int = 200_000
    max_literals: int = 4_000_000
    max_lines: int = 200_000
    max_work: int = 100_000_000


def require(condition, message):
    if not condition:
        raise LratError(message)


def integer(token):
    require(len(token) <= 11 and re.fullmatch(r"-?(0|[1-9][0-9]*)", token) is not None,
            "Invalid integer token")
    require(token != "-0", "Negative zero is unsupported")
    result = int(token)
    require(abs(result) <= 2_147_483_647, "Integer exceeds supported range")
    return result


def read_text(path, limits):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    try:
        with opener(path, "rb") as stream:
            raw = stream.read(limits.max_bytes + 1)
    except (OSError, EOFError) as exc:
        raise LratError("Cannot read proof input") from exc
    require(len(raw) <= limits.max_bytes, "File exceeds byte limit")
    try:
        return raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise LratError("Only ASCII text is supported") from exc


def parse_cnf(text, limits):
    header = None
    clauses = {}
    pending = []
    literal_count = 0
    for line in text.splitlines():
        fields = line.split()
        if not fields or fields[0] == "c":
            continue
        if header is None:
            require(len(fields) == 4 and fields[:2] == ["p", "cnf"], "Missing DIMACS header")
            n, m = map(integer, fields[2:])
            require(0 <= n <= limits.max_variables and 0 <= m <= limits.max_clauses,
                    "DIMACS dimensions exceed limits")
            header = n, m
            continue
        for field in fields:
            literal = integer(field)
            if literal:
                require(abs(literal) <= header[0], "CNF literal exceeds declared variables")
                pending.append(literal)
                literal_count += 1
                require(literal_count <= limits.max_literals, "CNF literal limit exceeded")
            else:
                clauses[len(clauses) + 1] = tuple(sorted(set(pending)))
                pending = []
                require(len(clauses) <= header[1], "Too many original clauses")
    require(header is not None and not pending, "Incomplete DIMACS input")
    require(len(clauses) == header[1], "DIMACS clause-count mismatch")
    return header[0], clauses, literal_count


def check_lrat_text(cnf_text, proof_text, *, limits=Limits()):
    for text in (cnf_text, proof_text):
        try:
            size = len(text.encode("ascii"))
        except UnicodeEncodeError as exc:
            raise LratError("Only ASCII text is supported") from exc
        require(size <= limits.max_bytes, "Text exceeds byte limit")
    n, database, total_literals = parse_cnf(cnf_text, limits)
    originals = len(database)
    cursor = originals
    additions = deletions = work = proof_lines = 0
    empty_id = next((i for i, clause in database.items() if not clause), None)

    def charge(amount):
        nonlocal work
        work += amount
        require(work <= limits.max_work, "Propagation-work limit exceeded")

    for line in proof_text.splitlines():
        fields = line.split()
        if not fields or fields[0] == "c":
            continue
        proof_lines += 1
        require(proof_lines <= limits.max_lines, "Proof line limit exceeded")
        require(len(fields) >= 3, "Truncated proof line")
        ident = integer(fields[0])
        if fields[1] == "d":
            require(ident >= cursor, "Deletion line ID moves backwards")
            deleted = list(map(integer, fields[2:]))
            require(deleted and deleted[-1] == 0 and all(i > 0 for i in deleted[:-1]),
                    "Malformed deletion record")
            for ref in deleted[:-1]:
                require(ref in database, "Deleting unavailable clause")
                del database[ref]
                deletions += 1
            cursor = ident
            continue
        require(ident > cursor and ident > originals, "Addition ID is not fresh and increasing")
        values = list(map(integer, fields[1:]))
        zeros = [i for i, value in enumerate(values) if value == 0]
        require(len(zeros) == 2 and zeros[-1] == len(values) - 1, "Malformed addition record")
        literals = values[:zeros[0]]
        hints = values[zeros[0]+1:-1]
        require(all(0 < abs(lit) <= n for lit in literals), "Proof literal exceeds original variables")
        require(all(ref > 0 for ref in hints), "RAT/negative hints are unsupported")
        require(all(ref in database for ref in hints), "Hint references unavailable clause")
        clause = tuple(sorted(set(literals)))
        clause_set = set(clause)
        require(all(-lit not in clause_set for lit in clause), "Tautological additions are unsupported")
        total_literals += len(literals)
        require(total_literals <= limits.max_literals, "Total literal limit exceeded")
        charge(len(literals) + len(hints))
        assignments = {abs(lit): lit < 0 for lit in clause}
        conflict = False
        for ref in hints:
            antecedent = database[ref]
            charge(len(antecedent))
            unassigned = []
            satisfied = False
            for lit in antecedent:
                value = assignments.get(abs(lit))
                if value is None:
                    unassigned.append(lit)
                elif value == (lit > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unassigned:
                conflict = True
                break
            require(len(unassigned) == 1, "Hint is neither unit nor conflicting")
            lit = unassigned[0]
            assignments[abs(lit)] = lit > 0
        require(conflict, "RUP hints do not derive a contradiction")
        additions += 1
        require(originals + additions <= limits.max_clauses, "Clause limit exceeded")
        database[ident] = clause
        cursor = ident
        if not clause:
            empty_id = ident
    require(empty_id in database and database[empty_id] == (), "No checked empty clause at proof end")
    return {"status": "verified_unsat", "variables": n, "original_clauses": originals,
            "added_clauses": additions, "deleted_clauses": deletions,
            "proof_lines": proof_lines, "empty_clause_id": empty_id, "literal_work": work}


def check_lrat(cnf_path, proof_path, *, limits=Limits()):
    return check_lrat_text(read_text(cnf_path, limits), read_text(proof_path, limits), limits=limits)


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cnf")
    parser.add_argument("proof")
    args = parser.parse_args()
    print(json.dumps(check_lrat(args.cnf, args.proof), sort_keys=True))
