# E001: finite-world falsification study (exploratory)

Frozen before execution, 2026-10-29. Synthetic mechanism study, not an external benchmark or an LLM-agent evaluation.

Generate 300 tasks (100 per sales top-region, customer count, thresholded order count) with seeds 0..99. Each task has one binary intent and three binary repair assumptions, giving 16 equiprobable worlds. Execute all worlds; evaluate each possible hidden true world. A task is the statistical unit; worlds are repeated measures. Exact enumeration is available equally to all full-world strategies.

Compare no clarification, ask all, fixed order with invariant stopping, random order with invariant stopping, world entropy, answer entropy, EC2, one-coordinate local checking, intent-on-observed-data then repair, repair-then-intent, and exact optimal decision tree. EC2 and optimal trees are established methods, not claimed contributions. Unit question cost. Answer set equality preserves ties. No probability calibration or human-response claim.

Primary measurements: task-averaged exact correctness and mean questions. Report aggregate and each family. Invariant stopping is guaranteed correct only within a complete enumerated universe and truthful feedback; do not present that guarantee as an empirical discovery. Compare EC2 to optimal cost to assess whether a new selection heuristic is warranted. Preserve counterexamples and all outcomes.

Negative controls: invariant tasks, XOR interaction, a repair which exposes previously equal intents, and incomplete-world stopping. These tests check mathematical and implementation properties, not prevalence.

Next evidence gate: independently sourced real databases, naturally ambiguous queries, model-generated candidates, equal candidate-generation budget, missed-world audits, and honest unanswerable feedback. Do not expand solely because synthetic baselines are weak.
