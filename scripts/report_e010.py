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


# Main comparison: matched guarantees; crossed policy and task groups.
families = ['top_region','customer_count','threshold_count']
STRICT = ['full_relevant_ec2','exact_fixed','exact_witness','partition_fixed',
          'partition_witness','immediate_fixed','immediate_witness']
COHORTS = families+['pooled']
FAMILY_LABEL = {'top_region':'Leading region','customer_count':'Customer count',
                'threshold_count':'Order threshold','pooled':'All tasks'}
family_summary = {}
for family in COHORTS:
    family_summary[family] = {}
    for method in STRICT:
        rr=[r for r in fresh if r['method']==method and (family=='pooled' or r['family']==family)]
        family_summary[family][method]={}
        for metric in ['executions','questions','cost10','cpu_ms']:
            values=np.array([np.mean([r[metric] for r in rr if r['seed']==seed]) for seed in seeds])
            family_summary[family][method][metric]={
                'mean':float(values.mean()),
                'ci95':np.quantile(values[sample].mean(axis=1),[.025,.975]).tolist()}
lines=[r'\begin{table*}[t]',r'\centering\small',r'\setlength{\tabcolsep}{4.1pt}',
       r'\begin{tabular}{llrrrrrrr}',r'\toprule',
       r' & & Full relevant & \multicolumn{2}{c}{Exact bound} & \multicolumn{2}{c}{Partition bound} & \multicolumn{2}{c}{Immediate witness} \\',
       r'\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}',
       r'Task family & Metric & EC2 & Fixed & Witness & Fixed & Witness & Fixed & Witness \\',r'\midrule']
for fi,family in enumerate(COHORTS):
    for mi,(metric,label) in enumerate([('executions',r'$E\downarrow$'),('questions',r'$Q$'),('cost10',r'$C_{10}\downarrow$')]):
        values=[family_summary[family][m][metric]['mean'] for m in STRICT]
        best=min(values)
        cells=[(r'\textbf{'+f'{v:.2f}'+'}') if metric!='questions' and abs(v-best)<1e-10 else f'{v:.2f}' for v in values]
        name=FAMILY_LABEL[family]+(' ($n=120$)' if family=='pooled' else ' ($n=40$)') if mi==0 else ''
        lines.append(name+' & '+label+' & '+' & '.join(cells)+r' \\')
    if fi<3:lines.append(r'\midrule')
lines += [r'\bottomrule',r'\end{tabular}',
          r'\caption{Execution and interaction costs under the same strict answer/relevance contract. Rows group three generated SQL families and their pooled mean; columns cross selection rule and acquisition order. $E$: executed worlds; $Q$: questions; $C_{10}=E+10Q$. Bold marks the smallest mean $E$ or $C_{10}$ within a row, including ties, not statistical significance. Candidate worlds are supplied and responses are simulated; this is not an LLM accuracy evaluation. Each family has 40 seeds and 16 hidden worlds per seed. Cluster intervals appear in Figure~\ref{fig:frontier}.}',
          r'\label{tab:main-expanded}',r'\end{table*}']
(TABLE/'main-expanded.tex').write_text('\n'.join(lines)+'\n')

# Contract checks are counts, separated from the performance comparison.
audit_summary={}
lines=[r'\begin{table*}[!t]',r'\centering\small',r'\setlength{\tabcolsep}{3.7pt}',
       r'\begin{tabular}{lrrrrrrrr}',r'\toprule',
       r' & \multicolumn{4}{c}{Fresh sales: 1,920 episodes / configuration} & \multicolumn{4}{c}{Stress: 768 episodes / configuration} \\',
       r'\cmidrule(lr){2-5}\cmidrule(lr){6-9}',
       r'Configuration & Wrong & Irr.Q & Unpr.Q & No cert. & Wrong & Irr.Q & Unpr.Q & No cert. \\',r'\midrule']
for method in METHODS:
    audit_summary[method]={}
    cells=[]
    for name,subset in [('fresh',fresh),('stress',stress)]:
        rr=[r for r in subset if r['method']==method]
        n=sum(r['episodes'] for r in rr)
        def total(metric):return int(round(sum(r[metric]*r['episodes'] for r in rr)))
        counts={'episodes':n,'wrong':n-total('accuracy'),'irrelevant':total('irrelevant'),
                'unproved':total('unproved'),'uncertified':n-total('stop_certificate'),
                'questions':total('questions')}
        audit_summary[method][name]=counts
        cells += [str(counts['wrong']),str(counts['irrelevant']) if counts['questions'] else '--',
                  str(counts['unproved']) if counts['questions'] else '--',str(counts['uncertified'])]
    lines.append(LABEL[method]+' & '+' & '.join(cells)+r' \\')
