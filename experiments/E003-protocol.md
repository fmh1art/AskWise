# E003: generated intent coverage on AmbiQT with repair alternatives

2026-10-29, exploratory model study, frozen before any model answers on this task.

Population: all E002 executable/perturbable AmbiQT-C items. Per database, sort SHA256(`A2-E003-20261029` + item id) and take at most eight items with distinct original Spider example IDs. Selection ignores equality, query answers, method outcomes, and LLM outputs. This is a diagnostic sample, not an official full AmbiQT score. Freeze IDs and hashes before generation.

Models: configured `gpt5_6_sol_hydra.yaml` and `doubao_seed2_lite.yaml`; record returned identifiers. One generation per item per model, no prompt tuning, no gold SQL in prompt, maximum four interpretations, JSON output, 4096 completion tokens. Context: ambiguous NL question and database schema, with no table rows or gold answers. Two concurrent requests within one model queue; models run sequentially. Reuse exact-prompt cached outputs, maximum three transport retries, malformed/truncated responses count as model failures and are not resampled. Maximum 24h per batch.

Main endpoint: recall of the two annotated SQL execution signatures across both data states. Report support precision, all-reference-found, errors, and matched comparison of observed-data deduplication versus repair-stable deduplication of the identical generated candidates. Duplicates are judged only on finite evaluated databases, not universal SQL semantics. SQL authorizer permits only SELECT/read/functions, with query-only mode and bounded execution. Data outputs remain local.

This evaluates candidate generation plus pruning, not human multi-turn dialogue or a complete deployed agent. Gold signatures are used by the evaluator only. No claim of globally complete natural-language support. Candidate repair space is provided by the controlled extension. Pairing and confidence intervals cluster by original database; do not count interpretations or data worlds as independent examples.

Acceptance gate: any new method must preserve valid candidates beyond observed-data pruning, and coverage failures must be separately quantified. Reproducing AIR's pruning operation is an ablation, not a full reproduction of its adversarial generation. No claim of a novel EC2 objective.
