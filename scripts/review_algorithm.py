"""Bounded algorithm ideation; outputs are unverified proposals, never results."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from a2.api import Client
root=Path(__file__).resolve().parents[1]
prompt='''Research task A2: ask only questions that change a data-analysis answer when both intent and data repairs are uncertain. User requires a substantive algorithm paper beyond EC2 and classical query-driven cleaning. Verified prior: AIR executes SQLs on observed database and deduplicates identical outputs; EC2 solves finite known equivalence-class determination; query-driven cleaning/entity resolution predate LLMs; CEGAR and lazy greedy are established. Complete-world EC2 was essentially optimal for question count in our pilot, so renaming it is not novel.
Investigate the setting where worlds h=(intent, repair) are initially specified, but their answer classes f(h)=SQL(intent,repair(D)) are expensive and unknown until internally executed. External clarification tests constrain the true h; internal executions reveal f at counterfactual h. We need to jointly choose executions and questions while never claiming global candidate coverage from finite agreement. Beware that this can be reduced formally to EC2 on meta-hypotheses (f,h), so merely proposing the joint state is not a contribution. A useful method must exploit factorization or lazy certificates to solve a computational barrier, and compare against full EC2, lazy EC2, query-first/execution-first, CEGAR witness heuristics, and tiny exact joint optimization.
Propose at most TWO precise executable algorithms with objectives, assumptions, pseudocode, an actual mathematical statement you can justify, and explicit ways they may already be covered by existing literature. Provide a small counterexample against a tempting naive method and a minimal discriminating experiment. Do not invent references, guarantees, or results. If neither idea is defensibly new say so. Distinguish theorem from conjecture. The setting should remain relevant to NL data analysis and be testable using two black-box LLM APIs plus Python/SQL. Keep under 2500 words.'''
for label in ['gpt5_6_sol_hydra','doubao_seed2_lite']:
    client=Client('/home/fanmeihao/projects/_llm_configs/'+label+'.yaml','/data01/fanmeihao-data/A2-research/api/algorithm-ideation')
    r=client.call(prompt,12288)
    result={'status':'unverified_proposal','model':r['response'].get('model'),'usage':r['response'].get('usage'),'signature':r['signature'],'text':r['response']['choices'][0]['message']['content']}
    (root/'reviews'/('algorithm-'+label+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(label,result['model'],result['usage'],flush=True)
