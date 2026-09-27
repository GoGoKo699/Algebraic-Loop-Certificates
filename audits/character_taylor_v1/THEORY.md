# Character relations and Taylor blocks reproduce the field-source contract

27 September 2026. Scientific comparison, not manuscript prose. The existing
source format is reused. No domain, production API, or certificate format is
added. This note distinguishes a constructive comparison from a claim that a
particular prior paper contains every clause of our software interface.

## 1. The exact comparison result

Fix an explicitly represented invertible affine recurrence over F_p, with a
fixed initial state a. Let C be a valid source certificate in the existing
`alc.compiled-orbit.v1` format. There is a deterministic polynomial-time compiler
which checks C and constructs the following recognizer using ordinary character
relations and finite Taylor/Jordan blocks. It recognizes the entire orbit of a,
for every subsequently supplied complete-state target, in polynomial time.
It returns the same least point period as the existing compiler, but no first
hitting time. It uses no finite-field target logarithm, factor search, or orbit
traversal. The serialized certificate is IDENTICAL; its derived cache differs.

The alternative does not call the old source compiler, cyclic-coordinate solver,
or unipotent-group recognizer. It shares the production parser and primality
checks, matrix inverse check, and elementary polynomial arithmetic. Independent
code paths are not formal verification of the shared arithmetic or Python.

The proof below covers general repeated factors, not just diagonal sources.
It supplies a representation-level comparator at the coarse polynomial-bound
level. It establishes neither a lower complexity exponent nor a timing advantage.
Source factorization, exact orders and source-to-source alignments may remain
expensive to discover. Their costs are charged equally to both paths.

## 2. The source certificate's ordinary algebraic data

Lift the recurrence to T=[[A,c],[0,1]], with v=(a,1). Let W be the cyclic span of
v, and let mu be the minimal polynomial of T on W. Put k=deg(mu)<=d+1. Since T
is invertible, mu has nonzero constant coefficient. Exact elimination supplies
an isomorphism

    R=F_p[X]/(mu) -> W,    h -> h(T)v.

For a query state y, reject if (y,1) is outside W; otherwise calculate its unique
coordinate h, of degree less than k. The orbit condition is X^t=h in R. Both
compilers check the inverse witness and compute their cyclic coordinate data
from the original source, rather than trusting a producer-supplied basis.

The supplied factors satisfy

    mu = product_i f_i^(e_i),    sum_i deg(f_i)*e_i=k.

Each f_i is checked monic, irreducible, and nonzero at zero. Let K_i=F_p[X]/(f_i),
alpha_i=X mod f_i, and let m_i be its checked exact multiplicative order. Complete
integer factor products and recursive prime proofs support the usual exact-order
checks. These are source obligations, not target-phase witnesses.

Comparison witnesses identify pairs i,j, a nonzero algebra S=F_p[Z]/(H), and
roots r_i,r_j of the named f_i,f_j. Since the f_i are irreducible, the corresponding
unital maps K_i -> S and K_j -> S are injective. H itself need not be irreducible.
With D=gcd(m_i,m_j)>1, the checked calibration is

    r_i^(m_i/D)=r_j^((m_j/D)c),    gcd(c,D)=1.

The proof data already used by the existing compiler therefore provide the
constants required by the classical character predicates. The comparator does
not receive stronger hints, target exponents, a larger splitting field, or a
lookup table. It independently checks all these obligations.

## 3. A local Taylor algebra retains every repeated factor

For an irreducible f of degree h and multiplicity e, let alpha=X mod f in K.
There is an F_p-algebra isomorphism

    F_p[X]/(f^e) -> K[Z]/(Z^e),    X -> alpha+Z.                 (T)

To prove it, f(alpha)=0 and f'(alpha)!=0 because finite fields are perfect.
Thus f(alpha+Z) is divisible by Z exactly once, so f^e maps to zero. Conversely,
a polynomial maps to zero exactly when alpha is a root of multiplicity at least e.
Since its coefficients are in F_p, every conjugate of alpha has the same
multiplicity. Their distinct minimal factors imply f^e divides that polynomial.
The kernel is precisely (f^e). Both algebras have dimension he, so (T) is an
isomorphism. Combined over i, the product of these maps is an isomorphism for R.

