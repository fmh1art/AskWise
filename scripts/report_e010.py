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
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, FixedLocator, FuncFormatter
from matplotlib.colors import LinearSegmentedColormap
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
# The current manuscript's Figure 6 is the visual reference for every plot:
# sans-serif bold labels, purple solid/hatched pairs, thin boxed axes and
# compact lower legends. Keep its exact palette and rendering unchanged.
plt.rcParams.update({'font.family':'DejaVu Sans','mathtext.fontset':'dejavusans',
                     'font.size':9,'axes.labelsize':9,'axes.titlesize':9.5,
                     'legend.fontsize':8,'xtick.labelsize':8,'ytick.labelsize':8,
                     'axes.titlelocation':'center','axes.titleweight':'bold',
                     'axes.labelweight':'bold',
                     'axes.linewidth':.6,'axes.edgecolor':'#292929',
                     'axes.labelcolor':'#171717','text.color':'#171717',
                     'xtick.color':'#292929','ytick.color':'#292929',
                     'xtick.major.width':.6,'ytick.major.width':.6,
                     'xtick.major.size':2.5,'ytick.major.size':2.5,
                     'xtick.major.pad':3,'ytick.major.pad':3,
                     'lines.linewidth':1.4,'lines.markersize':4.5,
                     'hatch.linewidth':.45,'legend.handlelength':1.6,
                     'legend.columnspacing':1.3,'legend.handletextpad':.5,
                     'legend.frameon':True,'legend.fancybox':False,
                     'legend.edgecolor':'#D0D0D0','legend.facecolor':'white',
                     'legend.framealpha':.95,'legend.borderpad':.4,
                     'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
                     'svg.hashsalt':'a2-publication-figures',
                     'axes.spines.top':True,'axes.spines.right':True})
PRUNE_COLOR={'observed':'#DDD0EF','stable':'#4C1190'}
PRUNE_HATCH={'observed':'//////','stable':''}
SELECTION_COLOR={'full':'#BEA5D7','exact':PRUNE_COLOR['stable'],
                 'partition':'#9A77BB','immediate':'#74479D'}
INK='#292929'
ERROR_STYLE={'elinewidth':.65,'capsize':1.5,'capthick':.65,'ecolor':INK}
def grid(ax,axis='y'):
    ax.set_axisbelow(True)
    ax.grid(axis=axis,color='#DCDCDC',linewidth=.4,linestyle=(0,(2,2)))

def panel(ax,letter,title):
    ax.set_title(f'({letter}) {title}',pad=6)

artifacts = []
def save(fig, name):
    for ext in ('pdf','svg','png'):
        p = FIG/(name+'.'+ext)
        metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else ({'Date':None} if ext=='svg' else None)
        fig.savefig(p,bbox_inches='tight',pad_inches=.035,dpi=300,metadata=metadata)
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
          r'\caption{Execution and interaction costs under strict answer/relevance guarantees. Bold marks the lowest mean cost within each row.}',
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
          r'\caption{Contract violations across ten configurations (episode and question counts).}',
          r'\label{tab:contract-audit}',r'\end{table*}']
(TABLE/'contract-audit.tex').write_text('\n'.join(lines)+'\n')

# Multiple task clusters; color encodes selection, hatch acquisition.
POLICY_COLOR=[SELECTION_COLOR[k] for k in
              ['full','exact','exact','partition','partition','immediate','immediate']]
POLICY_HATCH=['','',PRUNE_HATCH['observed'],'',PRUNE_HATCH['observed'],'',PRUNE_HATCH['observed']]
fig,axes=plt.subplots(2,2,figsize=(7.1,3.95))
fig.subplots_adjust(left=.075,right=.985,bottom=.24,top=.92,hspace=.62,wspace=.28)
x=np.arange(4)
# Extra gaps separate the three fixed/witness pairs inside each task cluster.
offsets=[-.34,-.205,-.115,.025,.115,.255,.345]
for ax,metric,letter,title,ylabel in zip(axes.flat,
        ['executions','questions','cost10','cpu_ms'],'abcd',
        ['Execution cost','User questions','Weighted total cost','Policy computation'],
        ['Executed worlds, $E$','Questions, $Q$','$C_{10}=E+10Q$','Time per episode (ms)']):
    ax.axvspan(2.54,3.50,color='#F2F3F5',zorder=0)
    high_max=0
    for j,method in enumerate(STRICT):
        entries=[family_summary[f][method][metric] for f in COHORTS]
        means=np.array([r['mean'] for r in entries]);lo=np.array([r['ci95'][0] for r in entries]);hi=np.array([r['ci95'][1] for r in entries])
        high_max=max(high_max,float(hi.max()))
        face=matplotlib.colors.to_rgba(POLICY_COLOR[j],.30) if POLICY_HATCH[j] else POLICY_COLOR[j]
        ax.bar(x+offsets[j],means,width=.078,color=face,
               hatch=POLICY_HATCH[j],edgecolor=POLICY_COLOR[j],linewidth=.4,
               yerr=np.maximum(0,np.array([means-lo,hi-means])),error_kw=ERROR_STYLE)
    ax.set(xticks=x,xticklabels=['Region','Customers','Threshold','Pooled'],
           ylabel=ylabel,xlim=(-.53,3.50),ylim=(0,high_max*1.12))
    ax.yaxis.set_major_locator(MaxNLocator(4,integer=metric in ['executions','cost10']))
    panel(ax,letter,title);grid(ax)
