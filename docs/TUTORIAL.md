# From safety invariants to checked algebraic witnesses

This tutorial connects the safety and history-variable viewpoint of
Manna and Pnueli's *Temporal Verification of Reactive Systems: Safety* (1995)
to the concrete construction in this repository. Start with the
[learning path](LEARNING_PATH.md) for the book reference and reading guidance.
The exposition below is original and based on this repository's models and
proofs. The book's full chapter text was not inspected for this guide.

The goal is to understand how a statement about **every possible execution**
becomes a finite candidate witness that an existing checker can examine.
You need binary vectors, matrix multiplication, prime factorization, and proof
by induction. Over the binary field, addition of bits is XOR.

## 1. Prove all executions by checking one step

A transition system has a state $q$, an initial condition, and an update
$q'=F(q,u)$ controlled by an input $u$. A prime marks the next state.
The environment may choose a different input at every step.

Our safety question is whether a Boolean detector $\operatorname{bad}(q,u)$
can ever be true. It is evaluated on the current state and input, **before**
the transition. One finite execution prefix can refute safety; observing many
safe prefixes cannot establish it for every future input sequence.

An *inductive invariant* $I$ solves this by meeting three obligations:

| Obligation | What to show |
|---|---|
| Initiation | Every initial state satisfies $I$ |
| Preservation | If $I(q)$ holds, then $I(F(q,u))$ holds for every input $u$ |
| Safety | If $I(q)$ holds, then $\operatorname{bad}(q,u)$ is false for every input $u$ |

Induction then puts every reachable state inside $I$, so no execution reaches
a bad evaluation. The invariant may also contain unreachable states, but they
must satisfy preservation and safety too. This last requirement explains why
a convenient but overly generous phase bound can fail below.

## 2. The exact circuit being explained

Let $A$ be an $n$-by-$n$ binary matrix. The original state is $q=(r,s,c)$:

| Symbol | Meaning |
|---|---|
| $r\in\mathbb F_2^n$ | The advancing register |
| $s\in\mathbb F_2^n$ | A saved seed |
| $c\in\{0,1\}$ | A parity bit |
| $u\in\mathbb F_2^n$ | The current unrestricted input |

A zero input advances the register. Any nonzero input reseeds both registers.
Define the imminent-return flag

$$
m=[s\ne0\ \land\ Ar=s].
$$

Here square brackets denote the truth value of a condition. The full update is

$$
r'=\begin{cases}Ar,&u=0,\\u,&u\ne0,\end{cases}
\qquad
s'=\begin{cases}s,&u=0,\\u,&u\ne0,\end{cases}
$$

$$
c'=\begin{cases}1-c,&u=0\ \land\ \neg m,\\0,&\text{otherwise}.\end{cases}
$$

The initial state is $(r,s,c)=(0,0,0)$. The detector is

$$
\operatorname{bad}(q,u)=
\bigl((u=0)\land(c=1)\land m\bigr)
\;\lor\;
\bigl((s\ne0)\land(Ar=0)\bigr).
$$

The second clause is **not gated by the input**. Reseeding does not switch it
off for the current evaluation. Likewise, resetting $c'$ cannot repair a bad
evaluation involving the old $c$. These details belong to the source property,
so a certificate must preserve them.

With zero registers and zero inputs, $c$ toggles even though the registers stay
zero. A correct invariant must therefore allow both parity values in that idle
state. The [full transition-system proof](../research/proof_interface_v1/THEORY.md)
also describes the reachable and universally safe sets precisely.

## 3. The algebraic premise gives odd cycles

Assume a supplied odd positive integer $M$ satisfies $A^M=I_n$, where $I_n$ is
the identity matrix. Consequently $A$ is invertible, with inverse $A^{M-1}$.
In particular, applying $A$ to a nonzero vector cannot produce zero.

For each seed $s$, let $T_s$ be its least positive return time:

$$
A^{T_s}s=s.
$$

Since $A^M s=s$, the least period $T_s$ divides $M$. One way to see this is to
divide $M$ by $T_s$: a nonzero remainder would be an earlier positive return.
Every seed period is therefore odd. The zero seed has $T_0=1$.

Odd periods are exactly what the parity monitor needs. Starting at a nonzero
seed with $c=0$, the imminent return comes after $T_s-1$ ordinary advances.
That number is even, so the parity bit is zero when the return is detected.
To turn this reasoning into a local invariant, we will record the current
position in the cycle.

