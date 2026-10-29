# E006: mixed execution/clarification cost pilot

2026-10-29, after E005. Exploratory development, not a novelty claim. Fixed EC2 action fidelity prevents choosing additional questions even when they avoid expensive executions. Test joint actions without requiring the same question path.

Candidate: greedy unresolved-certificate coverage. Obligations are unlabeled surviving worlds and surviving pairs not yet certified equal. Asking removes obligations by excluding worlds. Executing reveals labels, resolving its vertex and same-label edges to known worlds. Expected execution gain uses observed label frequencies plus one pseudo-count for a new class; it is a heuristic, not a calibrated prior or submodularity theorem. Only witnessed answer-separating questions are eligible. Stops only when all survivors have known equal answers.

Compare full EC2, fixed/partition lazy EC2 from previous studies, ask-first identification, witness-then-world-split, and certificate greedy. Ratios question/execution cost 0.1, 1, 10. Repeat E001 development instances. Report total cost, questions, executions, correctness, and policy time. No cost weights fit to outcomes. Also compute exact Bayesian joint optimum on 4-world Boolean cases with explicit independent Bernoulli(0.5) answer labels and uniform hidden world, both with/without witness gating. This prior is an artificial control, not a realistic SQL assumption.

The potential has complementary execution actions and no adaptive-submodularity guarantee is asserted. Gains over full execution are insufficient if witness-split is equally good. Independent real SQL evaluation and stronger cost models would be necessary for acceptance.
