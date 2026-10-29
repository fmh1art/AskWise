# E010: expanded evidence and manuscript reporting

The fresh run has 120 SQL-generated tasks (40 shared seeds times three families)
plus 48 separately labeled stress fixtures. Ten configurations and sixteen hidden
worlds yield 26,880 simulated policy episodes. This is not 26,880 independent
samples or API calls. Execution took 9.37 seconds; additional API requests: zero.

The revised 12-by-9 main table crosses task families and cost metrics with seven
policies enforcing the same guarantees. Contract failure counts are reported in
a separate ten-configuration appendix audit. The four-by-eleven model table
reports reference support by reference-defined stratum; resources appear once
per model in another appendix table. All model analyses reuse the same 310
E003 outcomes.

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

Nine plots are generated in PDF, SVG and PNG:
1. Grouped task-family cost comparison (four panels, seven strict configurations).
2. Paired family-level execution differences (40 seeds per family).
3. Stress answer/relevance heatmaps (descriptive repeated fixtures).
4. Structured scaling (reanalysis of three existing seeds per size).
5. Exact and relaxed bounds over all 6,561 partial Boolean maps.
6. Two-model reference support by reference stratum, with database-cluster intervals.
7. Grouped per-database model reference-recall comparisons.
8. Controlled-repair audit denominators and database heterogeneity.
9. Cost sensitivity computed from the same execution/question measurements.

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


## Presentation revision after user review
The earlier ten-by-ten pooled display is superseded by a twelve-row,
nine-column cost table. Its three family blocks plus pooled block each report
E, Q and E+10Q across seven strict configurations. The ten-configuration contract
audit is now separate. This avoids interpreting built-in conditional correctness
as an actual model success rate.

Model recovery is now also shown within two reference-defined strata. Of the
155 cases, 53 have two distinct reference signatures across the two data states
and 102 have one. In the two-signature stratum, recall changes from 42.45% to
67.92% for Doubao and from 44.34% to 73.58% for GPT; one-signature recall is
unchanged. Observed-state full recovery is structurally zero in the former
stratum because matching candidates share the observed answer and collapse.
These are descriptive analyses of the same cached sample, not extra benchmarks.

The cost, model and database figures now use grouped bars. The old cost
sensitivity plot is retained separately, bringing the statistical figure count
to nine. None of the original per-task outcomes or overall model metrics changed.
