from pathlib import Path
import sys, time, json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from a2.worlds import sales_task
from a2.binary_policy import run_binary

root = Path(__file__).resolve().parents[1]
records = []
methods = [('four_cell', 'fixed', False), ('four_cell', 'witness', False),
           ('partition', 'fixed', False), ('partition', 'witness', False),
           ('four_cell', 'witness', True)]
for family in ['top_region', 'customer_count', 'threshold_count']:
    for seed in range(100):
        p = sales_task(seed, family)
        if family == 'top_region':
            labels = [int(('East',) in ans) for ans in p.answers]
        else:
            threshold = 6 if family == 'customer_count' else 5
            labels = [int(ans[0][0] >= threshold) for ans in p.answers]
        for bound, acquisition, immediate in methods:
            name = 'immediate_witness' if immediate else bound+'_'+acquisition
            start = time.perf_counter()
            runs = [run_binary(p.worlds, lambda i: labels[i], lambda q: p.worlds[true][q],
                               bound=bound, acquisition=acquisition, immediate=immediate)
                    for true in range(16)]
            assert all(r['answer'] == labels[true] for true, r in enumerate(runs))
            records.append({'family': family, 'seed': seed, 'method': name,
                            'executions': sum(r['executions'] for r in runs)/16,
                            'questions': sum(r['questions'] for r in runs)/16,
                            'policy_seconds': time.perf_counter()-start})
    print(family, 'complete', flush=True)
out = root/'results/E009'
out.mkdir(exist_ok=True)
summary = {}
for name in sorted({r['method'] for r in records}):
    rows = [r for r in records if r['method'] == name]
    summary[name] = {k: sum(r[k] for r in rows)/len(rows) for k in ['executions', 'questions', 'policy_seconds']}
    summary[name]['cost_sensitivity'] = {str(c): summary[name]['executions']+c*summary[name]['questions'] for c in [0.1, 1, 10]}
(out/'per_task.json').write_text(json.dumps(records, indent=2)+'\n')
(out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2), flush=True)
