"""Generate auditable tables and publication figures from saved measurements."""
from pathlib import Path
from itertools import product
from collections import defaultdict
import sys, json, hashlib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from a2.evaluation import METHODS
from a2.binary_bounds import comparison_interval
from a2.binary_policy import partition_lower
from a2.relevance import witness

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/E010'
PAPER = ROOT.parent/'A2-paper'
FIG = PAPER/'figures'
TABLE = PAPER/'tables'
DATA = Path('/data01/fanmeihao-data/A2-research')
FIG.mkdir(exist_ok=True); TABLE.mkdir(exist_ok=True)
LABEL = {'anchor':'Anchor answer', 'ask_all':'Ungated ask-all', 'full_ec2':'Full EC2',
         'full_relevant_ec2':'Full relevant EC2', 'exact_fixed':'Exact / fixed',
         'exact_witness':'Exact / witness', 'partition_fixed':'Partition / fixed',
         'partition_witness':'Partition / witness', 'immediate_fixed':'Immediate / fixed',
         'immediate_witness':'Immediate / witness'}
COLORS = ['#999999','#555555','#56B4E9','#0072B2','#E69F00','#D55E00','#CC79A7','#882255','#009E73','#332288']
MARKERS = ['x','+','s','D','^','v','<','>','o','P']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':9,
                     'axes.titlesize':10,'legend.fontsize':7,'xtick.labelsize':8,'ytick.labelsize':8,
                     'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
                     'axes.spines.top':False,'axes.spines.right':False})
artifacts = []
def save(fig, name):
    for ext in ('pdf','svg','png'):
        p = FIG/(name+'.'+ext)
        fig.savefig(p, bbox_inches='tight', dpi=220)
        artifacts.append(str(p.relative_to(PAPER)))
    plt.close(fig)

rows = json.loads((OUT/'per_task.json').read_text())
fresh = [r for r in rows if r['cohort']=='fresh_sales']
stress = [r for r in rows if r['cohort']=='stress']
seeds = sorted({r['seed'] for r in fresh})
rng = np.random.default_rng(20261029)
sample = rng.integers(0, len(seeds), size=(2000,len(seeds)))
metrics = ['accuracy','executions','questions','irrelevant','unproved','stop_certificate','cost1','cost10','cpu_ms']
summary = {}; boot = {}; seed_values = {}
for method in METHODS:
    rr = [r for r in fresh if r['method']==method]
    values = {k:np.array([np.mean([r[k] for r in rr if r['seed']==s]) for s in seeds]) for k in metrics}
    seed_values[method] = values
    b = {k:v[sample].mean(axis=1) for k,v in values.items()}
    boot[method] = b
    summary[method] = {k:{'mean':float(v.mean()),'ci95':np.quantile(b[k],[.025,.975]).tolist()} for k,v in values.items()}
    for key in ['irrelevant','unproved']:
        rate = values[key].mean()/values['questions'].mean() if values['questions'].mean() else None
        bc = np.divide(b[key],b['questions'],out=np.full(2000,np.nan),where=b['questions']>0)
        summary[method][key+'_rate'] = {'mean':rate,'ci95':np.nanquantile(bc,[.025,.975]).tolist() if rate is not None else None}
    summary[method]['tasks'] = len(rr)
    summary[method]['episodes'] = 16*len(rr)

# Main table: exactly 10 configurations and 10 columns (method + 9 metrics).
lines = [r'\begin{table*}[t]',r'\centering\small',r'\setlength{\tabcolsep}{3.2pt}',
         r'\begin{tabular}{lrrrrrrrrr}',r'\toprule',
         r'Configuration & Acc.\% & $E$ & $Q$ & Irr.\% & Unpr.\% & Cert.\% & $E+Q$ & $E+10Q$ & ms \\',r'\midrule']
