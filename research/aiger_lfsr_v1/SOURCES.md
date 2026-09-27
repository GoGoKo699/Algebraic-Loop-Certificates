# Primary sources and exact scope

1. Tobias Nießen, **AIGER safety properties**, upstream repository:
   <https://github.com/tniessen/aiger-safety-properties>.
   Pinned commit `c8efd0251c0548dd46168db8410e6777c5f82b73`
   (29 November 2023). This repository describes its files as hand-designed
   testing and limited-benchmarking inputs, not industrial designs.

2. Original 23-task directory:
   <https://github.com/tniessen/aiger-safety-properties/tree/c8efd0251c0548dd46168db8410e6777c5f82b73/lfsr-period>.
   The preserved `.aag` bytes and [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)
   retain the upstream Git blob hashes. Upstream README and MIT license are
   preserved separately; Copyright (c) 2023 Tobias Nießen.

3. Width-4 task, inspected gate by gate:
   <https://github.com/tniessen/aiger-safety-properties/blob/c8efd0251c0548dd46168db8410e6777c5f82b73/lfsr-period/fibonacci-04-0xc.aag>.
   Git blob `908ebd7b513afa29385671c07e71167eaf1df90d`.
   Its raw interface permits arbitrary reseeding and checks zero-state entry and
   even return periods. The checker does not trust the upstream UNSAT label.

4. Width-24 task:
   <https://github.com/tniessen/aiger-safety-properties/blob/c8efd0251c0548dd46168db8410e6777c5f82b73/lfsr-period/fibonacci-24-0xe10000.aag>.
   Git blob `74414ad7dd0c4ad5fc58345d7b95fa8efcd98666`.
   This is the largest originally supplied task; we do not enlarge its width.

5. AIGER format and reference tools:
   <https://fmv.jku.at/aiger/>.
   The checker deliberately implements a strict subset matching these original
   ASCII files: ordinary zero-initialized latches and one safety output. Native
   format conversion and model-checker execution are separate observations.

6. Berkeley ABC primary source:
   <https://github.com/berkeley-abc/abc>.
   ABC's native PDR is an appropriate general AIGER safety baseline. A native
   verdict is not an independent external proof replay. The ordinary
   squarefree-polynomial comparator remains necessary even if PDR times out.

The squarefree/odd-order argument in THEORY.md is elementary established finite
linear algebra, supplied in full so that no novelty claim is inferred from the
absence of a matching package citation. Broader prior-art clearance, proof
assistant replay, general circuit extraction and industrial relevance are not
settled by this experiment.
