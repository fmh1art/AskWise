from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from a2.worlds import sales_task
from a2.relevance import audit_trace

root = Path(__file__).resolve().parents[1]
methods = ['ec2', 'optimal', 'fixed', 'random', 'answer_entropy', 'repair_first']
report = {m: {'questions': 0, 'irrelevant_questions': 0, 'episodes': 0, 'episodes_with_irrelevance': 0} for m in methods}
for family in ['top_region', 'customer_count', 'threshold_count']:
    for seed in range(100):
        p = sales_task(seed, family)
        for m in methods:
            r = report[m]
            for true in range(len(p.worlds)):
                trace = p.run(true, m, 20261029+seed)['trace']
                audit = audit_trace(p, true, trace)
                bad = sum(not x['relevant'] for x in audit)
                r['questions'] += len(audit)
                r['irrelevant_questions'] += bad
                r['episodes'] += 1
                r['episodes_with_irrelevance'] += bool(bad)
out = root/'results/E008'
out.mkdir(exist_ok=True)
(out/'relevance-audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