for index, m in enumerate(METHODS):
    s = summary[m]
    vals = [100*s['accuracy']['mean'],s['executions']['mean'],s['questions']['mean'],
            None if s['irrelevant_rate']['mean'] is None else 100*s['irrelevant_rate']['mean'],
            None if s['unproved_rate']['mean'] is None else 100*s['unproved_rate']['mean'],
            100*s['stop_certificate']['mean'],s['cost1']['mean'],s['cost10']['mean'],s['cpu_ms']['mean']]
    texts = ['--' if x is None else f'{x:.3f}' if j==8 else f'{x:.2f}' for j,x in enumerate(vals)]
    lines.append(LABEL[m]+' & '+' & '.join(texts)+r' \\')
    if index==3: lines.append(r'\midrule')
lines += [r'\bottomrule',r'\end{tabular}',
          r'\caption{Ten fixed configurations on 120 fresh-seed sales tasks (1,920 hidden-world episodes per row). $E$: counted executions; $Q$: questions. Irr. and Unpr. are question-conditional rates of truly irrelevant questions and questions lacking an observed local witness; a dash means no questions. Cert. is the valid stopping-certificate rate. ms measures policy computation with cached truth labels, excluding SQL construction and auditing. Costs are hypothetical weights. Paired seed-cluster intervals appear in the figures and machine-readable report.}',
          r'\label{tab:main-expanded}',r'\end{table*}']
(TABLE/'main-expanded.tex').write_text('\n'.join(lines)+'\n')

# Frontier and cost sensitivity use precisely the same measured E,Q pairs.
fig, ax = plt.subplots(1,2,figsize=(7.1,3.1),layout='constrained')
for j,m in enumerate(METHODS):
    s = summary[m]; x = s['executions']['mean']; y = s['questions']['mean']
    ci = s['executions']['ci95']; qi = s['questions']['ci95']
    ax[0].errorbar(x,y,xerr=[[max(0,x-ci[0])],[max(0,ci[1]-x)]],
                   yerr=[[max(0,y-qi[0])],[max(0,qi[1]-y)]],fmt=MARKERS[j],color=COLORS[j],
                   label=LABEL[m],capsize=2,markersize=5,alpha=.85)
ratios = np.logspace(-2,2,100)
for m in ['full_relevant_ec2','exact_fixed','partition_fixed','immediate_fixed','immediate_witness']:
    j = METHODS.index(m); s = summary[m]
    costs = s['executions']['mean']+ratios*s['questions']['mean']
    bc = boot[m]['executions'][:,None]+ratios*boot[m]['questions'][:,None]
    lo,hi = np.quantile(bc,[.025,.975],axis=0)
    ax[1].plot(ratios,costs,color=COLORS[j],linestyle=['-','--',':','-.','-'][['full_relevant_ec2','exact_fixed','partition_fixed','immediate_fixed','immediate_witness'].index(m)],label=LABEL[m])
    ax[1].fill_between(ratios,lo,hi,color=COLORS[j],alpha=.08)
ax[0].set(xlabel='Counted executions, E',ylabel='Questions, Q',title='(a) Cost and interaction')
zoom=ax[0].inset_axes([.08,.34,.53,.44])
for m in METHODS[3:]:
    j=METHODS.index(m);s=summary[m];x=s['executions']['mean'];y=s['questions']['mean']
    lo,hi=s['executions']['ci95'];ql,qh=s['questions']['ci95']
    zoom.errorbar(x,y,xerr=[[x-lo],[hi-x]],yerr=[[y-ql],[qh-y]],fmt=MARKERS[j],color=COLORS[j],capsize=1,markersize=3)
zoom.set(xlim=(12.7,16.2),ylim=(.68,.98),title='Strict policies (zoom)',xticks=[13,14,15,16],yticks=[.7,.8,.9])
zoom.title.set_fontsize(6.5);zoom.tick_params(labelsize=6)
ax[1].set(xscale='log',yscale='log',xlabel='Question / execution cost, c',ylabel='E + cQ',title='(b) Strict-policy sensitivity')
ax[1].legend(loc='upper left',fontsize=6.5)
fig.legend(*ax[0].get_legend_handles_labels(),loc='outside lower center',ncol=5,fontsize=6.6,frameon=False)
save(fig,'cost_frontier')

