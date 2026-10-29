from itertools import product
from fractions import Fraction
import random
from a2.compiled_scores import CompiledProblem, ScoreProgram


def explicit_pair_scores(problem, evidence):
    intents, domains = problem.domains(evidence)
    worlds = []
    for i in intents:
        for bits in product(*domains):
            mass = problem.intent_weights[i]
            for j, z in enumerate(bits):
                mass *= problem.repair_weights[j][z]
            worlds.append(((i, *bits), problem.programs[i].answer(bits), mass))
    total = sum(m for _, _, m in worlds)
    scores = {}
    for q in range(problem.n+1):
        if q in evidence:
            continue
        cut = 0
        for ix, (w, y, mass) in enumerate(worlds):
            for w2, y2, mass2 in worlds[ix+1:]:
                if y == y2:
                    continue
                cut_mass = sum(m3 for w3, _, m3 in worlds if w[q] != w3[q] or w2[q] != w3[q])
                cut += mass*mass2*cut_mass
        scores[q] = Fraction(cut, total**3)
    return scores


def test_weighted_marginals_and_ec2_all_partial_states():
    rng = random.Random(71029)
    for _ in range(12):
        programs = [ScoreProgram(tuple(rng.randint(-3, 3) for _ in range(3)), rng.randint(-2, 2), (-2, 2)) for _ in range(2)]
        p = CompiledProblem(programs, (2, 3), [(1, 2), (3, 1), (2, 5)])
        for evidence_values in product((None, 0, 1), repeat=4):
            evidence = {j: z for j, z in enumerate(evidence_values) if z is not None}
            h, joint, _ = p.histograms(evidence)
            eh, ejoint, _ = p.enumerate_histograms(evidence)
            assert h == eh
            assert joint == ejoint
            d = p.decision(evidence)
            if len(h) == 1:
                assert d['question'] is None
                assert d['answer'] == next(iter(h))
            else:
                assert d['scores'] == explicit_pair_scores(p, evidence)


def test_interaction_hidden_from_single_coordinate_anchor():
    p = CompiledProblem([ScoreProgram((1, 1), 0, (2,))])
    assert [p.programs[0].answer(x) for x in [(0, 0), (0, 1), (1, 0)]] == [0, 0, 0]
    assert p.programs[0].answer((1, 1)) == 1
    assert p.decision()['question'] in (1, 2)
    assert p.decision({1: 0})['answer'] == 0


def test_large_constant_function_certifies_without_world_expansion():
    p = CompiledProblem([ScoreProgram((1,)*64, 0, (65,))])
    d = p.decision()
    assert d['answer'] == 0
    assert d['states'] < 5000
