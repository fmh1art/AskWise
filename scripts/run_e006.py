from pathlib import Path
from itertools import product
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from a2.worlds import sales_task,Problem
from a2.joint_cost import run_joint,tiny_optimal
root=Path(__file__).resolve().parents[1];records=[];tiny=[];start=time.monotonic()
for cost in [0.1,1,10]:
    worlds=list(product([0,1],repeat=2))
    opts={str(g):tiny_optimal(worlds,cost,g) for g in [False,True]}
    empirical={}
    for policy in ['ask_first','witness_split','certificate']:
        rr=[]
        for labels in product([0,1],repeat=4):
            for true in range(4):
                r=run_joint(worlds,lambda i:labels[i],lambda q:worlds[true][q],cost,policy)
                assert r['answer']==labels[true];rr.append(r['cost'])
        empirical[policy]=sum(rr)/len(rr)
        assert empirical[policy]+1e-9>=opts[str(policy!='ask_first')]['expected_cost']
    tiny.append({'question_cost':cost,'optima':opts,'policies':empirical})
    for family in ['top_region','customer_count','threshold_count']:
        for seed in range(100):
            p=sales_task(seed,family)
            for policy in ['ask_first','witness_split','certificate']:
                rr=[]
                for true in range(16):
                    r=run_joint(p.worlds,lambda i:p.answers[i],lambda q:p.worlds[true][q],cost,policy)
                    assert r['answer']==p.answers[true];rr.append(r)
                records.append({'question_cost':cost,'family':family,'seed':seed,'policy':policy,**{k:sum(r[k] for r in rr)/16 for k in ['cost','questions','executions']}})
out=root/'results/E006';out.mkdir(exist_ok=True)
(out/'per_task.json').write_text(json.dumps(records,indent=2)+'\n')
summary={str(c):{p:{k:sum(r[k] for r in records if r['question_cost']==c and r['policy']==p)/300 for k in ['cost','questions','executions']} for p in ['ask_first','witness_split','certificate']} for c in [0.1,1,10]}
(out/'summary.json').write_text(json.dumps({'summary':summary,'tiny_exact':tiny},indent=2)+'\n')
print(json.dumps({'seconds':time.monotonic()-start,'summary':summary,'tiny_exact':tiny},indent=2))
