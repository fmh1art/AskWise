# Presentation references supplied through the user's CV

Date: 2026-10-29. Scope: A2 tables and figures only. The CV was used to locate
public paper links; its personal details are not copied into this repository.
PDFs and page renders are cached outside the repository in
/data01/fanmeihao-data/A2-research/presentation-references/.

| Reference inspected | Pages | Presentation pattern used |
|---|---|---|
| [DeepPrep](https://www.vldb.org/pvldb/vol19/p3371-fan.pdf) | 10–11 | Dataset groups with repeated metrics; baseline/ablation grouping; small multiples for task comparisons. |
| [AutoPrep](https://www.vldb.org/pvldb/vol18/p3504-fan.pdf) | 10–11 | Two-level headers; compact clustered bars with shared legend and light outlines (Figure 8). |
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

Second plot-polish pass (2026-10-29):
- Following AutoPrep Figure 8 and DeepPrep Figure 6, narrow bars form visible
  method pairs within task clusters. Cost plots separate selection colors from
  acquisition hatches, with a shared legend for each. All bar axes start at zero.
- All nine plots use the same Times-like STIX typography, muted colors, thin
  boxed axes, sparse grids, and lighter error bars. PDF/SVG exports remain vector;
  PNG previews are 300 dpi. Panel labels and legend positions are consistent.
- The six model panels share their scale and highlight the reference-defined
  two-signature cohort. Four callouts report measured percentage-point differences,
  not significance. Sample counts and structural zero recovery remain explicit.
- The certificate comparison now uses paired bars at discrete observation counts.
  Exact/partition colors match the main policy plot. The finite-map diagnostic
  has no sampling intervals.
- Stress heatmaps use white for zero violations and gray/dashes for undefined
  question-conditional rates. Database bars share alternating row guides and
  include sample counts; the controlled-audit bubble plot has a size legend.
- Cost sensitivity displays excess over the cheapest displayed policy at each
  cost weight, exposing the mean crossover at 24.75. Bootstrap replicates
  recompute the comparator minimum. This is a transformation of the existing
  paired counts, not a new policy run or an optimized adaptive policy.
- BatchER Figure 7 informs consistent small-multiple axes/markers and light
  uncertainty bands. Runtime markers show only the measured repair sizes;
  enumeration is never extrapolated.

The paper captions describe these encodings. Final validation checks the compiled
ACL pages as well as individual figures; all saved measurement statistics and
four generated tables are unchanged from the previous revision.

Third pass: closer reference styling (2026-10-29)
------------------------------------------------
The user requested closer alignment of the experimental Matplotlib plots with
their existing papers. AutoPrep p. 11 / Figure 8 and DeepPrep p. 11 / Figure 6
were re-inspected at enlarged figure scale; BatchER p. 10 / Figure 7 was also
checked. The earlier muted STIX treatment did not closely match the first two
references' sans-serif, bold-label, purple/hatched presentation.

- All nine plots now use DejaVu Sans, centered bold panel headings, bold axis
  labels and dark thin boxed axes. This approximates the visible reference
  typography; the source font of the raster reference figures is not asserted.
- Model comparisons use pale-purple hatching for observed-state pruning and
  deep-purple solid fill for two-state pruning, following DeepPrep's paired
  visual organization. The same encoding is used in the database breakdown.
  Model names appear once per row instead of repeating in each panel title.
- Cost plots retain four selection colors and seven configurations. Same-color
  solid/light-hatched pairs distinguish fixed/witness acquisition; separate,
  compact selection and acquisition legends now sit below the panels.
- Thin neutral legend frames, bold measured-difference labels and light dotted
  grids improve reading at final column width. Line markers/styles and pale
  uncertainty bands remain distinct, following BatchER's line-plot conventions.
- Means, intervals, axes' scientific definitions and bar zero baselines are
  preserved. No data, effect direction or method ranking is changed to imitate
  a reference's visual emphasis. The original report and all four generated
  tables remain byte-identical; there are no new model or policy runs.

The PNG previews and vector PDF/SVG outputs are regenerated by
scripts/report_e010.py. Current validation is recorded separately in
results/E010/reference-style-validation.json; prior checks remain historical.