lines += [r'\bottomrule',r'\end{tabular}',
          r'\caption{Retrospective contract audit of all ten configurations. Wrong: wrong returned answers; Irr.Q: irrelevant questions; Unpr.Q: questions without an observed local witness; No cert.: returns without complete known agreement. Entries are counts, with a dash when no questions were asked. Zero errors are expected from certificate-based stopping with supplied worlds and truthful responses; they are not a measured LLM success rate. Stress fixtures include repeated truth maps.}',
          r'\label{tab:contract-audit}',r'\end{table*}']
(TABLE/'contract-audit.tex').write_text('\n'.join(lines)+'\n')

# Multiple task clusters and crossed selection/acquisition variants.
POLICY_COLOR=['#0072B2','#E69F00','#E69F00','#AA4499','#AA4499','#009E73','#009E73']
POLICY_HATCH=['','', '//','', '//','', '//']
SHORT=['Full relevant EC2','Exact / fixed','Exact / witness','Partition / fixed',
       'Partition / witness','Immediate / fixed','Immediate / witness']
fig,axes=plt.subplots(2,2,figsize=(7.1,4.65),layout='constrained')
x=np.arange(4);width=.105
for ax,metric,title,ylabel in zip(axes.flat,
        ['executions','questions','cost10','cpu_ms'],
        ['(a) Execution cost','(b) User questions','(c) Weighted total cost','(d) Policy computation'],
        ['Executed worlds, E','Questions, Q','C₁₀ = E + 10Q','Time per episode (ms)']):
    for j,method in enumerate(STRICT):
        entries=[family_summary[f][method][metric] for f in COHORTS]
        means=np.array([r['mean'] for r in entries]);lo=np.array([r['ci95'][0] for r in entries]);hi=np.array([r['ci95'][1] for r in entries])
        ax.bar(x+(j-3)*width,means,width=width*.94,label=SHORT[j],color=POLICY_COLOR[j],
               hatch=POLICY_HATCH[j],edgecolor='#333333',linewidth=.35,
               yerr=np.maximum(0,np.array([means-lo,hi-means])),error_kw={'elinewidth':.6,'capsize':1.3})
    ax.set(xticks=x,xticklabels=['Region','Customers','Threshold','All'],ylabel=ylabel,title=title,ylim=(0,None))
    ax.tick_params(axis='x',labelsize=7)
    ax.set_axisbelow(True);ax.grid(axis='y',linestyle=':',alpha=.25)
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=4,fontsize=7,frameon=False)
save(fig,'cost_frontier')

# Cost sensitivity remains available, explicitly separated from new evidence.
fig,ax=plt.subplots(figsize=(3.4,2.5),layout='constrained')
ratios=np.logspace(-2,2,100)
for m,style in [('full_relevant_ec2','-'),('exact_fixed','--'),('partition_fixed',':'),('immediate_fixed','-.')]:
    j=STRICT.index(m)
    costs=summary[m]['executions']['mean']+ratios*summary[m]['questions']['mean']
    bc=boot[m]['executions'][:,None]+ratios*boot[m]['questions'][:,None]
    lo,hi=np.quantile(bc,[.025,.975],axis=0)
    ax.plot(ratios,costs,color=POLICY_COLOR[j],linestyle=style,label=LABEL[m])
    ax.fill_between(ratios,lo,hi,color=POLICY_COLOR[j],alpha=.10)
ax.set(xscale='log',xlabel='Question / execution cost, c',ylabel='E + cQ',ylim=(0,None))
ax.legend(frameon=False,fontsize=6.5,loc='upper left')
save(fig,'cost_sensitivity')

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


# Reference-defined strata, fixed independently of model outputs.
model_strata={}
stratum_defs=[('all','All cases',lambda r:True),('distinct','Two signatures',lambda r:r['metrics']['gold_support_size']==2),
              ('invariant','One signature',lambda r:r['metrics']['gold_support_size']==1)]