Writing

    h(alpha_i+Z)=sum_(j<e_i) H_(i,j) Z^j,

the coefficients H_(i,j) are Hasse/Taylor coefficients. No factorial is inverted.
They can be obtained by multiplying by alpha_i+Z while processing coefficients,
or by the finite identity

    H_(i,j)=sum_(r>=j) h_r * binom(r,j) * alpha_i^(r-j).

The implementation precomputes the images of 1,X,...,X^(k-1). The total number
of stored base-field coefficients is k*sum_i e_i*deg(f_i)=k^2. This is not an
expanded high-degree invariant polynomial or an orbit-state list. The checks
include multiplicities greater than the characteristic, for which division by
j! would be invalid.

Under (T), a true orbit point X^t has local value

    (alpha_i+Z)^t = alpha_i^t (1+Z/alpha_i)^t.                 (J)

This is the usual binomial formula for a Jordan block. It cleanly separates
constant field data from the nilpotent coefficients.

## 4. The constant terms are characterized by standard character relations

Put beta_i=H_(i,0). First check beta_i^(m_i)=1 in K_i. This implies beta_i is
nonzero and belongs to <alpha_i>, since the multiplicative group of a finite
field is cyclic. For proof purposes there is a unique t_i mod m_i with
beta_i=alpha_i^(t_i); the query never solves for it.

Each comparison checks

    phi_i(beta_i)^(m_i/D)=phi_j(beta_j)^((m_j/D)c).            (C)

After the source calibration, (C) is exactly t_i=t_j modulo D. On the local
subgroups these are kernels of characters trivial on the source generator.
They are the ordinary multiplicative relations used for diagonal cyclic actions,
not a different kind of orbit invariant invented by this code.

The graph of comparisons is accepted only when every prime-power support is
connected. This sufficient-and-necessary coverage criterion is proved in the
preceding compiled-orbit note. The new checker implements it independently with
union-find for each support. Equivalently, paths propagate equality modulo each
prime power dividing a required gcd. Thus the tested relations imply a common
semisimple residue

    t = t_sem mod m,     m=lcm_i(m_i),    gcd(m,p)=1.

No value of t_sem needs to be known. The established input bound on each comparison
algebra is deg(H)<=deg(f_i)deg(f_j); summing over pairs gives polynomial space.
A common splitting field for all f_i is unnecessary.

## 5. Characteristic-primary time is read from a binomial row

Normalize the Taylor expansion by its nonzero constant:

    Y_i(Z)=h(alpha_i+Z)/beta_i.

For a true orbit point this is (1+Z/alpha_i)^t. Let e_max=max_i e_i and let
P=p^a be the least p-power at least e_max. Then the order of 1+Z/alpha_i in
K_i[Z]/(Z^e_i) is the least p-power at least e_i, because

    (1+Z/alpha_i)^(p^j)=1+Z^(p^j)/alpha_i^(p^j).

Choose a block with multiplicity e_max. Write the possible residue t mod P as
z=sum_(j<a) z_j p^j. The coefficient of Z^(p^j) in its normalized expansion is

    [Z^(p^j)]Y = z_j * alpha^(-p^j).                       (D)

One proof is to expand

    (1+W)^z = product_j (1+W^(p^j))^(z_j)

in characteristic p. Lower-place choices have maximum total degree p^j-1,
so the coefficient at p^j is exactly z_j. This is the relevant special case
of the classical Lucas binomial-digit identity, not a new logarithm theorem.

Equation (D) determines the only possible digit by multiplying its coefficient
by alpha^(p^j). The result must lie in the embedded prime field F_p; a general
extension-field value is not a permissible base-p digit. The implementation
checks this condition in the canonical polynomial representation.

There are at most ceil(log_p e_max) such digits. Recovering them is not a search
across p possibilities, and it does not recover a semisimple field logarithm.
The integer z has at most log_2 p+log_2 e_max bits, since P<p*e_max for e_max>1.

## 6. Every coefficient must be checked, in every block

