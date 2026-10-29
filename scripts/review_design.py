"""One fixed design review per authorized API; no model-generated code execution."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from a2.api import Client
root=Path(__file__).resolve().parents[1]
prompt='''You are a skeptical research reviewer. The topic is asking only clarifications that affect a data-analysis answer, jointly over natural-language intent and uncertain data repairs. Verified related work: AIR (arXiv:2610.24248), section 3.2, executes candidate SQL on the observed database and prunes identical results; EC2 (Golovin, Krause, Ray, NeurIPS 2010) already solves finite hypothesis equivalence-class determination; CircleClar (arXiv:2610.20052) estimates model-realizable answer support. Do not invent citations or claim novelty. A local exhaustive exploratory study of 300 generated sales tasks, 16 worlds/task, compares 11 methods: full-world EC2 costs 1.80792 questions, exact optimal costs 1.80667, all questions costs 4; all three are correct within the supplied complete universe. Observed-database intent pruning costs 2.02458 with 98.875% accuracy. Local single-assumption checks cost 1.70583 with 98.9792% accuracy. These are synthetic, oracle candidates, truthful simulated feedback, not LLM results.
Identify fatal threats, whether a new selection heuristic is justified, and an experimentally discriminative research direction retaining the user's topic. Consider incomplete candidate coverage, cross-axis interactions, cost of candidate execution, unknown user responses, and fair EC2/AIR comparisons. Supply a concrete small example or explain why no novelty can currently be defended. Return concise prose. No approval role is delegated to you.'''
for label in ['doubao_seed2_lite','gpt5_6_sol_hydra']:
    client=Client('/home/fanmeihao/projects/_llm_configs/'+label+'.yaml','/data01/fanmeihao-data/A2-research/api/design-review')
    r=client.call(prompt,8192)
    output={'model':r['response'].get('model'),'usage':r['response'].get('usage'),'signature':r['signature'],'text':r['response']['choices'][0]['message']['content']}
    (root/'reviews'/(label+'.json')).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(label,output['model'],output['usage'],flush=True)
