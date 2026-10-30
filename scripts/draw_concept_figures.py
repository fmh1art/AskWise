"""Editable explanatory figures; constructed example, not experimental results."""
from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'AskWise_Tex'/'figures'
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix',
                     'font.size':8,'pdf.fonttype':42,'svg.fonttype':'none',
                     'svg.hashsalt':'a2-concept-figures'})
INK='#28333F'
BLUE='#587FA3'; PURPLE='#79669B'; GREEN='#4A917E'; OCHRE='#CDA257'
files={}
def text(ax,x,y,s,size=8,color=INK,weight='normal',ha='center',va='center'):
    return ax.text(x,y,s,fontsize=size,color=color,weight=weight,ha=ha,va=va,linespacing=1.25)
def box(ax,x,y,w,h,label,fill='#F2F4F6',edge='#9CA6B0',size=8,weight='normal'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.0,rounding_size=1.2',
                              facecolor=fill,edgecolor=edge,linewidth=.65,zorder=2))
    text(ax,x+w/2,y+h/2,label,size,weight=weight)
def arrow(ax,points,color=INK,dashed=False):
    for a,b in zip(points[:-2],points[1:-1]):
        ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=.75,
                linestyle='--' if dashed else '-',zorder=1)
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',
                                mutation_scale=6.5,linewidth=.75,color=color,
                                linestyle='--' if dashed else '-',zorder=1))