selection_handles=[Patch(facecolor=SELECTION_COLOR[k],edgecolor=INK,linewidth=.3,label=label)
                   for k,label in [('full','Full relevant EC2'),('exact','Exact bound'),
                                   ('partition','Partition bound'),('immediate','Immediate witness')]]
fig.legend(handles=selection_handles,loc='lower center',bbox_to_anchor=(.53,.078),
           ncol=4)
acquisition_handles=[Patch(facecolor=color,edgecolor=PRUNE_COLOR['stable'],linewidth=.4,hatch=h,label=label)
                     for color,h,label in [(PRUNE_COLOR['stable'],'', 'Fixed acquisition'),
                                           (PRUNE_COLOR['observed'],PRUNE_HATCH['observed'],'Witness acquisition')]]
fig.legend(handles=acquisition_handles,loc='lower center',bbox_to_anchor=(.53,.005),
           ncol=2)
save(fig,'cost_frontier')

# Same cost data, but plot excess relative to the cheapest policy at each c.
# This exposes the crossover that absolute costs obscure at large c.
fig,ax=plt.subplots(figsize=(3.4,2.45),layout='constrained')
ratios=np.logspace(-2,2,160)
sensitivity_methods=['full_relevant_ec2','exact_fixed','partition_fixed','immediate_fixed']
cost_curves=np.array([summary[m]['executions']['mean']+ratios*summary[m]['questions']['mean']
                      for m in sensitivity_methods])
bootstrap_curves=np.array([boot[m]['executions'][:,None]+ratios*boot[m]['questions'][:,None]
                          for m in sensitivity_methods])
cost_min=cost_curves.min(axis=0)
bootstrap_min=bootstrap_curves.min(axis=0)
for k,(m,style,label) in enumerate(zip(sensitivity_methods,['-','--',':','-.'],
                                      ['Full relevant EC2','Exact bound','Partition bound','Immediate witness'])):
    j=STRICT.index(m)
    costs=cost_curves[k]-cost_min
    lo,hi=np.quantile(bootstrap_curves[k]-bootstrap_min,[.025,.975],axis=0)
    ax.plot(ratios,costs,color=POLICY_COLOR[j],linestyle=style,label=label)
    ax.fill_between(ratios,lo,hi,color=POLICY_COLOR[j],alpha=.10,linewidth=0)
cross=(summary['exact_fixed']['executions']['mean']-summary['immediate_fixed']['executions']['mean'])/(summary['immediate_fixed']['questions']['mean']-summary['exact_fixed']['questions']['mean'])
ax.axvline(cross,color='#7A7E83',ls=(0,(2,2)),lw=.65)
ax.text(cross*.88,.52,f'$c={cross:.2f}$',rotation=90,ha='right',va='bottom',fontsize=7.5)
ax.set(xscale='log',xlabel='Question / execution cost, $c$',
       ylabel='Excess cost, $C_c-\\min C_c$',ylim=(0,None))
ax.yaxis.set_major_locator(MaxNLocator(4));grid(ax)
fig.legend(*ax.get_legend_handles_labels(),frameon=True,fontsize=7.5,
           loc='outside lower center',ncol=2)
save(fig,'cost_sensitivity')