for model,rr in models.items():
    model_strata[model]={}
    for name,_,condition in stratum_defs:
        cohort=[r for r in rr if condition(r)]
        model_strata[model][name]={'n':len(cohort),'db_clusters':len({r['db_id'] for r in cohort}),'rules':{}}
        for rule in ['observed','stable']:
            values={}
            counts=np.array([sum(r['db_id']==db for r in cohort) for db in dbs])
            for metric in ['recall','precision','all_found']:
                sums=np.array([sum(float(r['metrics'][rule][metric]) for r in cohort if r['db_id']==db) for db in dbs])
                denom=counts[db_sample].sum(axis=1)
                b=np.divide(sums[db_sample].sum(axis=1),denom,out=np.full(len(denom),np.nan),where=denom>0)
                values[metric]={'mean':float(sums.sum()/counts.sum()),'ci95':np.nanquantile(b,[.025,.975]).tolist()}
            model_strata[model][name]['rules'][rule]=values
# Reference-cohort membership must be identical for both model caches.
assert [[r['id'],r['metrics']['gold_support_size']] for r in models['doubao_seed2_lite']] == [[r['id'],r['metrics']['gold_support_size']] for r in models['gpt5_6_sol_hydra']]
lines=[r'\begin{table*}[t]',r'\centering\small',r'\setlength{\tabcolsep}{3.5pt}',
       r'\begin{tabular}{llrrrrrrrrr}',r'\toprule',
       r' & & \multicolumn{3}{c}{All cases ($n=155$)} & \multicolumn{3}{c}{Two signatures ($n=53$)} & \multicolumn{3}{c}{One signature ($n=102$)} \\',
       r'\cmidrule(lr){3-5}\cmidrule(lr){6-8}\cmidrule(lr){9-11}',
       r'Model & Pruning & Rec. & Prec. & Full & Rec. & Prec. & Full & Rec. & Prec. & Full \\',r'\midrule']
for mi,(model,name) in enumerate([('doubao_seed2_lite','Doubao Lite'),('gpt5_6_sol_hydra','GPT Sol')]):
    for rule,label in [('observed','Observed'),('stable','Two-state')]:
        cells=[]
        for group,_,_ in stratum_defs:
            for metric in ['recall','precision','all_found']:
                value=100*model_strata[model][group]['rules'][rule][metric]['mean']
                cells.append(f'{value:.2f}')
        lines.append((name if rule=='observed' else '')+' & '+label+' & '+' & '.join(cells)+r' \\')
    if mi==0:lines.append(r'\midrule')
lines += [r'\bottomrule',r'\end{tabular}',
          r'\caption{Actual model candidate recovery (\%). Rec.: reference recall; Prec.: reference precision; Full: complete reference recovery. Groups are defined by the number of distinct reference execution signatures across the same two data states, independently of either model. The 53 two-signature and 102 one-signature cases partition the 155 sampled cases; they are descriptive subgroups, not extra benchmarks. Both pruning rules use the same generation outputs. Resources are reported once per model in Table~\ref{tab:model-resources}.}',
          r'\label{tab:model-expanded}',r'\end{table*}']
(TABLE/'model-expanded.tex').write_text('\n'.join(lines)+'\n')
lines=[r'\begin{table*}[!t]',r'\centering\small',r'\setlength{\tabcolsep}{5pt}',
       r'\begin{tabular}{lrrrrrrr}',r'\toprule',
       r'Model & Outcomes & Valid SQL (\%) & Generated & Kept: obs./two & Tokens & $t_{50}$ (s) & $t_{90}$ (s) \\',r'\midrule']
for model,name in [('doubao_seed2_lite','Doubao Lite'),('gpt5_6_sol_hydra','GPT Sol')]:
    a=model_summary[model]['observed'];b=model_summary[model]['stable']
    lines.append(name+f" & {a['n']} & {100*a['valid_sql_rate']:.2f} & {a['generated']:.2f} & {a['support_size']['mean']:.2f} / {b['support_size']['mean']:.2f} & {a['tokens_per_task']:.0f} & {a['latency_p50']:.2f} & {a['latency_p90']:.2f}"+r' \\')
lines += [r'\bottomrule',r'\end{tabular}',
          r'\caption{Generation resources and candidate counts, recorded once per model. Generated, kept, and tokens are per-case means; kept counts compare observed/two-state pruning. SQL validity requires execution on both states and does not imply correctness. Latencies describe recorded generation calls. The same 155 calls per model serve all pruning rules and subgroup analyses.}',
          r'\label{tab:model-resources}',r'\end{table*}']