# Paired effects are case averages; three panels retain the task families.
families = ['top_region','customer_count','threshold_count']
fig, ax = plt.subplots(1,3,figsize=(7.1,2.7),layout='constrained',sharey=True)
paired = []
for a,family in zip(ax,families):
    points = []
    for seed in seeds:
        arow = next(r for r in fresh if r['family']==family and r['seed']==seed and r['method']=='exact_fixed')
        brow = next(r for r in fresh if r['family']==family and r['seed']==seed and r['method']=='immediate_witness')
        delta = arow['executions']-brow['executions']; points.append(delta)
        paired.append({'family':family,'seed':seed,'delta_executions':delta})
    jitter = np.random.default_rng(42).uniform(-.14,.14,len(points))
    a.scatter(jitter,points,s=12,alpha=.65,color='#0072B2')
    a.axhline(0,color='gray',linestyle='--',linewidth=.8)
    ci = np.quantile(np.array(points)[sample].mean(axis=1),[.025,.975]); mean = np.mean(points)
    a.errorbar(.32,mean,yerr=[[mean-ci[0]],[ci[1]-mean]],fmt='D',color='#D55E00',capsize=4)
    a.set(xlim=(-.25,.55),xticks=[],title=family.replace('_',' ').title())
ax[0].set_ylabel('Executions: exact fixed − immediate witness')
save(fig,'paired_execution')

# Descriptive stress heatmaps; repeated truth maps are not independent evidence.
sf = ['constant','single_bit','nuisance_xor','rare_conjunction','threshold','intent_branch']
fig, ax = plt.subplots(1,2,figsize=(7.1,4.1),layout='constrained')
for a,key,title in zip(ax,['accuracy','irrelevant'],['(a) Wrong answers (%)','(b) Irrelevant questions (%)']):
    matrix = []
    for m in METHODS:
        row = []
        for f in sf:
            rr = [r for r in stress if r['method']==m and r['family']==f]
            if key=='accuracy': value = 100*(1-np.mean([r[key] for r in rr]))
            else:
                denom = sum(r['questions'] for r in rr)
                value = 100*sum(r[key] for r in rr)/denom if denom else np.nan
            row.append(value)
        matrix.append(row)
    matrix = np.array(matrix)
    im = a.imshow(matrix,vmin=0,vmax=100,cmap='cividis',aspect='auto')
    for y,x in np.ndindex(matrix.shape):
        v = matrix[y,x]
        a.text(x,y,'–' if np.isnan(v) else f'{v:.0f}',ha='center',va='center',fontsize=7,color='#555555' if np.isnan(v) else ('white' if v<55 else 'black'))
    a.set(xticks=range(6),xticklabels=['Const.','Single','XOR','AND','Thresh.','Branch'],title=title)
    a.tick_params(axis='x',labelrotation=45)
    a.set_yticks(range(10),[LABEL[m] for m in METHODS] if a is ax[0] else ['']*10)
fig.colorbar(im,ax=ax,shrink=.7,label='Percent')
save(fig,'stress_panel')

# Existing scaling evidence; no extrapolated enumeration times.
scaling = json.loads((ROOT/'results/E007/scaling.json').read_text())['rows']
ns = sorted({r['n_repairs'] for r in scaling})
fig,ax = plt.subplots(1,2,figsize=(7.1,2.7),layout='constrained')
for key,label,color,marker in [('compiled_seconds','Compiled score messages','#0072B2','o'),('enumerated_seconds','Explicit enumeration','#D55E00','s')]:
    xx=[]; yy=[]; low=[]; high=[]
    for n in ns:
        v=[r[key] for r in scaling if r['n_repairs']==n and key in r]
        if v: xx.append(n); yy.append(np.median(v)); low.append(min(v)); high.append(max(v))
    ax[0].plot(xx,yy,marker=marker,color=color,label=label)
    ax[0].fill_between(xx,low,high,color=color,alpha=.15)