# Paired task differences: show every seed and the uncertainty of its mean.
families = ['top_region','customer_count','threshold_count']
fig,axes=plt.subplots(1,3,figsize=(7.1,2.4),sharey=True)
fig.subplots_adjust(left=.075,right=.985,bottom=.19,top=.85,wspace=.12)
paired=[]
for a,family,letter in zip(axes,families,'abc'):
    points=[]
    for seed in seeds:
        arow=next(r for r in fresh if r['family']==family and r['seed']==seed and r['method']=='exact_fixed')
        brow=next(r for r in fresh if r['family']==family and r['seed']==seed and r['method']=='immediate_witness')
        delta=arow['executions']-brow['executions'];points.append(delta)
        paired.append({'family':family,'seed':seed,'delta_executions':delta})
    jitter=np.random.default_rng(42).uniform(-.13,.13,len(points))
    a.scatter(jitter,points,s=14,alpha=.95,color=PRUNE_COLOR['observed'],
              edgecolors=PRUNE_COLOR['stable'],linewidths=.5,zorder=3)
    a.axhline(0,color='#7A7E83',linestyle=(0,(3,2)),linewidth=.65)
    ci=np.quantile(np.array(points)[sample].mean(axis=1),[.025,.975]);mean=np.mean(points)
    a.errorbar(.39,mean,yerr=[[mean-ci[0]],[ci[1]-mean]],fmt='D',
               color=PRUNE_COLOR['stable'],capsize=3,elinewidth=.9,
               markersize=4,zorder=4)
    a.text(.96,.94,f'Mean {mean:+.2f}',transform=a.transAxes,ha='right',va='top',fontsize=8)
    a.set(xlim=(-.24,.64),xticks=[0,.39],xticklabels=['40 seeds','Mean + CI'])
    panel(a,letter,FAMILY_LABEL[family]);grid(a)
axes[0].set_ylabel('Executed worlds saved')
save(fig,'paired_execution')

# White is zero failure; gray marks an undefined question-conditional rate.
sf=['constant','single_bit','nuisance_xor','rare_conjunction','threshold','intent_branch']
fig,axes=plt.subplots(1,2,figsize=(7.1,3.45),layout='constrained',
                      gridspec_kw={'wspace':.04})
failure_cmap=LinearSegmentedColormap.from_list('a2_failure',
               ['#FFFFFF',PRUNE_COLOR['observed'],'#9665BF',PRUNE_COLOR['stable']])
failure_cmap.set_bad('#E6E8EB')
for a,key,letter,title in zip(axes,['accuracy','irrelevant'],'ab',
                              ['Wrong answers (%)','Irrelevant questions (%)']):
    matrix=[]
    for m in METHODS:
        row=[]
        for f in sf:
            rr=[r for r in stress if r['method']==m and r['family']==f]
            if key=='accuracy':value=100*(1-np.mean([r[key] for r in rr]))
            else:
                denom=sum(r['questions'] for r in rr)
                value=100*sum(r[key] for r in rr)/denom if denom else np.nan
            row.append(value)
        matrix.append(row)
    matrix=np.array(matrix)
    im=a.pcolormesh(np.arange(-.5,6,1),np.arange(-.5,10,1),
                    np.ma.masked_invalid(matrix),vmin=0,vmax=100,cmap=failure_cmap,
                    rasterized=False)
    a.set(xlim=(-.5,5.5),ylim=(9.5,-.5))
    for y,x in np.ndindex(matrix.shape):
        v=matrix[y,x]
        a.text(x,y,'–' if np.isnan(v) else f'{v:.0f}',ha='center',va='center',
               fontsize=7.5,color='white' if v>=65 else INK)
    a.set(xticks=range(6),xticklabels=['Const.','Single','XOR','AND','Thr.','Branch'])
    a.tick_params(length=0,axis='both',pad=4)
    a.set_yticks(range(10),[LABEL[m] for m in METHODS] if a is axes[0] else ['']*10)
    a.set_xticks(np.arange(-.5,6,1),minor=True);a.set_yticks(np.arange(-.5,10,1),minor=True)
    a.tick_params(which='minor',length=0);a.grid(which='minor',color='#D7DADD',linewidth=.4)
    a.axhline(2.5,color='#888D92',linewidth=.8)
    panel(a,letter,title)
colorbar=fig.colorbar(im,ax=axes,shrink=.82,pad=.02,aspect=28,
                      ticks=[0,25,50,75,100],label='Rate (%)')
colorbar.solids.set_rasterized(False)
save(fig,'stress_panel')

