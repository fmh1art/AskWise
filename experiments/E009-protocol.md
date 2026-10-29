# E009: exact binary comparison certificates under strict relevance

Frozen 2026-10-29 before running this policy. Development only.

Compare four-cell exact bounds versus E005 partition-star bounds with identical
fixed and witness-adjacency execution acquisition. Both require an observed
context-matched unequal pair before questioning. All selected questions must be
greedy EC2 maximizers for every completion of the unknown Boolean labels, but
may select different tied maximizers. A simple immediate-witness policy asks as
soon as a local witness exists and is an essential execution-cost control.
Stopping requires all surviving worlds executed and equal; no unseen labels are
available to the acquisition policy. Question costs are equal and the prior is
uniform on a complete binary cube. No total-cost optimality theorem is claimed.

Reuse E001's 300 development cases, all 16 true worlds. Convert their SQL answers
to declared Boolean outputs: top_region tests whether East is among winners;
customer_count tests count>=6; threshold_count tests count>=5. These are derived
controlled tasks, not new external benchmarks. Report executions, questions,
policy CPU, and total costs at question/execution weights 0.1, 1, 10. The latter
are sensitivity analyses, not a user-specified production exchange rate.

Verify every Boolean map over an eight-world cube, every true world, and each
bound/immediate policy: correct output, a local pair using only already observed
labels at every question, and a complete stopping certificate. If the simple
immediate-witness control dominates the exact-bound policy in the primary
execution metric, do not call exact action certification the main contribution.
Wall limit 30 minutes.
