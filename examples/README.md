# Executable examples

Each input has a matching `.certificate.json`. The CLI checks the pair before answering anything.

| Input | Exact consequence | Evidence |
|---|---|---|
| [Fibonacci](fibonacci.json) | `(1,0)` reaches `(4,5)` at `11 mod 16` over F7 | [Minimal-period certificate](fibonacci.certificate.json) |
| [Affine clock](affine.json) | `x <- x+1` reaches `4` at `4 mod 7` from zero | [Hit certificate](affine.certificate.json) |
| [Outside span](outside_span.json) | The identity map cannot move `(1,0)` to `(0,1)` | [Separating functional](outside_span.certificate.json) |
| [Inside span, absent](inside_span_absent.json) | Multiplication by 4 over F5 alternates `1,4`, never `2` | [Explicit cycle](inside_span_absent.certificate.json) |

`python examples/consumer_demo.py` verifies the first two and intersects their schedules. Both targets occur at `11 mod 112`. It then counts hits and locates the next simultaneous hit at a large binary-encoded horizon without replaying either recurrence.

These are small explanatory examples. Their solutions are easy classically. No practical or asymptotic discovery speedup is claimed.
