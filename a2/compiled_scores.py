"""Exact EC2 via score-distribution messages; a strong baseline, not new EC2.

Assumptions: a categorical intent, independent binary repairs with integer
weights, and an integer affine score classified by sorted cut points.
Forward/reverse marginal computation is classical probabilistic inference.
This module accepts a declared program; it does not certify arbitrary SQL.
"""
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod


@dataclass(frozen=True)
class ScoreProgram:
    coefficients: tuple
    offset: int = 0
    cuts: tuple = (0,)

    def label(self, score):
        return bisect_right(self.cuts, score)

    def answer(self, bits):
        return self.label(self.offset + sum(a*x for a, x in zip(self.coefficients, bits)))


class CompiledProblem:
    def __init__(self, programs, intent_weights=None, repair_weights=None):
        self.programs = tuple(programs)
        if not programs:
            raise ValueError('At least one program required')
        self.n = len(programs[0].coefficients)
        self.intent_weights = tuple(intent_weights or [1]*len(programs))
        self.repair_weights = tuple(repair_weights or [(1, 1)]*self.n)
        if len(self.intent_weights) != len(programs) or len(self.repair_weights) != self.n:
            raise ValueError('Weight dimensions differ')
        for p in programs:
            if len(p.coefficients) != self.n or tuple(sorted(set(p.cuts))) != p.cuts:
                raise ValueError('Inconsistent coefficients or cuts')
            if not all(type(v) is int for v in (*p.coefficients, p.offset, *p.cuts)):
                raise ValueError('Exact integer score required')
        weights = (*self.intent_weights, *(v for pair in self.repair_weights for v in pair))
        if any(type(w) is not int or w <= 0 for w in weights):
            raise ValueError('Strictly positive integer prior weights required')
        if any(len(pair) != 2 for pair in self.repair_weights):
            raise ValueError('Binary repairs required')

    def domains(self, evidence):
        for q, z in evidence.items():
            size = len(self.programs) if q == 0 else 2
            if not 0 <= q <= self.n or not 0 <= z < size:
                raise ValueError('Invalid evidence')
        intents = (evidence[0],) if 0 in evidence else range(len(self.programs))
        domains = [(evidence[j+1],) if j+1 in evidence else (0, 1) for j in range(self.n)]
        return intents, domains

    def histograms(self, evidence=None):
        """Return answer masses and joint (question, response, answer) masses."""
        evidence = evidence or {}
        intents, domains = self.domains(evidence)
        hist = Counter()
        joint = defaultdict(Counter)
        state_count = 0
        for i in intents:
            p = self.programs[i]
            prefix = [{p.offset: 1}]
            for j, a in enumerate(p.coefficients):
                nxt = defaultdict(int)
                for s, mass in prefix[-1].items():
                    for z in domains[j]:
                        nxt[s+a*z] += mass*self.repair_weights[j][z]
                prefix.append(dict(nxt))
            state_count += sum(map(len, prefix))
            final = Counter()
            for s, mass in prefix[-1].items():
                final[p.label(s)] += mass
            iw = self.intent_weights[i]
            for y, mass in final.items():
                hist[y] += iw*mass
                joint[0, i][y] += iw*mass
                # Reverse messages compute every coordinate marginal for y.
                adj = {s: int(p.label(s) == y) for s in prefix[-1]}
                for j in reversed(range(self.n)):
                    a = p.coefficients[j]
                    prev = {}
                    for s, prefix_mass in prefix[j].items():
                        value = 0
                        for z in domains[j]:
                            term = self.repair_weights[j][z]*adj.get(s+a*z, 0)
                            joint[j+1, z][y] += iw*prefix_mass*term
                            value += term
                        prev[s] = value
                    adj = prev
        return hist, dict(joint), state_count

    def decision(self, evidence=None):
        evidence = evidence or {}
        hist, joint, states = self.histograms(evidence)
        return decision_from_histograms(hist, joint, evidence, states)

    def enumerate_histograms(self, evidence=None):
        """Independent explicit-world reference; deliberately not the fast path."""
        evidence = evidence or {}
        intents, domains = self.domains(evidence)
        hist = Counter()
        joint = defaultdict(Counter)
        worlds = 0
        for i in intents:
            for bits in product(*domains):
                mass = self.intent_weights[i]*prod(self.repair_weights[j][z] for j, z in enumerate(bits))
                y = self.programs[i].answer(bits)
                hist[y] += mass
                for q, z in enumerate((i, *bits)):
                    joint[q, z][y] += mass
                worlds += 1
        return hist, dict(joint), worlds


def decision_from_histograms(hist, joint, evidence, states=0):
    total = sum(hist.values())
    remaining_twice = total*total-sum(v*v for v in hist.values())
    if not remaining_twice:
        return {'question': None, 'answer': next(iter(hist)), 'scores': {}, 'states': states}
    scores = {}
    for q in sorted({q for q, z in joint} - set(evidence)):
        residual = 0
        for (qq, z), counts in joint.items():
            if qq != q:
                continue
            mass = sum(counts.values())
            residual += mass*(mass*mass-sum(v*v for v in counts.values()))
        # Normalize by the same posterior total; arbitrary-precision exact.
        scores[q] = Fraction(total*remaining_twice-residual, 2*total**3)
    q = max(scores, key=lambda q: (scores[q], -q))
    return {'question': q, 'answer': None, 'scores': scores, 'states': states}
