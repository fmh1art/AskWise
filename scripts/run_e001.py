from pathlib import Path
import json, sys, time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from a2.worlds import sales_task

root=Path(__file__).resolve().parents[1]
methods=['none','ask_all','fixed','random','world_entropy','answer_entropy','ec2','local','observed_then_repair','repair_first','optimal']
out=root/'results'/'E001'
out.mkdir(parents=True,exist_ok=True)
records=[]
start=time.monotonic()
for family in ['top_region','customer_count','threshold_count']:
    for seed in range(100):
        p=sales_task(seed,family)
        for method in methods:
            runs=[p.run(i,method,seed=20261029+seed) for i in range(16)]
            records.append({'task':p.name,'family':family,'seed':seed,'method':method,
                'accuracy':sum(r['correct'] for r in runs)/16,
                'questions':sum(r['questions'] for r in runs)/16,
                'invariant':p.invariant(tuple(range(16)))})
(out/'per_task.json').write_text(json.dumps(records,indent=2)+'\n')
summary={}
for family in ['all','top_region','customer_count','threshold_count']:
    summary[family]={}
    for method in methods:
        rr=[r for r in records if r['method']==method and (family=='all' or r['family']==family)]
        summary[family][method]={k:sum(r[k] for r in rr)/len(rr) for k in ['accuracy','questions']}
        summary[family][method]['n_tasks']=len(rr)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'seconds':time.monotonic()-start,'summary':summary['all']},indent=2))
