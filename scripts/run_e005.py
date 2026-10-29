from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from a2.worlds import sales_task
from a2.lazy_classes import run_lazy
root=Path(__file__).resolve().parents[1]
records=[];start=time.monotonic()
for family in ['top_region','customer_count','threshold_count']:
    for seed in range(100):
        p=sales_task(seed,family)
        for acq in ['fixed','random','comparison']:
            runs=[];t0=time.monotonic()
            for true in range(len(p.worlds)):
                r=run_lazy(p.worlds,lambda i:p.answers[i],lambda q:p.worlds[true][q],acquisition=acq,seed=20261029+seed,bound='partition')
                oracle=p.run(true,'ec2')
                expected=[t['question'] for t in oracle['trace'] if 'question' in t]
                assert r['asked']==expected and r['answer']==p.answers[true]
                runs.append(r)
            records.append({'family':family,'seed':seed,'acquisition':acq,'executions':sum(r['executions'] for r in runs)/len(runs),'questions':sum(r['questions'] for r in runs)/len(runs),'seconds':time.monotonic()-t0})
out=root/'results/E005';out.mkdir(exist_ok=True)
(out/'per_task.json').write_text(json.dumps(records,indent=2)+'\n')
summary={a:{k:sum(r[k] for r in records if r['acquisition']==a)/300 for k in ['executions','questions','seconds']} for a in ['fixed','random','comparison']}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'elapsed':time.monotonic()-start,'summary':summary},indent=2))
