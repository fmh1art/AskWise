from itertools import product
from a2.binary_policy import run_binary
from a2.relevance import witness


def test_all_boolean_functions_answers_and_observed_local_witnesses():
    worlds = tuple(product((0, 1), repeat=3))
    for labels in product((0, 1), repeat=8):
        for true in range(8):
            for bound, immediate in [('four_cell', False), ('partition', False), ('four_cell', True)]:
                r = run_binary(worlds, lambda i: labels[i], lambda q: worlds[true][q], bound=bound, immediate=immediate)
                assert r['answer'] == labels[true]
                state = list(range(8))
                known = {}
                for step in r['trace']:
                    if 'execute' in step:
                        known[step['execute']] = step['label']
                    else:
                        q = step['question']
                        assert witness(worlds, state, known, q) is not None
                        state = [i for i in state if worlds[i][q] == step['response']]
                assert all(i in known and known[i] == r['answer'] for i in state)