ax[0].set(xscale='log',yscale='log',xlabel='Repair variables',ylabel='Seconds',title='(a) Root inference time')
ax[0].legend(frameon=False)
ax[1].plot(ns,[np.median([r['message_states'] for r in scaling if r['n_repairs']==n]) for n in ns],'o-',color='#0072B2',label='Materialized message states')
ax[1].plot(ns,[2.**(n+1) for n in ns],'s--',color='#999999',label='Implicit possible worlds')
ax[1].set(yscale='log',xlabel='Repair variables',ylabel='Count',title='(b) Declared affine-score family')
ax[1].legend(frameon=False)
save(fig,'structured_scaling')

# Exact finite partial-map diagnostic; all worlds/labels below are artificial.
worlds = tuple(product((0,1),repeat=3))
bound_groups = defaultdict(lambda: {'states':0,'exact':0,'partition':0,'slack_sum':0.0})
for partial in product((None,0,1),repeat=8):
    known={i:y for i,y in enumerate(partial) if y is not None}
    g=bound_groups[len(known)];g['states']+=1
    exact={}; relax={}
    for q,r in [(0,1),(0,2),(1,2),(1,0),(2,0),(2,1)]:
        exact[q,r]=comparison_interval(worlds,range(8),known,q,r)[0]
        relax[q,r]=partition_lower(worlds,range(8),known,q,r)/8
        assert exact[q,r] >= relax[q,r]
        g['slack_sum']+=exact[q,r]-relax[q,r]
    eligible=[q for q in range(3) if witness(worlds,range(8),known,q) is not None]
    for name,scores in [('exact',exact),('partition',relax)]:
        g[name]+=any(all(scores[q,r]>=0 for r in range(3) if r!=q) for q in eligible)
bound_rows=[{'observed':k,**g,'exact_rate':g['exact']/g['states'],'partition_rate':g['partition']/g['states'],
             'mean_slack':g['slack_sum']/(6*g['states'])} for k,g in sorted(bound_groups.items())]
fig,ax=plt.subplots(1,2,figsize=(7.1,2.7),layout='constrained')
for key,label,color,marker in [('exact_rate','Exact four-cell','#D55E00','o'),('partition_rate','Partition relaxation','#0072B2','s')]:
    ax[0].plot([r['observed'] for r in bound_rows],[100*r[key] for r in bound_rows],marker=marker,color=color,label=label)
ax[0].set(xlabel='Observed labels out of 8',ylabel='States certifying a witnessed maximum (%)',title='(a) Action certificates',ylim=(-2,103))
ax[0].legend(frameon=False)
ax[1].plot([r['observed'] for r in bound_rows],[r['mean_slack'] for r in bound_rows],'o-',color='#009E73')
ax[1].set(xlabel='Observed labels out of 8',ylabel='Mean lower-bound gap (edge-count units)',title='(b) Relaxation slack')
save(fig,'bound_certificates')

# Real-model results: purely cached measurements; no new API calls.
plan=json.loads((ROOT/'experiments/E003-plan.json').read_text())
models={}
for model in ['doubao_seed2_lite','gpt5_6_sol_hydra']:
    models[model]=[json.loads((DATA/'E003'/model/(str(i)+'.json')).read_text()) for i in plan['ids']]
dbs=sorted({r['db_id'] for r in models['doubao_seed2_lite']})
db_sample=np.random.default_rng(20261029).integers(0,len(dbs),size=(2000,len(dbs)))
model_summary={}; model_boot={}
for model,rr in models.items():
    model_summary[model]={}
    for rule in ['observed','stable']:
        result={}; b={}
        for metric in ['recall','precision','all_found','support_size']:
            totals=np.array([sum(float(r.get('metrics',{}).get(rule,{}).get(metric,0)) for r in rr if r['db_id']==db) for db in dbs])
            counts=np.array([sum(r['db_id']==db for r in rr) for db in dbs])
            values=totals[db_sample].sum(axis=1)/counts[db_sample].sum(axis=1)
            b[metric]=values
            result[metric]={'mean':float(totals.sum()/counts.sum()),'ci95':np.quantile(values,[.025,.975]).tolist()}
        result.update(n=len(rr),failed=sum(r['status']!='ok' for r in rr),
                      generated=np.mean([r.get('metrics',{}).get('n_queries',0) for r in rr]).item(),
                      valid_sql_rate=sum(r.get('metrics',{}).get('n_valid',0) for r in rr)/sum(r.get('metrics',{}).get('n_queries',0) for r in rr),
                      tokens_per_task=sum(r.get('usage',{}).get('total_tokens',0) for r in rr)/len(rr),
                      latency_p50=float(np.median([r['elapsed_seconds'] for r in rr])),
                      latency_p90=float(np.quantile([r['elapsed_seconds'] for r in rr],.9)))
        model_summary[model][rule]=result;model_boot[model,rule]=b

