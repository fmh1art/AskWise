# E008: strict relevance audit and exact binary comparison bound

Frozen 2026-10-29 after the user's explicit strict-guarantee decision.

Relevance means a witnessed pair of surviving worlds which differ only in the
queried coordinate and have different answers. This is a conditional guarantee
within the declared universe; it is not a promise about which response occurs.
For Cartesian supports this tests coordinate dependence. For constrained
supports it can be conservative or admit no feasible next question; no claim of
completeness there. Previous E006 used a weaker, arbitrary conflicting-pair gate
and must not be described as satisfying this strengthened contract.

Audit all 300 E001 development instances and all true worlds for EC2, optimal,
fixed, random, answer-entropy, and repair-first. Preserve prior results. Add a
constructed nuisance-bit + XOR example: EC2's marginal gains tie, so a fixed
tie rule can query an irrelevant coordinate. A relevance-filtered full-map
baseline is therefore mandatory, not a sufficient new contribution.

Candidate technical component: for Boolean answers, a uniform Cartesian binary
cube, and equally costly coordinate tests q,r, let a,b,c,d be the numbers of
positive answers in their four joint response cells. The unnormalized EC2 gain
difference is (a-d)(b-c). With partially executed labels each count has an exact
integer interval; the two differences use disjoint cells. Therefore the exact
minimum/maximum over all binary completions are the four endpoint products.
This is stronger than an independent-edge relaxation and requires no labels
outside observed executions. Validate all 3^8 partial label maps against all
256 completions on an eight-world cube. No new acquisition-policy guarantee,
novelty, SQL applicability, or empirical saving is asserted by this identity.

Reproduction correction: the first audit inadvertently used `seed` for the
random policy rather than E001's `20261029+seed`. Its output is archived outside
Git at `/data01/fanmeihao-data/A2-research/E008/relevance-audit-initial-seed-offset.json`.
The final audit replays E001's exact random seed. Deterministic policies and the
bound check are unaffected; no scientific endpoint was changed.