def save(fig,name):
    for ext in ('pdf','svg','png'):
        p=OUT/f'{name}.{ext}'
        meta={'CreationDate':None,'ModDate':None} if ext=='pdf' else ({'Date':None} if ext=='svg' else None)
        fig.savefig(p,dpi=300,bbox_inches='tight',pad_inches=.025,metadata=meta)
        files[str(p.relative_to(OUT.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()
    plt.close(fig)

fig,ax=plt.subplots(figsize=(3.2,2.75))
fig.subplots_adjust(0,0,1,1)
ax.set(xlim=(0,100),ylim=(0,105));ax.axis('off')
box(ax,1,91,98,13,'Revenue: all or completed orders?',fill='#EAF0F5',edge=BLUE,weight='bold')
text(ax,23,83,'Interpretation',7.7,weight='bold')
text(ax,62,83,'Observed $r_0$',7.7,weight='bold')
text(ax,87,83,'Repair $r_1$',7.7,weight='bold')
text(ax,62,76,'pending = 0',7)
text(ax,87,76,'pending = 50',7)
for y,label,a,b in [(61,'Completed only',100,100),(49,'All orders',100,150)]:
    box(ax,1,y,46,11,label,fill='#F4F5F7',size=8)
    box(ax,49,y,24,11,str(a),fill='#EEF3F7',edge=BLUE,size=9)
    box(ax,75,y,24,11,str(b),fill='#F0EAF5' if b==150 else '#F4F5F7',
        edge=PURPLE if b==150 else '#9CA6B0',size=9,weight='bold' if b==150 else 'normal')
text(ax,50,43,'Equal now does not mean equal after repair.',7.3,color=PURPLE)
box(ax,19,28,62,11,'Clarify the pending amount',fill='#F8F1E3',edge=OCHRE,size=8)
arrow(ax,[(50,40),(50,39)],color=OCHRE)
arrow(ax,[(36,28),(25,24)],color=GREEN)
arrow(ax,[(64,28),(75,24)],color=PURPLE)
box(ax,1,1,47,23,'0 confirmed\nBoth totals = 100\nSkip the intent question',fill='#EAF3EF',edge=GREEN,size=7.4)
box(ax,52,1,47,23,'50 confirmed\n100 versus 150\nAsk which orders count',fill='#F0EAF5',edge=PURPLE,size=7.4)
save(fig,'overview')

fig,ax=plt.subplots(figsize=(7.1,3.0))
fig.subplots_adjust(0,0,1,1)
ax.set(xlim=(0,210),ylim=(0,92));ax.axis('off')
# Four stable roles: supplied universe, persistent state, certificates, actions.
for x,label in [(22,'Declared problem'),(70,'Current evidence'),(124,'Certificate checks'),(187,'Next action')]:
    text(ax,x,88,label,9,weight='bold')
box(ax,1,56,41,23,'Question + database\nInterpretations $\\mathcal{I}$, repairs $\\mathcal{R}$\nAdmissible worlds $\\mathcal{H}$',fill='#EAF0F5',edge=BLUE,size=8)
box(ax,49,56,43,23,'Surviving worlds $V$\nExecuted worlds $K$\nCached answers',fill='#EAF0F5',edge=BLUE,size=8)
arrow(ax,[(42,67.5),(49,67.5)],color=BLUE)
# A positive answer certificate ends the loop.
box(ax,101,61,46,18,'1  Answer certificate\nAll surviving answers\nknown and equal?',fill='#EAF3EF',edge=GREEN,size=8)
arrow(ax,[(92,70),(101,70)],color=BLUE)
box(ax,169,64,40,14,'Return common answer',fill='#EAF3EF',edge=GREEN,size=8,weight='bold')
arrow(ax,[(147,71),(169,71)],color=GREEN);text(ax,157,75,'yes',7,color=GREEN)
arrow(ax,[(124,61),(124,54)]);text(ax,129,58,'no',7,ha='left')
box(ax,101,36,46,18,'2  Relevance certificate\nObserved unequal pair\nfor one coordinate?',fill='#F8F1E3',edge=OCHRE,size=8)
# The policy branch is explicit and has its own decision rule.
arrow(ax,[(124,36),(124,29)]);text(ax,129,32.5,'yes',7,ha='left')
box(ax,98,8,52,21,'3  Selection rule\nImmediate: witnessed coordinate\nCertified: witnessed EC2 maximizer\nwith bounds against all competitors',
    fill='#F0EAF5',edge=PURPLE,size=7.5)
box(ax,169,17,40,15,'Ask coordinate $q$\nReceive response $z$',fill='#F0EAF5',edge=PURPLE,size=8)
arrow(ax,[(150,20),(169,24)],color=PURPLE);text(ax,159,16,'permitted',7,color=PURPLE)
box(ax,169,40,40,15,'Execute unknown $h\\in V$\nReveal and cache $A(h)$',fill='#F8F1E3',edge=OCHRE,size=8)
arrow(ax,[(147,46),(169,46)],color=OCHRE);text(ax,158,50,'no witness',7,color=OCHRE)
arrow(ax,[(150,28),(169,42)],color=OCHRE)
text(ax,188,36,'Certified policy: not ready',7,color=OCHRE)
# Response filtering and newly known answers return to the same state.
box(ax,49,8,43,21,'Update state\nAsk: $V\\leftarrow\\{h\\in V:q(h)=z\\}$\nExecute: $K\\leftarrow K\\cup\\{h\\}$',
    fill='#F2F4F6',edge=BLUE,size=7.6)
arrow(ax,[(189,17),(189,2),(70,2),(70,8)],color=BLUE)
arrow(ax,[(209,47),(210,47),(210,0),(45,0),(45,18),(49,18)],color=BLUE)
arrow(ax,[(70,29),(70,56)],color=BLUE)
text(ax,67,42,'Recheck after\nevery action',7.2,color=BLUE,ha='right')
save(fig,'algorithm_framework')
out=ROOT/'results/E010/concept-figure-manifest.json'
out.write_text(json.dumps({'kind':'explanatory diagrams, not measurements',
 'example':{'completed_total':100,'pending_observed':0,'pending_allowed_repair':50,
            'answer_matrix':[[100,100],[100,150]]},
 'algorithm_scope':'finite supplied universe; binary coordinate policies with local relevance',
 'source':'scripts/draw_concept_figures.py',
 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'files':files},indent=2)+'\n')
print(json.dumps({'figures':2,'artifacts':len(files)}))
