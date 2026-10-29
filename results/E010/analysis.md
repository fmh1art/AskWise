# E010: expanded evidence and manuscript reporting

The fresh run has 120 SQL-generated tasks (40 shared seeds times three families)
plus 48 separately labeled stress fixtures. Ten configurations and sixteen hidden
worlds yield 26,880 simulated policy episodes. This is not 26,880 independent
samples or API calls. Execution took 9.37 seconds; additional API requests: zero.

The 10-by-10 main table separates answer accuracy, counted executions, questions,
true irrelevance, unproved relevance, stopping certificates, two hypothetical cost
weights and policy computation. The four-by-ten model table reuses all 310 E003
outcomes for reference support, SQL validity, candidate counts, token usage and
latency. Repeated generation-cost fields represent shared calls.

Exact/fixed uses 13.8021 executions; partition/fixed uses 14.8771; immediate/witness
uses 13.1833. The exact-minus-immediate paired effect is 0.61875 executions with
95% seed-cluster interval [0.34583, 0.94169]. The exact bound improves the relaxation
but does not pass the primary execution-cost gate. Immediate querying asks 0.8354
questions versus 0.8104 for exact/fixed; high question costs can change the ranking.

All strict configurations satisfy the measured answer/relevance/stopping
contract. Ungated ask-all is correct but 79.11% of its questions are irrelevant on
fresh sales. Full EC2 has no relevance violations on that cohort but asks 50%
irrelevant questions on the nuisance-XOR fixture. This is a concrete reason to
report stress diagnostics separately from pooled accuracy.

Eight plots are generated in PDF, SVG and PNG:
1. Execution/question frontier and cost sensitivity (same measured pairs).
2. Paired family-level execution differences (40 seeds per family).
3. Stress answer/relevance heatmaps (descriptive repeated fixtures).
4. Structured scaling (reanalysis of three existing seeds per size).
5. Exact and relaxed bounds over all 6,561 partial Boolean maps.
6. Two-model reference support with database-cluster intervals.
7. Per-database model reference-recall gains.
8. Controlled-repair audit denominators and database heterogeneity.

The source manifest records hashes for all 310 cached model outcomes, other
measurement sources, analysis code, tables and figures. SQL truth-map construction
is excluded from policy CPU timings. No real-user latency, natural repair
prevalence, total API billing, new independent benchmark, or algorithmic novelty
is inferred from these expanded metrics.

Reproduce with the project virtual environment:
    python scripts/run_e010.py
    python scripts/report_e010.py

The report command needs the existing E003 cache in the external data directory.
The run command itself needs no API credentials or original AmbiQT databases.
