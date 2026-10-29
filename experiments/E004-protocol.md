# E004: exact EC2 action certification with unknown answer classes

2026-10-29. Exploratory algorithm prototype. User requires a substantive algorithm contribution, so positive runtime/cost results alone do not establish novelty.

Policy input: finite worlds and binary clarification outcomes, no answer labels. Labels are obtained exclusively through a counted execution callback. The reference EC2 baseline pays one execution per world up front. The proposed prototype bounds pairwise differences of EC2 gains, treating unknown disagreement edges conservatively in [0,1]. It can ask only after the maximizing question is certified and a real disagreement is observed. Stopping requires all surviving labels known and equal. Same question tie-breaking as exact EC2. Bounds are computed with integers under uniform prior.

Compare comparison-directed label acquisition, fixed-order label acquisition, random label acquisition (seed fixed), and full upfront EC2 on E001's 300 tasks and every hidden world. Reusing E001 makes this an exploratory development experiment, not independent confirmation. Verify complete traces against full EC2 on every Boolean output function of three binary assumptions (256 functions × 8 hidden worlds × 3 acquisitions).

Main criteria: exact action-sequence fidelity, same final answer, executions saved, policy-selection runtime, and difference versus fixed/random lazy controls. Count all executions; do not infer a speedup from reduced execution count. SQL runtime dominates only if measured or explicitly modeled. A toy count reduction is insufficient to meet the user's algorithm novelty requirement.