# Existing scaling evidence; no extrapolated enumeration times.
scaling=json.loads((ROOT/'results/E007/scaling.json').read_text())['rows']
ns=sorted({r['n_repairs'] for r in scaling})
fig,axes=plt.subplots(1,2,figsize=(7.1,2.6),layout='constrained')
for key,label,color,marker,style in [
        ('compiled_seconds','Compiled messages',PRUNE_COLOR['stable'],'o','-'),
        ('enumerated_seconds','Explicit enumeration',SELECTION_COLOR['partition'],'s','--')]:
    xx=[];yy=[];low=[];high=[]
    for n in ns:
        v=[r[key] for r in scaling if r['n_repairs']==n and key in r]
        if v:xx.append(n);yy.append(np.median(v));low.append(min(v));high.append(max(v))
    axes[0].plot(xx,yy,marker=marker,color=color,ls=style,label=label,
                 markerfacecolor='white',markeredgewidth=.8)
    axes[0].fill_between(xx,low,high,color=color,alpha=.15,linewidth=0)
axes[0].set(xscale='log',yscale='log',xlabel='Repair variables',ylabel='Runtime (s)')
axes[0].xaxis.set_major_locator(FixedLocator([8,16,32,64,128,256]))
axes[0].xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:g}'))
axes[0].xaxis.set_minor_locator(FixedLocator([]))
panel(axes[0],'a','Root inference time')
axes[0].legend(loc='upper center',bbox_to_anchor=(.5,-.31),fontsize=8);grid(axes[0])
axes[1].plot(ns,[np.median([r['message_states'] for r in scaling if r['n_repairs']==n]) for n in ns],
             'o-',color=PRUNE_COLOR['stable'],label='Materialized states',markerfacecolor='white')
axes[1].plot(ns,[2.**(n+1) for n in ns],'s--',color=SELECTION_COLOR['partition'],
             label='Implicit worlds',markerfacecolor='white')
axes[1].set(xscale='log',yscale='log',xlabel='Repair variables',ylabel='Count',
            ylim=(1,1e80),yticks=[1,1e20,1e40,1e60,1e80])
axes[1].xaxis.set_major_locator(FixedLocator([8,16,32,64,128,256]))
axes[1].xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:g}'))
axes[1].xaxis.set_minor_locator(FixedLocator([]))
panel(axes[1],'b','Declared score family');grid(axes[1])
axes[1].legend(loc='upper center',bbox_to_anchor=(.5,-.31),fontsize=8)
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
fig,axes=plt.subplots(1,2,figsize=(7.1,2.45),layout='constrained')
observed=np.array([r['observed'] for r in bound_rows])
for j,(key,label,color,hatch) in enumerate([
        ('exact_rate','Exact four-cell',PRUNE_COLOR['stable'],''),
        ('partition_rate','Partition relaxation',PRUNE_COLOR['observed'],PRUNE_HATCH['observed'])]):
    rates=np.array([100*r[key] for r in bound_rows])
    axes[0].bar(observed+(j-.5)*.36,rates,width=.31,color=color,hatch=hatch,
                edgecolor=PRUNE_COLOR['stable'],linewidth=.4,label=label)
    axes[0].text(6+(j-.5)*.36,rates[6]+2,f'{rates[6]:.1f}',ha='center',fontsize=7.5)
axes[0].set(xlabel='Observed labels (of 8)',ylabel='Certified states (%)',
            xticks=range(9),ylim=(0,110),yticks=[0,25,50,75,100])
panel(axes[0],'a','Action certificates');grid(axes[0])
axes[0].legend(loc='upper center',bbox_to_anchor=(.5,-.32),fontsize=8,ncol=2)
gap=[r['mean_slack'] for r in bound_rows]
axes[1].plot(observed,gap,'o-',color=PRUNE_COLOR['stable'],markerfacecolor='white',markeredgewidth=.9)
axes[1].fill_between(observed,0,gap,color=PRUNE_COLOR['observed'],alpha=.6,linewidth=0)
axes[1].set(xlabel='Observed labels (of 8)',ylabel='Lower-bound gap (edge units)',
            xticks=range(9),ylim=(0,None))
axes[1].yaxis.set_major_locator(MaxNLocator(4))
panel(axes[1],'b','Relaxation slack');grid(axes[1])
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
          r'\caption{Model candidate recovery (\%) by reference-signature stratum.}',
          r'\label{tab:model-expanded}',r'\end{table*}']
