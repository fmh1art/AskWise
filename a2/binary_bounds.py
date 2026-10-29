"""Exact four-cell EC2 score-difference bounds for a balanced binary cube.

This is a candidate execution-selection component, not a new EC2 objective.
Labels must be Boolean; test costs equal; no non-Cartesian or correlated priors.
"""
from itertools import product


def comparison_interval(worlds, state, known, q, r):
    if q == r:
        return (0, 0)
    cells = {(a, b): [0, 0] for a, b in product((0, 1), repeat=2)}
    for i in state:
        lohi = cells[worlds[i][q], worlds[i][r]]
        if i in known:
            if known[i] not in (0, 1):
                raise ValueError('Boolean answers required')
            lohi[0] += known[i]
            lohi[1] += known[i]
        else:
            lohi[1] += 1
    a, b, c, d = [cells[key] for key in [(0, 0), (0, 1), (1, 0), (1, 1)]]
    u = (a[0]-d[1], a[1]-d[0])
    v = (b[0]-c[1], b[1]-c[0])
    corners = [x*y for x in u for y in v]
    return min(corners), max(corners)


def certified_best(worlds, state, known, questions):
    """All global greedy maximizers certified for every remaining completion."""
    return [q for q in questions if all(comparison_interval(worlds, state, known, q, r)[0] >= 0 for r in questions)]
