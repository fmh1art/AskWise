"""Strict, finite-cube development policies for Boolean answer maps."""
from itertools import combinations, product
from collections import Counter
from a2.binary_bounds import comparison_interval
from a2.relevance import witness


def partition_lower(worlds, state, known, q, r):
    n = len(state)
    counts = {s: Counter(worlds[i][s] for i in state) for s in (q, r)}
    by_unknown = {i: {} for i in state if i not in known}
    lower = 0
    for i, j in combinations(state, 2):
        cq = n if worlds[i][q] != worlds[j][q] else n-counts[q][worlds[i][q]]
        cr = n if worlds[i][r] != worlds[j][r] else n-counts[r][worlds[i][r]]
        d = cq-cr
        if i in known and j in known:
            lower += d*(known[i] != known[j])
        elif i not in known and j not in known:
            lower += min(0, d)
        else:
            u, k = (i, j) if i not in known else (j, i)
            label = known[k]
            by_unknown[u][label] = by_unknown[u].get(label, 0)+d
    for groups in by_unknown.values():
        total = sum(groups.values())
        lower += min([total]+[total-v for v in groups.values()])
    return lower


def run_binary(worlds, execute, respond, bound='four_cell', acquisition='witness', immediate=False):
    worlds = tuple(tuple(w) for w in worlds)
    if not worlds:
        raise ValueError('Nonempty cube required')
    dims = len(worlds[0])
    if set(worlds) != set(product((0, 1), repeat=dims)) or len(worlds) != 2**dims:
        raise ValueError('Complete binary Cartesian cube required')
    state = list(range(len(worlds)))
    known = {}
    trace = []
    questions = 0
    while True:
        unknown = [i for i in state if i not in known]
        if not unknown and len({known[i] for i in state}) == 1:
            return {'answer': known[state[0]], 'executions': len(known), 'questions': questions, 'trace': trace}
        qs = [q for q in range(dims) if len({worlds[i][q] for i in state}) > 1]
        eligible = [q for q in qs if witness(worlds, state, known, q) is not None]
        chosen_q = None
        for q in eligible:
            if immediate or all(
                (comparison_interval(worlds, state, known, q, r)[0] if bound == 'four_cell'
                 else partition_lower(worlds, state, known, q, r)) >= 0
                for r in qs if r != q
            ):
                chosen_q = q
                break
        if chosen_q is not None:
            q = chosen_q
            pair = witness(worlds, state, known, q)
            z = respond(q)
            if z not in (0, 1):
                raise ValueError('Unsupported response')
            state = [i for i in state if worlds[i][q] == z]
            questions += 1
            trace.append({'question': q, 'response': z, 'witness': pair})
            continue
        if not unknown:
            raise AssertionError('Nonconstant Boolean cube must have a witnessed greedy maximizer')
        if acquisition == 'fixed':
            chosen = unknown[0]
        elif acquisition == 'witness':
            def priority(i):
                adjacent = [j for j in state if j in known and sum(a != b for a, b in zip(worlds[i], worlds[j])) == 1]
                labels = {known[j] for j in adjacent}
                # Two opposite neighbors guarantee some relevance witness;
                # one represented class gives one under one of the outcomes.
                return len(labels), len(adjacent), -i
            chosen = max(unknown, key=priority)
        else:
            raise ValueError(acquisition)
        label = execute(chosen)
        if label not in (0, 1):
            raise ValueError('Boolean execution result required')
        known[chosen] = int(label)
        trace.append({'execute': chosen, 'label': int(label)})
