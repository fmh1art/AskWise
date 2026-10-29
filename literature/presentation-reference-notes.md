# Presentation references supplied through the user's CV

Date: 2026-10-29. Scope: A2 tables and figures only. The CV was used to locate
public paper links; its personal details are not copied into this repository.
PDFs and page renders are cached outside the repository in
/data01/fanmeihao-data/A2-research/presentation-references/.

| Reference inspected | Pages | Presentation pattern used |
|---|---|---|
| [DeepPrep](https://www.vldb.org/pvldb/vol19/p3371-fan.pdf) | 10–11 | Dataset groups with repeated metrics; baseline/ablation grouping; small multiples for task comparisons. |
| [AutoPrep](https://www.vldb.org/pvldb/vol18/p3504-fan.pdf) | 10 | Two-level headers, comparable metrics under each group, aligned entries and explicit best-value emphasis. |
| [BatchER](https://fmh1art.github.io/files/BatchER-ICDE2024.pdf) | 10 | Task-by-metric row blocks crossed with method families and variants; multiple panels sharing visual conventions. |
| [DeepAnalyze](https://arxiv.org/pdf/2510.16872) | 8 | Dense but labeled horizontal method comparisons and consistent grouping. |

These references inform visual organization only. Their measurements, benchmark
counts, and performance claims are not copied into A2. They are not added to A2's
scientific bibliography solely to justify a visual style.

A2 changes:
- Table 2 now crosses four task groups (three families and their pooled mean),
  three cost metrics, and seven configurations satisfying the same guarantees:
  12 data rows, nine columns, 84 comparable numeric entries.
- Table 3 groups actual model recovery by all 155 cases, 53 cases with two
  reference signatures, and 102 with one. These strata partition the same sample.
- Contract failures are an appendix audit of counts. Zero errors under supplied
  worlds and exhaustive stopping are explained as conditional correctness,
  not presented as perfect LLM accuracy.
- Generation resources are reported once per model, not repeated for each
  cached pruning rule.
- Cost figure: four grouped-bar panels, four task clusters, seven configurations.
  Model figure: six panels, three reference strata, two pruning rules.
  Database figure: paired horizontal bars in two model panels.
- All sampling intervals remain cluster bootstrap intervals. No significance
  stars or extra experimental runs are inferred from the denser presentation.
