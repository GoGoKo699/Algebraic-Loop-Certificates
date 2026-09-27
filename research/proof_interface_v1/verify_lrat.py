"""Finite soundness controls for the strict positive-hint LRAT replay checker."""
from dataclasses import replace
from itertools import product
import gzip
import json
from pathlib import Path
import tempfile

from .lrat import Limits, LratError, check_lrat, check_lrat_text


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_controls():
    cnf = "p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n"
    proof = "5 2 0 1 2 0\n5 d 1 2 0\n6 0 5 3 4 0\n"
    result = check_lrat_text(cnf, proof)
    require(result["status"] == "verified_unsat" and result["deleted_clauses"] == 2,
            "Valid derivation/deletion was not replayed")
    clauses = [(1, 2), (-1, 2), (1, -2), (-1, -2)]
    def satisfies(bits, formula):
        return all(any(bits[abs(lit)-1] == (lit > 0) for lit in clause) for clause in formula)
    require(not any(satisfies(bits, clauses) for bits in product((False, True), repeat=2)),
            "Independent Boolean truth table disagrees")
    invalid = {
        "missing_final_empty": "5 2 0 1 2 0\n",
        "invented_hint": "5 0 999 0\n",
        "nonunit_hint": "5 0 1 2 0\n",
        "negative_rat_hint": "5 2 0 -1 2 0\n",
        "missing_zero": "5 2 0 1 2\n",
        "extra_zero": "5 2 0 1 2 0 0\n",
        "future_variable": "5 3 0 1 2 0\n",
        "original_id_reuse": "4 2 0 1 2 0\n",
        "addition_id_reuse": "5 2 0 1 2 0\n5 0 5 3 4 0\n",
        "deleted_hint": "4 d 1 0\n5 2 0 1 2 0\n",
        "unknown_deletion": "4 d 99 0\n",
        "double_deletion": "4 d 1 1 0\n",
        "backward_deletion": "3 d 1 0\n",
        "deleted_empty": proof + "6 d 6 0\n",
        "unparsed_trailer": proof + "unknown\n",
        "tautological_addition": "5 1 -1 0 1 0\n",
        "no_hints": "5 0 0\n",
        "binary_dialect": "a\x80\x00",
    }
    rejected = 0
    for name, candidate in invalid.items():
        try:
            check_lrat_text(cnf, candidate)
        except LratError:
            rejected += 1
        else:
            raise ValueError(f"Accepted invalid/unsupported control: {name}")
    # Removing any one of the four clauses makes the CNF satisfiable. Renumber
    # original clauses in each serialized input; a fabricated empty-clause
    # chain must be rejected, regardless of which satisfying state exists.
    falseproofs = 0
    for removed in range(4):
        remaining = clauses[:removed] + clauses[removed+1:]
        require(any([satisfies(bits, remaining) for bits in product((False, True), repeat=2)]),
                "Expected satisfiable independent control")
        sat_cnf = "p cnf 2 3\n" + "".join(" ".join(map(str, c)) + " 0\n" for c in remaining)
        try:
            check_lrat_text(sat_cnf, "4 0 1 2 3 0\n")
        except LratError:
            falseproofs += 1
        else:
            raise ValueError("Accepted fabricated UNSAT proof of satisfiable formula")
    malformed_cnfs = [
        "p cnf 2 3\n1 0\n", "p cnf 1 1\n2 0\n",
        "p cnf 1 1\n1\n", "p cnf 1 0\n1 0\n",
        "p cnf 1 1\np cnf 1 1\n1 0\n", "p cnf 1 1\n-0\n",
    ]
    for malformed in malformed_cnfs:
        try:
            check_lrat_text(malformed, "")
        except LratError:
            rejected += 1
        else:
            raise ValueError("Accepted malformed DIMACS input")
    for limits in (replace(Limits(), max_bytes=10), replace(Limits(), max_work=1),
                   replace(Limits(), max_lines=1), replace(Limits(), max_variables=1),
                   replace(Limits(), max_clauses=4), replace(Limits(), max_literals=1)):
        try:
            check_lrat_text(cnf, proof, limits=limits)
        except LratError:
            rejected += 1
        else:
            raise ValueError("Resource cap was not enforced")
    require(check_lrat_text("p cnf 0 1\n0\n", "")["status"] == "verified_unsat",
            "Original empty clause should establish UNSAT directly")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        formula = root / "input.cnf"
        compressed = root / "proof.lrat.gz"
        formula.write_text(cnf)
        compressed.write_bytes(gzip.compress(proof.encode("ascii"), mtime=0))
        require(check_lrat(formula, compressed)["status"] == "verified_unsat",
                "Compressed proof replay differs")
        compressed.write_bytes(gzip.compress((proof + "\n" * 1000).encode("ascii"), mtime=0))
        try:
            check_lrat(formula, compressed, limits=replace(Limits(), max_bytes=100))
        except LratError:
            rejected += 1
        else:
            raise ValueError("Decompressed-byte cap was not enforced")
        compressed.write_bytes(b"not a gzip stream")
        try:
            check_lrat(formula, compressed)
        except LratError:
            rejected += 1
        else:
            raise ValueError("Malformed gzip stream was accepted")
    return {"valid_derivations": 3, "invalid_or_unsupported_rejected": rejected,
            "satisfiable_formula_falseproofs_rejected": falseproofs,
            "independent_truth_table_assignments": 20}


if __name__ == "__main__":
    print(json.dumps(verify_controls(), sort_keys=True))
