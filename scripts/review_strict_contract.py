"""Two bounded API proof reviews; responses are unverified advisory material."""
from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from a2.api import Client

root = Path(__file__).resolve().parents[1]
prompt = '''Independently audit this research derivation; do not invent references,
performance, or missing assumptions. A2 must guarantee correct answers and
context-matched question relevance in a declared finite universe. Each question
reveals one hidden binary coordinate. An internal execution reveals the Boolean
answer at a chosen counterfactual world. Only observed unequal labels can prove
a relevance witness; its two worlds must differ only in the queried coordinate.
For this derivation the surviving worlds form a full uniform binary Cartesian
cube, questions have equal cost, and the answer function is otherwise arbitrary.

Known EC2 objective: sum of prior-product weights on unequal-answer unordered
pairs eliminated by the observed question response, in expectation over that
response. For unanswered coordinates q,r let a,b,c,d count positive labels in
their joint-response cells 00,01,10,11. The claimed unnormalized expected gain
difference is (a-d)(b-c); with normalized posterior pair weights divide by n^2.
Known partial labels give independent count intervals; the two differences
use disjoint cells. Claimed exact minimum/maximum across all Boolean completions
are the four corner products of the two difference intervals. We exhaustively
checked all 3^8 partial maps on 8 worlds against explicit unordered-edge cuts.

Algorithm component: ask a witnessed coordinate only if its lower comparison
bound against every rival is nonnegative; otherwise execute another world.
Stop only when every surviving world has been executed and has the same answer.
No guarantee is claimed on minimum execution cost, novelty, or correlated priors.
The earlier E006 arbitrary conflicting-pair gate was weaker and does not satisfy
this new relevance definition. The current full-map EC2 can ask irrelevant
nuisance bits under ties, e.g. f(x0,x1,x2)=x1 XOR x2 with x0 first in tie order.

Development data: Boolean transforms of 300 old 16-world sales problems, all
hidden worlds evaluated. Exact bound fixed acquisition: E=13.7545833,Q=.85625;
older partition-star bound fixed acquisition: E=14.8745833,Q=.85625;
simple immediate-local-witness querying: E=13.0116667,Q=.8720833.
Thus the new bound loses on the primary execution objective to the simple
control, also on E+cQ for c=.1,1,10. This is development, not confirmation.

Verify the algebra, exact interval attainability, relevance/termination logic,
and whether the negative conclusion is warranted. Identify a concrete flaw if
one exists, or list precisely what is still unproved. Do not call this a novel
method merely because the formula is correct. Keep the reply under 1500 words.
'''
for name in ['gpt5_6_sol_hydra', 'doubao_seed2_lite']:
    client = Client('/home/fanmeihao/projects/_llm_configs/'+name+'.yaml', '/data01/fanmeihao-data/A2-research/api/strict-contract-review')
    r = client.call(prompt, 8192)
    result = {'status': 'unverified_advisory_review', 'model': r['response'].get('model'),
              'usage': r['response'].get('usage'), 'signature': r['signature'],
              'text': r['response']['choices'][0]['message']['content']}
    (root/'reviews'/('strict-contract-'+name+'.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(name, result['model'], result['usage'], flush=True)