lines=[r'\begin{table*}[t]',r'\centering\small',r'\setlength{\tabcolsep}{3.0pt}',r'\begin{tabular}{lrrrrrrrrr}',r'\toprule',
       r'Model / pruning & Rec.\% & Prec.\% & All\% & SQL\% & Gen. & Kept & Tokens & $t_{50}$ & $t_{90}$ \\',r'\midrule']
for model,name in [('doubao_seed2_lite','Doubao Lite'),('gpt5_6_sol_hydra','GPT Sol')]:
    for rule,label in [('observed','observed'),('stable','two-state')]:
        r=model_summary[model][rule]
        vals=[100*r[m]['mean'] for m in ['recall','precision','all_found']]+[100*r['valid_sql_rate'],r['generated'],r['support_size']['mean'],r['tokens_per_task'],r['latency_p50'],r['latency_p90']]
        lines.append(name+' / '+label+' & '+' & '.join(f'{v:.0f}' if j==6 else f'{v:.2f}' for j,v in enumerate(vals))+r' \\')
lines += [r'\bottomrule',r'\end{tabular}',r'\caption{Cached E003 analysis: 155 cases per model, 20 databases. Rec./Prec. measure two-state reference-signature support; All is full reference recovery. SQL is the fraction of generated queries executable in both states; Gen./Kept are mean candidate counts. Tokens and latency quantiles (seconds) describe the shared generation call, repeated here for comparison, not additional calls. Both pruning rules use exactly the same candidates.}',r'\label{tab:model-expanded}',r'\end{table*}']
(TABLE/'model-expanded.tex').write_text('\n'.join(lines)+'\n')
fig,ax=plt.subplots(1,3,figsize=(7.1,2.7),layout='constrained',sharey=True)
for a,metric,title in zip(ax,['recall','precision','all_found'],['Reference recall','Reference precision','All references recovered']):
    for j,rule in enumerate(['observed','stable']):
        means=[];lo=[];hi=[]
        for model in models:
            r=model_summary[model][rule][metric];means.append(100*r['mean']);lo.append(100*(r['mean']-r['ci95'][0]));hi.append(100*(r['ci95'][1]-r['mean']))
        a.bar(np.arange(2)+(j-.5)*.32,means,width=.30,color=['#56B4E9','#D55E00'][j],label=['Observed-state','Two-state'][j],
              yerr=[lo,hi],capsize=2,hatch=['','//'][j],alpha=.9)
    a.set(xticks=[0,1],xticklabels=['Doubao','GPT Sol'],title=title,ylim=(0,100))
ax[0].set_ylabel('Percent');ax[-1].legend(frameon=False,fontsize=6.5)
save(fig,'model_support')

fig,ax=plt.subplots(1,2,figsize=(7.1,4.4),layout='constrained',sharey=True)
database_rows=[]
for a,(model,rr) in zip(ax,models.items()):
    changes=[]
    for db in dbs:
        subset=[r for r in rr if r['db_id']==db]
        delta=np.mean([r['metrics']['stable']['recall']-r['metrics']['observed']['recall'] for r in subset])*100
        changes.append(delta);database_rows.append({'model':model,'db_id':db,'n':len(subset),'delta_recall_pp':float(delta)})
    a.hlines(range(len(dbs)),0,changes,color='#0072B2',linewidth=1.2)
    a.scatter(changes,range(len(dbs)),color='#D55E00',s=17)
    a.set(xlabel='Two-state − observed recall (pp)',title='Doubao Lite' if model.startswith('doubao') else 'GPT Sol')