(TABLE/'model-expanded.tex').write_text('\n'.join(lines)+'\n')
lines=[r'\begin{table*}[!t]',r'\centering\small',r'\setlength{\tabcolsep}{5pt}',
       r'\begin{tabular}{lrrrrrrr}',r'\toprule',
       r'Model & Outcomes & Valid SQL (\%) & Generated & Kept: obs./two & Tokens & $t_{50}$ (s) & $t_{90}$ (s) \\',r'\midrule']
for model,name in [('doubao_seed2_lite','Doubao Lite'),('gpt5_6_sol_hydra','GPT Sol')]:
    a=model_summary[model]['observed'];b=model_summary[model]['stable']
    lines.append(name+f" & {a['n']} & {100*a['valid_sql_rate']:.2f} & {a['generated']:.2f} & {a['support_size']['mean']:.2f} / {b['support_size']['mean']:.2f} & {a['tokens_per_task']:.0f} & {a['latency_p50']:.2f} & {a['latency_p90']:.2f}"+r' \\')
lines += [r'\bottomrule',r'\end{tabular}',
          r'\caption{Candidate-generation resources and SQL validity, reported once per model.}',
          r'\label{tab:model-resources}',r'\end{table*}']
(TABLE/'model-resources.tex').write_text('\n'.join(lines)+'\n')
fig,axes=plt.subplots(2,3,figsize=(7.1,3.65),sharey=True)
fig.subplots_adjust(left=.095,right=.99,bottom=.235,top=.92,hspace=.50,wspace=.17)
for row,(model,name) in enumerate([('doubao_seed2_lite','Doubao Lite'),('gpt5_6_sol_hydra','GPT Sol')]):
    for col,(metric,title) in enumerate([('recall','Recall'),('precision','Precision'),('all_found','Full recovery')]):
        ax=axes[row,col]
        ax.axvspan(.56,1.44,color='#F2F3F5',zorder=0)
        highs=[]
        for j,rule in enumerate(['observed','stable']):
            data=[model_strata[model][group]['rules'][rule][metric] for group,_,_ in stratum_defs]
            means=np.array([r['mean']*100 for r in data])
            low=np.array([r['ci95'][0]*100 for r in data]);high=np.array([r['ci95'][1]*100 for r in data])
            highs.append(high)
            ax.bar(np.arange(3)+(j-.5)*.32,means,width=.275,
                   color=PRUNE_COLOR[rule],hatch=PRUNE_HATCH[rule],edgecolor=PRUNE_COLOR['stable'],linewidth=.4,
                   yerr=np.maximum(0,np.array([means-low,high-means])),error_kw=ERROR_STYLE,
                   label=['Observed-state pruning','Two-state pruning'][j])
        tick_labels=(['All','Two sig.','One sig.'] if row==0 else
                     ['All\n$n=155$','Two sig.\n$n=53$','One sig.\n$n=102$'])
        ax.set(xticks=range(3),xticklabels=tick_labels,
               ylim=(0,118),yticks=[0,25,50,75,100],xlim=(-.55,2.52))
        panel(ax,chr(97+row*3+col),title)
        if metric in ['recall','all_found']:
            cohort=model_strata[model]['distinct']['rules']
            delta=100*(cohort['stable'][metric]['mean']-cohort['observed'][metric]['mean'])
            height=max(highs[0][1],highs[1][1])+5
            ax.plot([.84,.84,1.16,1.16],[height-1.5,height,height,height-1.5],color=INK,lw=.55)
            ax.text(1,height+2,f'+{delta:.1f} pp',ha='center',va='bottom',fontsize=8,fontweight='bold',
                    color=PRUNE_COLOR['stable'])
        if metric=='all_found':
            ax.text(.84,2,'0',ha='center',va='bottom',fontsize=8,color=INK)
        grid(ax)
        if col==0:ax.set_ylabel(name+'\nScore (%)',linespacing=1.5)
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='lower center',
           bbox_to_anchor=(.54,.015),ncol=2)
save(fig,'model_support')