## 4. A three-bit example with two different periods

Use the existing synthetic [rotation3 model](../research/odd_order_witness_v1/models/rotation3.aag).
Its tap mask is `0x4`. In **coordinate order** $(x_0,x_1,x_2)$, its update is

$$
A(x_0,x_1,x_2)=(x_2,x_0,x_1).
$$

In this section, `100` abbreviates the tuple $(1,0,0)$ in that order; it is
not a convention about how an integer is printed in binary. Thus
`100 → 010 → 001 → 100`, whereas `111 → 111`.
The nonzero seeds have periods 1 or 3. Both $A^3=I_3$ and $A^9=I_3$ hold.
We deliberately use the valid but nonminimal supplied exponent $M=9$.

After a nonzero input has seeded `100`, the following table describes successive
zero-input evaluations. The phase $t$ names the position we will later store.

| Phase $t$ | Register $r$ | Saved $s$ | Parity $c$ | Imminent return $m$ | Next phase |
|---:|---|---|---:|---|---:|
| 0 | `100` | `100` | 0 | false | 1 |
| 1 | `010` | `100` | 1 | false | 2 |
| 2 | `001` | `100` | 0 | true | 0 |

At the return evaluation, $c=0$, so the first bad clause is false. The register
never becomes zero, so the second clause is false too. For seed `111`, every
active evaluation is already an imminent return: its phase and parity stay zero.

Why not simply use $0\le t<9$ for both seeds? For seed `100`, that would allow
$t=3$, $r=s=\texttt{100}$ and $c=1$. This state has the wrong cycle parity.
Two zero-input transitions bring it to $r=\texttt{001}$ with $c=1$, where the
next zero-input evaluation is bad. It is unreachable from the intended initial
state, but an invariant admitting it would still have to prove it safe.
The bound must use the seed's actual period, not just a common multiple.

## 5. Compute each seed's period with fixed tests

Suppose the complete factorization is
$M=\prod_i p_i^{e_i}$, with distinct primes $p_i$.
For each prime and each $k=1,\ldots,e_i$, test

$$
A^{M/p_i^k}s=s.
$$

Write $v_{p_i}(T_s)$ for the number of factors $p_i$ in the true period.
The test succeeds exactly when $T_s$ divides $M/p_i^k$, equivalently when
$v_{p_i}(T_s)\le e_i-k$. As $k$ ranges from 1 to $e_i$, exactly
$v_{p_i}(T_s)$ tests fail. Multiply by $p_i$ once for each failure:

$$
P(s)=\prod_i\prod_{k=1}^{e_i}
\begin{cases}
1,&A^{M/p_i^k}s=s,\\
p_i,&A^{M/p_i^k}s\ne s.
\end{cases}
$$

Then $P(s)=T_s$. This works for zero, fixed points, mixed periods, repeated
prime factors and unnecessary factors in $M$.

For rotation3 with $M=9=3^2$, the two tests are $A^3s=s$ and $As=s$:

| Seed | First test | Second test | Product $P(s)$ |
|---|---|---|---:|
| `000` | true | true | 1 |
| `111` | true | true | 1 |
| `100` | true | false | 3 |

Each test uses a **fixed matrix**, so it becomes a binary linear circuit on
the seed bits. The constructor shares equivalent tests and multiplies by fixed
primes. No circuit must discover a discrete logarithm. Obtaining the complete
factorization is still construction work; this does not make factoring free.

## 6. Add history and prove the invariant

Add a zero-initialized history register $t$ of
$L=\max(1,\lceil\log_2 M\rceil)$ bits. For $M=9$, four bits suffice.
Its update is defined for every state and input:

$$
t'=\begin{cases}
0,&u\ne0\ \lor\ s=0\ \lor\ m,\\
t+1\pmod{2^L},&\text{otherwise}.
\end{cases}
$$

Use the extended-state predicate

$$
H(r,s,c,t)=
(r=s=0\land t=0)
\;\lor\;
(s\ne0\land 0\le t<P(s)\land r=A^t s\land c=t\bmod2).
$$

The idle clause puts no condition on $c$. Now check the three obligations.

**Initiation.** All registers start at zero, so the idle clause holds.

**Preservation.** A nonzero input establishes $r'=s'=u$, $c'=0$ and $t'=0$,
which satisfies the active clause for the new seed. With zero input, an idle
state stays idle while $c$ toggles. For an active state, exactness of $P(s)$
gives $m$ if and only if $t=P(s)-1$. At that point the source and history
updates return to $(r',s',c',t')=(s,s,0,0)$. Otherwise $t<P(s)-1$, and the
updates advance the phase and register together and toggle parity. The phase
does not overflow within $H$.