ax[0].set_yticks(range(len(dbs)),dbs,fontsize=7)
ax[0].invert_yaxis()
save(fig,'database_support')

audit=json.loads((ROOT/'results/E002/audit_status.json').read_text())
summary2=json.loads((ROOT/'results/E002/summary.json').read_text())
fig,ax=plt.subplots(1,2,figsize=(7.1,3),layout='constrained')
categories=['All items','Eligible','Changed equality','Query errors','No eligible swap']
counts=[summary2['n_total'],summary2['n_ok'],summary2['n_equal_then_different'],summary2['n_error'],summary2['n_no_distinct']]
ax[0].barh(range(5),counts,color=['#999999','#0072B2','#D55E00','#CC79A7','#E69F00'])
for y,n in enumerate(counts):ax[0].text(n+12,y,str(n),va='center',fontsize=8)
ax[0].set_yticks(range(5),categories);ax[0].invert_yaxis();ax[0].set(xlim=(0,1450),xlabel='Items (nested counts)',title='(a) Audit denominators')
effects=[]
for db in sorted({r['db_id'] for r in audit}):
    rr=[r for r in audit if r['db_id']==db and r['status']=='ok']
    if rr:effects.append((db,100*sum(r['equal_observed'] and not r['equal_changed'] for r in rr)/len(rr),len(rr)))
effects.sort(key=lambda x:x[1])
ax[1].scatter(range(len(effects)),[e[1] for e in effects],s=[e[2]/3+12 for e in effects],color='#0072B2',alpha=.75)
ax[1].set(xlabel='Databases, ordered by observed effect',ylabel='Equal → different (%)',ylim=(-3,103),title='(b) Controlled-swap heterogeneity')
save(fig,'repair_audit')

paired_delta=seed_values['exact_fixed']['executions']-seed_values['immediate_witness']['executions']
paired_summary={'mean':float(paired_delta.mean()),'ci95':np.quantile(paired_delta[sample].mean(axis=1),[.025,.975]).tolist()}
model_gains={}
for model in models:
    model_gains[model]={}
    for metric in ['recall','precision','all_found']:
        delta=model_boot[model,'stable'][metric]-model_boot[model,'observed'][metric]
        model_gains[model][metric]={'mean':model_summary[model]['stable'][metric]['mean']-model_summary[model]['observed'][metric]['mean'],
                                  'ci95':np.quantile(delta,[.025,.975]).tolist()}
report={'scope':'E010 fresh-seed check and separately labeled reuse/stress diagnostics',
        'bootstrap':{'replicates':2000,'seed':20261029,'sales_clusters':40,'model_clusters':20},
        'main':summary,'models':model_summary,'paired_effects':paired,'bound_diagnostic':bound_rows,
        'paired_exact_minus_immediate_executions':paired_summary,'paired_model_support_gains':model_gains,
        'database_effects':database_rows,'figures':sorted({str(Path(p).with_suffix('')) for p in artifacts})}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
manifest={'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'per_task.json',ROOT/'results/E007/scaling.json',ROOT/'experiments/E003-plan.json',ROOT/'results/E002/audit_status.json',ROOT/'results/E002/summary.json',Path(__file__)]},
          'model_cache_sha256':{str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest() for model in models for i in plan['ids'] for p in [DATA/'E003'/model/(str(i)+'.json')]},
          'table_files':{str(p.relative_to(PAPER)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [TABLE/'main-expanded.tex',TABLE/'model-expanded.tex']},
          'figure_files':{p:hashlib.sha256((PAPER/p).read_bytes()).hexdigest() for p in artifacts},
          'new_api_requests':0,'main_table_rows':10,'main_table_columns':10,'figure_count':len(artifacts)//3}
(OUT/'report-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'main':{m:{k:summary[m][k]['mean'] for k in ['accuracy','executions','questions']} for m in METHODS},'figures':len(artifacts)//3},indent=2))