(TABLE/'model-resources.tex').write_text('\n'.join(lines)+'\n')
fig,axes=plt.subplots(2,3,figsize=(7.1,4.25),layout='constrained',sharey=True)
for row,(model,name) in enumerate([('doubao_seed2_lite','Doubao Lite'),('gpt5_6_sol_hydra','GPT Sol')]):
    for col,(metric,title) in enumerate([('recall','Reference recall'),('precision','Reference precision'),('all_found','Full reference recovery')]):
        ax=axes[row,col]
        for j,rule in enumerate(['observed','stable']):
            data=[model_strata[model][group]['rules'][rule][metric] for group,_,_ in stratum_defs]
            means=np.array([r['mean']*100 for r in data])
            low=np.array([r['ci95'][0]*100 for r in data]);high=np.array([r['ci95'][1]*100 for r in data])
            ax.bar(np.arange(3)+(j-.5)*.34,means,width=.31,
                   color=['#56B4E9','#D55E00'][j],hatch=['','//'][j],edgecolor='#333333',linewidth=.35,
                   yerr=np.maximum(0,np.array([means-low,high-means])),error_kw={'elinewidth':.75,'capsize':1.8},
                   label=['Observed-state','Two-state'][j])
        ax.set(xticks=range(3),xticklabels=['All\n155','Two sig.\n53','One sig.\n102'],ylim=(0,105),
               title='('+chr(97+row*3+col)+') '+title)
        if metric=='all_found':
            ax.text(1-.17,1.5,'0',ha='center',va='bottom',fontsize=7,color='#333333')
        ax.tick_params(axis='x',labelsize=7)
        ax.set_axisbelow(True);ax.grid(axis='y',linestyle=':',alpha=.22)
        if col==0:ax.set_ylabel(name+'\nPercent')
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=2,frameon=False)
save(fig,'model_support')


fig,ax=plt.subplots(1,2,figsize=(7.1,5.0),layout='constrained',sharey=True)
database_rows=[]
for a,(model,rr) in zip(ax,models.items()):
    for j,rule in enumerate(['observed','stable']):
        means=[]
        for db in dbs:
            subset=[r for r in rr if r['db_id']==db]
            means.append(100*np.mean([r['metrics'][rule]['recall'] for r in subset]))
            if rule=='stable':
                delta=100*np.mean([r['metrics']['stable']['recall']-r['metrics']['observed']['recall'] for r in subset])
                database_rows.append({'model':model,'db_id':db,'n':len(subset),'delta_recall_pp':float(delta)})
        a.barh(np.arange(len(dbs))+(j-.5)*.36,means,height=.34,color=['#56B4E9','#D55E00'][j],
               hatch=['','//'][j],edgecolor='#333333',linewidth=.25,label=['Observed-state','Two-state'][j])
    a.set(xlabel='Reference recall (%)',xlim=(0,100),title='Doubao Lite' if model.startswith('doubao') else 'GPT Sol')
    a.set_axisbelow(True);a.grid(axis='x',linestyle=':',alpha=.22)
ax[0].set_yticks(range(len(dbs)),dbs,fontsize=6.5);ax[0].invert_yaxis()
fig.legend(*ax[0].get_legend_handles_labels(),loc='outside lower center',ncol=2,frameon=False)
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
        'main':summary,'models':model_summary,'family_costs':family_summary,'model_strata':model_strata,'contract_audit':audit_summary,'paired_effects':paired,'bound_diagnostic':bound_rows,
        'paired_exact_minus_immediate_executions':paired_summary,'paired_model_support_gains':model_gains,
        'database_effects':database_rows,'figures':sorted({str(Path(p).with_suffix('')) for p in artifacts})}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
manifest={'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'per_task.json',ROOT/'results/E007/scaling.json',ROOT/'experiments/E003-plan.json',ROOT/'results/E002/audit_status.json',ROOT/'results/E002/summary.json',Path(__file__)]},
          'model_cache_sha256':{str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest() for model in models for i in plan['ids'] for p in [DATA/'E003'/model/(str(i)+'.json')]},
          'table_files':{str(p.relative_to(PAPER)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [TABLE/'main-expanded.tex',TABLE/'model-expanded.tex',TABLE/'contract-audit.tex',TABLE/'model-resources.tex']},
          'figure_files':{p:hashlib.sha256((PAPER/p).read_bytes()).hexdigest() for p in artifacts},
          'new_api_requests':0,'main_table_rows':12,'main_table_columns':9,'main_policy_configurations':7,'model_table_rows':4,'model_table_columns':11,'figure_count':len(artifacts)//3}
(OUT/'report-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'main':{m:{k:summary[m][k]['mean'] for k in ['accuracy','executions','questions']} for m in METHODS},'figures':len(artifacts)//3},indent=2))