**Safety.** In the idle clause, $s=0$, so both bad clauses are false. In the
active clause, invertibility makes $Ar\ne0$, ruling out the second clause for
every input. For the first clause, an imminent return means $t=P(s)-1$.
Since $P(s)$ is odd, this phase is even and $c=0$. Reseeding inputs also make
the first clause false through its explicit $u=0$ gate.

Induction proves safety for every input sequence, including arbitrary repeated
reseeding. We have not assumed that the environment waits for a cycle to finish.

Adding $t$ does not remove any original execution. Start it at zero and apply
its total update along any original run: this gives a unique extended run.
Dropping $t$ recovers the same original states and inputs because their updates
were untouched. This is the trace-preservation role of a **history variable**.
It records a phase along an execution; it need not reconstruct that phase from
an arbitrary pair $(r,s)$ presented in isolation.

For full bounds and edge cases, including $M=1$, see the
[seed-period proof](../research/odd_order_witness_v1/THEORY.md) and the
[final cost clarification](../research/CONTRIBUTION_ASSESSMENT_18.md).

## 7. From this proof to a checked artifact

AIGER is a format for Boolean circuits built from AND gates and inverted edges,
with inputs and state-holding latches. A witness is another circuit in that
format. Certifaiger is the tool that relates it to the original circuit.

The implemented producer recognizes the specified raw circuit wrapper and
constructs an ordinary AIGER witness. It retains the original inputs and state,
adds history, and sets its strengthened detector to
$\operatorname{bad}_{\mathrm{original}}\lor\neg H$.
The original model is supplied separately to Certifaiger. Its obligations must
justify the correspondence and the safety argument; construction alone is not
acceptance. The implemented frontend is bounded to widths 2 through 24 and
positive odd $M<2^{24}$.

Each obligation asks whether a proposed condition, such as induction, can fail.
The pipeline encodes that failure condition as **CNF**, a conjunction of clauses.
A satisfying assignment is a counterexample to that obligation; **UNSAT** means
no such assignment exists. This checks the encoded condition over all its
states and inputs, rather than testing a bounded list of executions.
An **LRAT** trace records steps that a proof checker can replay to justify UNSAT
without repeating the solver's search.

The pinned pipeline generates nine obligations and requires UNSAT with
successful native proof replay for each. The repository separately replays
the retained completed CNF proofs. This checks those formulas, while native
model/witness interpretation, obligation generation and CNF translation remain
trusted. The checkers and runtimes also remain trusted; this is not an
end-to-end formally verified compiler. The [interface dossier](../research/proof_interface_v1/SOURCES.md)
and [assurance table](../research/CONTRIBUTION_ASSESSMENT_18.md#assurance-boundary)
spell out the boundary.

The [completed comparison](../research/BOUNDED_COMPARISON_GATE_17.md) found added
accepted-witness coverage at width 8 against one fixed rIC3 configuration under
its stated budget. It did not establish a general speedup or a new algebraic
method. Order extraction and history variables are established techniques;
the [contribution assessment](../research/CONTRIBUTION_ASSESSMENT_18.md) retains
this work as a reproducible integration case study and leaves a distinct
standalone contribution uncleared. A small witness need not have a small SAT
proof: exporter trials at widths 12, 16 and 24 exhausted the raw-artifact budget.

## 8. Where the production certificates fit

The production `alc/` package has a separate contract: one invertible affine
recurrence over a prime field, one initial state, and one full-state target.
An accepted positive certificate establishes the complete hit set
$\{t_0+jr:j\ge0\}$, where $r$ is the least point period. Its checker validates
supplied return, nonreturn and hit evidence. This hardware exporter does not
use the complete orbit-certificate engine.

See the [production specification](SPECIFICATION.md) for that proof and the
[repository example](../README.md#try-a-complete-target-hit-example) for its commands.
Producer failure, rejected evidence and resource exhaustion establish neither
unreachability in that contract nor an unsafe hardware model here.

Before reading the technical modules, check that you can explain why the idle
case allows both parity values, why $M=9$ cannot replace $P(s)$ for rotation3,
and why adding a total history update leaves every original input sequence
available. Those three points connect the transition-system proof to the
delivered witness.