# Paired database bars share row order, range, sample-count labels and legend.
fig,axes=plt.subplots(1,2,figsize=(7.1,4.7),sharey=True)
fig.subplots_adjust(left=.225,right=.985,bottom=.135,top=.93,wspace=.10)
database_rows=[]
for a,(model,rr),letter in zip(axes,models.items(),'ab'):
    for k in range(0,len(dbs),2):
        a.axhspan(k-.48,k+.48,color='#F2F3F5',zorder=0)
    for j,rule in enumerate(['observed','stable']):
        means=[]
        for db in dbs:
            subset=[r for r in rr if r['db_id']==db]
            means.append(100*np.mean([r['metrics'][rule]['recall'] for r in subset]))
            if rule=='stable':
                delta=100*np.mean([r['metrics']['stable']['recall']-r['metrics']['observed']['recall'] for r in subset])
                database_rows.append({'model':model,'db_id':db,'n':len(subset),'delta_recall_pp':float(delta)})
        a.barh(np.arange(len(dbs))+(j-.5)*.36,means,height=.29,color=PRUNE_COLOR[rule],
               hatch=PRUNE_HATCH[rule],edgecolor=PRUNE_COLOR['stable'],linewidth=.35,
               label=['Observed-state pruning','Two-state pruning'][j],zorder=3)
    a.set(xlabel='Reference recall (%)',xlim=(0,103),xticks=[0,25,50,75,100])
    panel(a,letter,'Doubao Lite' if model.startswith('doubao') else 'GPT Sol');grid(a,'x')
    a.tick_params(axis='y',length=0,labelsize=7.5)
db_counts={db:sum(r['db_id']==db for r in models['doubao_seed2_lite']) for db in dbs}
axes[0].set_yticks(range(len(dbs)),[f'{db}  ({db_counts[db]})' for db in dbs])
axes[0].set_ylim(len(dbs)-.5,-.5)
fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',
           bbox_to_anchor=(.57,-.005),ncol=2,frameon=True)
save(fig,'database_support')

audit=json.loads((ROOT/'results/E002/audit_status.json').read_text())
summary2=json.loads((ROOT/'results/E002/summary.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(7.1,2.75),layout='constrained',gridspec_kw={'wspace':.07})
categories=['All items','Eligible swaps','Changed equality','Query errors','No eligible swap']
counts=[summary2['n_total'],summary2['n_ok'],summary2['n_equal_then_different'],summary2['n_error'],summary2['n_no_distinct']]
axes[0].barh(range(5),counts,height=.60,
             color=['#E6E8EB',PRUNE_COLOR['observed'],PRUNE_COLOR['stable'],PRUNE_COLOR['observed'],PRUNE_COLOR['observed']],
             hatch=['',PRUNE_HATCH['observed'],'',PRUNE_HATCH['observed'],PRUNE_HATCH['observed']],
             edgecolor=PRUNE_COLOR['stable'],linewidth=.4)
for y,n in enumerate(counts):axes[0].text(n+20,y,f'{n:,}',va='center',fontsize=8)
axes[0].axhline(2.6,color='#B6BBC0',lw=.5,ls=(0,(3,2)))
axes[0].set_yticks(range(5),categories);axes[0].invert_yaxis()
axes[0].set(xlim=(0,1490),xticks=[0,400,800,1200],xlabel='Items (nested counts)')
axes[0].tick_params(axis='y',length=0)
panel(axes[0],'a','Audit denominators');grid(axes[0],'x')
effects=[]
for db in sorted({r['db_id'] for r in audit}):
    rr=[r for r in audit if r['db_id']==db and r['status']=='ok']
    if rr:effects.append((db,100*sum(r['equal_observed'] and not r['equal_changed'] for r in rr)/len(rr),len(rr)))
effects.sort(key=lambda x:x[1])
rank=np.arange(1,len(effects)+1)
axes[1].vlines(rank,0,[e[1] for e in effects],color=PRUNE_COLOR['observed'],lw=.8)
axes[1].scatter(rank,[e[1] for e in effects],s=[e[2]/3+12 for e in effects],
                color=PRUNE_COLOR['stable'],edgecolors='white',linewidths=.45,zorder=3)
axes[1].set(xlabel='Database rank (ordered by effect)',ylabel='Equal → different (%)',
            xticks=[1,5,10,15,20],xlim=(.25,len(effects)+.75),ylim=(0,108),yticks=[0,25,50,75,100])
sizes=sorted({min(e[2] for e in effects),int(np.median([e[2] for e in effects])),max(e[2] for e in effects)})
handles=[axes[1].scatter([],[],s=n/3+12,color=PRUNE_COLOR['stable'],edgecolors='white',
                         linewidths=.45,label=str(n)) for n in sizes]
axes[1].legend(handles=handles,title='Eligible cases',title_fontsize=8,fontsize=8,
               loc='upper center',bbox_to_anchor=(.5,-.30),ncol=len(handles),
               columnspacing=.8,handletextpad=.4)
panel(axes[1],'b','Database variation');grid(axes[1])
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
