"""Bounded completion hook for the already-authorized fixed E003 run.

No new model requests, scientific decisions, daemon, or recurring schedule.
"""
from pathlib import Path
import json,time,subprocess,sys,hashlib
root=Path(__file__).resolve().parents[1];paper=root.parent/'AskWise_Tex'
data=Path('/data01/fanmeihao-data/A2-research/E003')
plan=json.loads((root/'experiments/E003-plan.json').read_text())
deadline=time.monotonic()+23*3600
def cmd(args,cwd=root):
    r=subprocess.run(args,cwd=cwd,text=True,capture_output=True)
    if r.returncode:raise RuntimeError('Command failed: '+args[0]+'; '+r.stderr[-800:])
    return r.stdout
while True:
    ready=all((data/model/(str(i)+'.json')).exists() for model in ['doubao_seed2_lite','gpt5_6_sol_hydra'] for i in plan['ids'])
    if ready:break
    if time.monotonic()>deadline:raise TimeoutError('Fixed run incomplete; no new requests launched')
    time.sleep(30)
cmd([sys.executable,'scripts/summarize_e003.py'])
cmd([sys.executable,'scripts/verify_artifacts.py'])
summary=json.loads((root/'results/E003/summary.json').read_text())
verify=json.loads((root/'results/verification.json').read_text())
assert summary['complete'] and verify['complete']
rows=[]
for name in ['doubao_seed2_lite','gpt5_6_sol_hydra']:
    r=summary['models'][name];m=r['metrics']
    label='Doubao Lite' if name.startswith('doubao') else 'GPT Sol'
    rows.append(f"{label} & {100*m['observed_recall']:.2f} & {100*m['stable_recall']:.2f} & {r['failed']} "+chr(92)*2)
table='\n'.join([r'\begin{table}[t]',r'\centering\small',r'\begin{tabular}{lrrr}',r'\toprule',r'Model & Observed & Two-state & Failures \\',r'\midrule',*rows,r'\bottomrule',r'\end{tabular}',r'\caption{Reference signature recall (\%) on 155 frozen cases per model.}',r'\label{tab:e003}',r'\end{table}'])+'\n'
(paper/'tables/e003.tex').write_text(table)
p=paper/'sections/experiments.tex';text=p.read_text()
old='The run is ongoing; model-study results will be inserted only after completion and verification.'
new='''All 310 planned model outcomes have been recorded and their request signatures and usage verified.
\\input{tables/e003}
Failures count as zero recovery under the frozen protocol.
The comparison uses the same generated candidates for both pruning rules.
Adding a second state refines the execution signatures by construction, so nondecreasing recall alone does not establish a new method.
The measurements quantify reference-support recovery, not complete semantic coverage or human dialogue success.
Database-cluster bootstrap intervals and per-item failure accounting are retained in the accompanying results.'''
if old not in text:raise RuntimeError('Expected manuscript status marker missing; preserve user edits')
p.write_text(text.replace(old,new))
cmd(['bash','build.sh'],paper)
log=(paper/'main.log').read_text(errors='replace')
if 'undefined citations' in log or 'Overfull' in log:raise RuntimeError('Manuscript needs layout/citation review')
s=json.loads((root/'state.json').read_text());s['running_experiment']=None
s['completed_milestones'].append('E003 all 310 planned outcomes verified and manuscript updated')
s['next_action']='Resolve guarantee preference and continue substantive algorithm development; E003 completion is not research completion'
s['phase']='algorithm-development';(root/'state.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
receipt={'status':'E003 completed; overall research incomplete','summary':'results/E003/summary.json','verification':'results/verification.json','paper_sha256':hashlib.sha256((paper/'main.pdf').read_bytes()).hexdigest(),'completed_at':time.time()}
(root/'results/E003/completion.json').write_text(json.dumps(receipt,indent=2)+'\n')
# Publish only fixed-run artifacts. Never stage unrelated files.
for repo,paths,message in [(root,['results/E003/summary.json','results/E003/completion.json','results/verification.json','state.json'],'Verify fixed two-model candidate study and update research state'),(paper,['tables/e003.tex','sections/experiments.tex','main.pdf','main.bbl'],'Insert verified fixed-sample model results into working draft')]:
    cmd(['git','add',*paths],repo)
    cmd(['git','commit','-m',message],repo)
    cmd(['git','push','origin','main'],repo)
    head=cmd(['git','rev-parse','HEAD'],repo).strip()
    remote=cmd(['git','ls-remote','origin','refs/heads/main'],repo).split()[0]
    assert head==remote
    print(repo.name,head,flush=True)
print(json.dumps(receipt),flush=True)
