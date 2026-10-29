from itertools import product
from a2.evaluation import METHODS, evaluate_episode


def test_accounting_exposes_unsafe_controls_and_preserves_strict_contract():
    worlds = tuple(product((0, 1), repeat=3))
    labels = [w[1] ^ w[2] for w in worlds]
    for method in METHODS:
        for true in range(8):
            r = evaluate_episode(worlds, labels, true, method)
            if method == 'anchor':
                assert r['executions'] == 1 and not r['stop_certificate']
            else:
                assert r['accuracy'] == r['stop_certificate'] == 1
            if method not in ['anchor', 'ask_all', 'full_ec2']:
                assert r['unproved'] == r['irrelevant'] == 0
            if method == 'full_ec2':
                assert r['irrelevant'] >= 1
            if method == 'ask_all':
                assert r['unproved'] == 3 and r['executions'] == 1
            assert r['cost1'] == r['executions']+r['questions']
