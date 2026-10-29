from itertools import product
from a2.worlds import Problem, sales_task

def test_xor_is_not_invariant_when_marginal_answer_entropy_gain_is_zero():
    p=Problem(list(product([0,1],repeat=2)),[0,1,1,0])
    assert p.optimal((0,1,2,3))[0] == 2
    for m in ['ec2','answer_entropy','optimal']:
        assert all(p.run(i,m)['correct'] for i in range(4))

def test_interaction_defeats_one_coordinate_anchor():
    p=Problem(list(product([0,1],repeat=2)),[0,0,0,1])
    assert not p.run(3,'local')['correct']
    assert p.run(3,'ec2')['correct']

def test_observed_equality_not_preserved_after_repair():
    p=Problem([(0,0),(0,1),(1,0),(1,1)],[0,1,0,2])
    assert not p.run(3,'observed_then_repair')['correct']
    assert p.run(3,'ec2')['correct']

def test_certificate_requires_nonempty_and_complete_scope_is_explicit():
    p=Problem([(0,),(1,)],[0,1])
    assert p.certificate(()) is None
    assert p.certificate((0,1)) is None
    r=p.run(1,'ec2',initial=(0,))
    assert not r['correct'] and r['certificate'] is not None
    assert 'completeness not established' in r['certificate']['scope']

def test_exact_cost_and_correctness():
    for family in ['top_region','customer_count','threshold_count']:
        for seed in range(10):
            p=sales_task(seed,family)
            optimal=sum(p.run(i,'optimal')['questions'] for i in range(16))/16
            assert optimal == p.optimal(tuple(range(16)))[0]
            for method in ['ask_all','fixed','random','world_entropy','answer_entropy','ec2','repair_first','optimal']:
                runs=[p.run(i,method) for i in range(16)]
                assert all(r['correct'] for r in runs)
                assert sum(r['questions'] for r in runs)/16 >= optimal
