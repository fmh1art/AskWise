"""Shared accounting and retrospective guarantee audit for E010."""
from collections import Counter
import time
from a2.binary_policy import run_binary
from a2.relevance import witness

METHODS = (
    'anchor', 'ask_all', 'full_ec2', 'full_relevant_ec2',
    'exact_fixed', 'exact_witness', 'partition_fixed', 'partition_witness',
    'immediate_fixed', 'immediate_witness',
)


def ec2_choice(worlds, state, known, eligible):
    def edges(ids):
        counts = Counter(known[i] for i in ids)
        return (len(ids)**2-sum(v*v for v in counts.values()))/2
    def gain(q):
        parts = [[i for i in state if worlds[i][q] == z] for z in (0, 1)]
        return edges(state)-sum(len(p)/len(state)*edges(p) for p in parts)
    return max(eligible, key=lambda q: (gain(q), -q))


def run_accounted(worlds, execute, respond, method):
    """No ground-truth map is available to this policy adapter."""
    if method.startswith(('exact_', 'partition_', 'immediate_')):
        mode, acquisition = method.split('_')
        return run_binary(worlds, execute, respond, bound='partition' if mode == 'partition' else 'four_cell',
                          acquisition=acquisition, immediate=mode == 'immediate')
    trace = []
    state = list(range(len(worlds)))
    known = {}
    def run(i):
        known[i] = execute(i)
        trace.append({'execute': i, 'label': known[i]})
    def ask(q):
        nonlocal state
        z = respond(q)
        trace.append({'question': q, 'response': z})
        state = [i for i in state if worlds[i][q] == z]
    if method == 'anchor':
        run(0)
        return {'answer': known[0], 'trace': trace}
    if method == 'ask_all':
        for q in range(len(worlds[0])):
            ask(q)
        run(state[0])
        return {'answer': known[state[0]], 'trace': trace}
    if method not in ('full_ec2', 'full_relevant_ec2'):
        raise ValueError(method)
    for i in state:
        run(i)
    while len({known[i] for i in state}) > 1:
        qs = [q for q in range(len(worlds[0])) if len({worlds[i][q] for i in state}) > 1]
        if method == 'full_relevant_ec2':
            qs = [q for q in qs if witness(worlds, state, known, q) is not None]
        ask(ec2_choice(worlds, state, known, qs))
    return {'answer': known[state[0]], 'trace': trace}


def evaluate_episode(worlds, labels, true, method):
    calls = set()
    def execute(i):
        if i in calls:
            raise AssertionError('Repeated execution must not silently be free')
        calls.add(i)
        return labels[i]
    start = time.perf_counter()
    result = run_accounted(worlds, execute, lambda q: worlds[true][q], method)
    cpu_ms = (time.perf_counter()-start)*1000
    # Post-hoc audit can see the full truth map; the policy cannot.
    state = list(range(len(worlds)))
    observed = {}
    truth = dict(enumerate(labels))
    questions = irrelevant = unproved = 0
    for step in result['trace']:
        if 'execute' in step:
            observed[step['execute']] = step['label']
        else:
            q = step['question']
            questions += 1
            irrelevant += witness(worlds, state, truth, q) is None
            unproved += witness(worlds, state, observed, q) is None
            state = [i for i in state if worlds[i][q] == step['response']]
    certificate = all(i in observed and observed[i] == result['answer'] for i in state)
    return {'accuracy': float(result['answer'] == labels[true]), 'executions': len(calls),
            'questions': questions, 'irrelevant': irrelevant, 'unproved': unproved,
            'stop_certificate': float(certificate), 'cpu_ms': cpu_ms,
            'cost1': len(calls)+questions, 'cost10': len(calls)+10*questions}
