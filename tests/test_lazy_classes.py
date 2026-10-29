from itertools import product
from a2.worlds import Problem
from a2.lazy_classes import run_lazy

def test_exact_ec2_trace_for_every_three_bit_boolean_function():
    worlds=list(product([0,1],repeat=3))
    for labels in product([0,1],repeat=8):
        p=Problem(worlds,labels)
        for true in range(8):
            oracle=p.run(true,'ec2')
            expected=[t['question'] for t in oracle['trace'] if 'question' in t]
            for acquisition in ['comparison','fixed','random']:
                calls=[]
                def execute(i):calls.append(i);return labels[i]
                r=run_lazy(worlds,execute,lambda q:worlds[true][q],acquisition=acquisition)
                assert r['asked']==expected
                assert r['answer']==labels[true]
                assert len(calls)==len(set(calls))<=8

def test_constant_universe_requires_all_labels_without_extra_structure():
    worlds=list(product([0,1],repeat=4))
    r=run_lazy(worlds,lambda _:7,lambda _:0)
    assert r['executions']==16 and r['questions']==0
