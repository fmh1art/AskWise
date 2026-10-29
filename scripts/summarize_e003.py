from pathlib import Path
import json,collections
import numpy as np
root=Path(__file__).resolve().parents[1]
data=Path('/data01/fanmeihao-data/A2-research/E003')
plan=json.loads((root/'experiments/E003-plan.json').read_text())
report={'planned_per_model':plan['n'],'models':{},'complete':True}
for model in ['doubao_seed2_lite','gpt5_6_sol_hydra']:
    records=[]
    for idx in plan['ids']:
        p=data/model/(str(idx)+'.json')
        if p.exists():records.append(json.loads(p.read_text()))
    complete=len(records)==plan['n'];report['complete']&=complete
    groups=collections.defaultdict(list)
    for r in records:
        rr={'id':r['id'],'db_id':r['db_id'],'status':r['status']}
        for method in ['stable','observed']:
            for metric in ['recall','precision','all_found']:
                rr[method+'_'+metric]=float(r.get('metrics',{}).get(method,{}).get(metric,0))
        groups[r['db_id']].append(rr)
    flat=[r for g in groups.values() for r in g]
    metrics={k:sum(r[k] for r in flat)/len(flat) for k in ['stable_recall','observed_recall','stable_precision','observed_precision','stable_all_found','observed_all_found']} if flat else {}
    bootstrap=None
    if complete and len(groups)>1:
        rng=np.random.default_rng(20261029);dbs=list(groups);deltas=[]
        for _ in range(2000):
            rows=[r for i in rng.integers(0,len(dbs),len(dbs)) for r in groups[dbs[i]]]
            deltas.append(np.mean([r['stable_recall']-r['observed_recall'] for r in rows]))
        bootstrap={'unit':'database','n_clusters':len(dbs),'replicates':2000,'delta_recall_percentile95':np.quantile(deltas,[0.025,0.975]).tolist()}
    report['models'][model]={'completed':len(records),'failed':sum(r['status']!='ok' for r in records),'actual_models':sorted({r.get('model','unknown') for r in records}),
      'metrics':metrics,'uncertainty':bootstrap,'tokens':sum(r.get('usage',{}).get('total_tokens',0) for r in records)}
out=root/'results/E003';out.mkdir(exist_ok=True)
(out/('summary.json' if report['complete'] else 'partial.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
