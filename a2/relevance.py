"""Context-matched relevance certificates within a declared finite universe."""
from itertools import combinations


def witness(worlds, state, known, question):
    """A pair differs only in the queried coordinate and has unequal answers.

    Unknown labels cannot witness relevance. This is a sufficient criterion on
    constrained supports, and complete for coordinate relevance on a Cartesian
    support. It does not promise the actual response changes the final answer.
    """
    groups = {}
    for i in state:
        if i not in known:
            continue
        context = worlds[i][:question]+worlds[i][question+1:]
        for j in groups.get(context, []):
            if worlds[i][question] != worlds[j][question] and known[i] != known[j]:
                return j, i
        groups.setdefault(context, []).append(i)
    return None


def audit_trace(problem, true_index, trace):
    state = list(range(len(problem.worlds)))
    known = dict(enumerate(problem.answers))
    asked = []
    for step in trace:
        if 'question' not in step:
            continue
        q = step['question']
        pair = witness(problem.worlds, state, known, q)
        asked.append({'question': q, 'relevant': pair is not None, 'witness': pair})
        z = problem.worlds[true_index][q]
        state = [i for i in state if problem.worlds[i][q] == z]
    return asked
