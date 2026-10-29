from itertools import product
from a2.worlds import Problem
from a2.relevance import witness, audit_trace
from a2.binary_bounds import comparison_interval


def test_ec2_can_ask_an_irrelevant_coordinate_under_ties():
    worlds = tuple(product((0, 1), repeat=3))
    labels = [w[1] ^ w[2] for w in worlds]
    p = Problem(worlds, labels)
    trace = p.run(0, 'ec2')['trace']
    assert trace[0]['question'] == 0
    assert audit_trace(p, 0, trace)[0]['relevant'] is False
    assert witness(worlds, range(8), dict(enumerate(labels)), 1) is not None


def test_global_pair_is_insufficient_for_context_matched_relevance():
    worlds = tuple(product((0, 1), repeat=2))
    known = {0: 0, 3: 1}
    assert worlds[0][0] != worlds[3][0] and known[0] != known[3]
    assert witness(worlds, range(4), known, 0) is None
    assert witness(worlds, range(4), {0: 0, 1: 0, 2: 1, 3: 1}, 0) == (0, 2)


def test_four_cell_bound_exact_for_every_partial_boolean_map():
    worlds = tuple(product((0, 1), repeat=3))
    # Precompute each complete map's actual EC2 difference by an independent
    # unordered-edge calculation, then group over all 3^8 partial maps.
    complete = []
    for labels in product((0, 1), repeat=8):
        scores = []
        for q in range(3):
            scores.append(sum(
                sum(worlds[i][q] != w[q] or worlds[j][q] != w[q] for w in worlds)/8
                for i in range(8) for j in range(i+1, 8) if labels[i] != labels[j]
            ))
        complete.append((labels, scores))
    for partial in product((None, 0, 1), repeat=8):
        known = {i: y for i, y in enumerate(partial) if y is not None}
        feasible = [scores for labels, scores in complete if all(labels[i] == y for i, y in known.items())]
        for q, r in [(0, 1), (0, 2), (1, 2)]:
            actual = [s[q]-s[r] for s in feasible]
            assert comparison_interval(worlds, range(8), known, q, r) == (min(actual), max(actual))
