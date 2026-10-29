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
figures include grouped cost, model, and database bars. Run scripts/run_e010.py
and scripts/report_e010.py with the project environment. The report reuses the
external E003 cache and E007 scaling data. See results/E010/analysis.md and
literature/presentation-reference-notes.md for sources and interpretation.
The manuscript cites 24 relevant scientific works; presentation references are
recorded separately.
