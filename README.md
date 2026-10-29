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