After recovering z from one largest block, check

    H_(i,j)/beta_i = binom(z,j)*alpha_i^(-j)
       for all i and all 0<=j<e_i.                        (F)

Binomial values are computed by base-p digits; the lower index is at most k.
There is no cost proportional to a large target exponent. Full replay is essential.
For example, in characteristic two modulo Z^5, the candidate 1+Z^3 has zero
coefficients at Z,Z^2,Z^4. Those digits suggest z=0, but the coefficient at Z^3
violates (F). The test suite retains the corresponding actual source and target.
Different blocks must use the SAME z; their nilpotent times cannot be selected
independently.

Soundness and completeness now follow directly. A power X^t passes local
subgroup checks, character conditions and every Taylor coefficient. Conversely,
local and character checks give t_sem mod m. Condition (F) gives a common z mod P.
Because m and P are coprime, integer CRT supplies t with both residues. Equation
(J) then matches the queried h in every local Taylor algebra. The isomorphism
(T) gives h=X^t in R. This proves exact membership for all targets, not just
sound exclusion. It also proves the least period is

    r=lcm_i(m_i)*P.

The period is not just an upper bound: local scalar orders force m, and the
largest nilpotent block forces P. The product is required because they are
coprime. This formula is standard Jordan-order theory.

## 7. The two complete query contracts are equivalent

Both the existing compiled predicate and this character/Taylor predicate are
now proved equivalent to X^t=h. Therefore they agree on EVERY target for any
accepted certificate in the common domain. The same serialized certificate
is accepted after rechecking; no advice about future targets is added.

The alternative independently computes a cyclic basis/left inverse and a
Taylor cache. It does not rely on the old CompiledOrbit.query or on the old
unipotent_log. Thus it also gives a useful implementation-diversity check.
It does rely on the same representation of the algebraic source facts and
on shared elementary field arithmetic and primality verification. It is not
an independently authored certificate producer or an independently formalized
mathematical foundation.

This is stronger than the previous scalar-only or prime-power-wrapper comparisons:
it covers all invertible affine prime-field sources, all complete targets,
and all multiplicities. Its construction is a certifying adaptation of
classical character relations and Jordan/Taylor arithmetic written for this
audit, not code retrieved from a historical solver. The comparison establishes
that the coarse polynomial certificate/check/query guarantee does not by itself
distinguish a new algorithmic mechanism.

## 8. Resource accounting

Let B=ceil(log_2 p) and k<=d+1. The proof has the same bytes as the existing
source certificate, including prime proofs, inverse matrix, complete primary
factors/orders and source alignments. All are polynomial-size in d and B.
The new Taylor cache has O(k^2) base-field entries, plus existing-sized coordinate
and pair-map data. The compiler uses polynomial elimination and checked field
powers; queries use a fixed linear map, local field powers, character checks,
base-p digit extraction and polynomially many coefficient checks.

The two recognizers have the SAME COARSE polynomial bounds; no equality of
operation counts or optimal complexity exponent is claimed. No timings are
reported. A smaller derived cache for one case would not establish a general
verification advantage. Both source producers may need difficult source logs
and factorization. Those are unchanged costs, not hidden free preprocessing.

## 9. Scope and research consequence

The current full-state prime-field contract survives as a proved certifying
implementation of established structure. The proposed compiler remains useful
research software, with accurate source/query and untrusted-proof boundaries.
This audit supplies no new practical advantage and does not establish historical
priority for the full software contract in either direction.

The bibliography gap concerning the Menezes-Wu reduction is now closed at
full-text mathematical-inspection level through the author-hosted PDF; see
SOURCES.md. That paper solves promised matrix logarithms and does not itself
state this exact static-certificate interface. The comparison uses its actual
Jordan algebra together with the ordinary character construction; it does not
mislabel promised exponent recovery as an already published unpromised
all-target certifying implementation.

On current evidence, the coarse source-compilation theorem should be treated
as a certifying reformulation, not as a cleared original theorem sufficient
for the paper. A sharper verifier-cost result, formal assurance result, or
an independently useful analysis capability would need its own proof and
comparison. None is claimed completed by this audit. Manuscript work is on hold.
