# Invariant evaluation, inverse witnesses and history

This audit closes the remaining conceptual novelty route from the native
history-witness experiments. The forced original-state predicate is a concrete
instance of an established inverse-bit separator construction. Keeping its
inverse witness as history is a valid, conventional extension. The native
integration remains useful; a new general separation does not follow.

Read the [project decision](../INVARIANT_HISTORY_GATE_13.md), the precise
[theorem and boundaries](THEORY.md), and the [primary-source comparison](SOURCES.md).
The earlier [odd-order witness checkpoint](../odd_order_witness_v1/README.md)
retains the actual native executions and proof traces. This audit runs no new
native solver experiment and changes no earlier evidence.

The main distinctions are deterministic predicate evaluation versus a supplied
inverse witness; ordinary Boolean circuits versus restricted CNF; and actual
history state versus acyclic definitions of current-state signals. A short
existentially quantified representation over the original free variables is
already available. No unconditional circuit-size or general formula-size
lower bound is claimed.

From the repository root:

```sh
python -m research.invariant_history_v1.verify
```

The standard-library check independently enumerates finite permutations with
zero through five active elements. It compares graph reachability and backward
safety with the mathematical characterization, checks phase recovery and
history projection, and retains even-cycle counterexamples to the odd-cycle
premise. These checks concern the stated finite models, not asymptotic hardness
or historical priority. The root verifier also runs them.

The audit covers 154 permutations: 60 with only odd cycles and 94 with a
reachable even-cycle error. It checks 3,814 source states, 1,866 phase
recoveries, 1,053 history states and 6,128 history edges. A nonrecurrent-tail
control shows why recurrence matters; 52 output checks cover the padded total
permutation correspondence, including zero.

Further research needs an independently motivated consumer and a falsifiable
benefit over the strongest source-aware method. Another history encoding or a
larger synthetic example is not the next objective. Manuscript writing remains
on hold.
