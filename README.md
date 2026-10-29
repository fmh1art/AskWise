# A2: Ask only questions that change the answer

Active research targeting ACL main-conference submission quality. **Research in progress; not submission-ready.**

Code and protocols live here. Manuscript: `../A2-paper`. Local datasets and raw API evidence: `/data01/fanmeihao-data/A2-research`. Credentials are read only from user-specified external YAML files and are never committed.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/run_e001.py
.venv/bin/python scripts/audit_ambiqt.py
.venv/bin/python scripts/run_e003.py --freeze-only
timeout 24h .venv/bin/python scripts/run_e003.py
```

Read `state.json`, `decisions.md`, and the current protocol before resuming. Check live processes and exact cache signatures before starting a second run. E003 stores per-item completion records and resumes without rerunning successful requests.

E001 is a synthetic finite-world experiment with 11 strategies, including EC2 and exact optimal trees. E002 is an oracle audit on AmbiQT-C plus controlled value swaps. E003 measures actual model-generated candidate support. These are distinct endpoints. Two or three task families are not independent external benchmarks. An observed-data pruning ablation is not the complete AIR system.

The original AmbiQT database and annotations remain outside this repository. Upstream: https://github.com/testzer0/AmbiQT (MIT repository; original Spider database provenance retained upstream). New code is MIT licensed. Raw model outputs are not endorsed findings; see `reviews/review-adjudication.md`.

E003 is complete: both configured APIs returned 155 verified outcomes. Two-state
reference recall is 67.74% (Doubao Lite) and 69.03% (GPT Sol); neither is a complete
semantic-coverage guarantee. See `results/E003/summary.json` for denominators,
precision, clustered uncertainty, and failures.

The user requires strict correctness and question relevance within declared
alternatives. E008 formalizes relevance using a context-matched unequal pair;
E006's weaker arbitrary-pair gate does not meet this contract. E007 supplies a
classical structured-inference baseline. E009's exact binary comparison bound
beats an older relaxation but loses on execution cost to immediate-witness
querying. These negative development results remain recorded. The substantive
algorithm and independent confirmation gate have **not** been passed.


E010 expands the evidence without new API calls: 120 fresh generated SQL tasks
and 48 descriptive stress fixtures. The revised main cost table crosses task
families and metrics with seven matched-guarantee policies (12 rows, nine columns);
all ten configurations remain in a separate contract audit. Actual model recovery
is stratified by 53 two-signature and 102 one-signature cases. Nine statistical
figures include grouped cost, model, and database bars. Regenerate the figures
and tables with .venv/bin/python scripts/report_e010.py; this does not rerun
policies or call model APIs. The report reuses the
external E003 cache and E007 scaling data. See results/E010/analysis.md and
literature/presentation-reference-notes.md for sources and interpretation.
The manuscript cites 24 relevant scientific works; presentation references are
recorded separately.

The plot-polish revision applies a shared publication style to all nine figures,
separates selection/acquisition legends, adds measured subgroup difference
labels, and exposes the cost crossover using excess cost. Numeric results and
tables are unchanged. See results/E010/presentation-validation.json for the
current artifact and compiled-PDF checks.

The manuscript expansion adds a single-column overview and a double-column
algorithm framework. Following the user's explicit image-model request, the
active illustrations are now PNGs generated with the built-in image-generation
tool. Five illustration calls produced the selected pair; actual initial and
revision prompts are saved in A2-paper/figures/prompts. The overview prioritizes
an intuitive example and the framework preserves the algorithm's control flow.
Earlier vector assets and scripts/draw_concept_figures.py remain archived.
The ten-page main draft has six experimental subsections and seventeen PDF
pages in total. It is an expanded working version for later trimming, not a
page-limit-compliant submission. Existing measured outputs, tables and nine
statistical plots remain unchanged; explanatory diagrams have a separate
manifest. Current manuscript checks and selected-image provenance are in
results/E010/imagegen-figure-validation.json and imagegen-figure-manifest.json
in the same directory; manuscript-expansion-validation.json records the previous
vector version. The user's complete A2
requirements are also maintained in AutoResearchSkills at
docs/requirements/a2-2026-10-29.md, with reusable guidance in the related Skills.
