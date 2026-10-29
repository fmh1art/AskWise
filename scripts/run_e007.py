"""Bounded structural-inference baseline scaling audit."""
from pathlib import Path
import sys, random, json, time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from a2.compiled_scores import CompiledProblem, ScoreProgram

root = Path(__file__).resolve().parents[1]
rows = []
for n in [8, 12, 16, 32, 64, 128, 256]:
    for seed in range(71029, 71032):
        rng = random.Random(seed)
        programs = []
        for intent in range(2):
            coeff = tuple(rng.randint(-3, 6) for _ in range(n))
            center = sum(coeff)//2+intent
            programs.append(ScoreProgram(coeff, intent, (center, center+4)))
        problem = CompiledProblem(programs)
        start = time.perf_counter()
        hist, joint, states = problem.histograms()
        elapsed = time.perf_counter()-start
        row = {'n_repairs': n, 'seed': seed, 'worlds': str(2**(n+1)),
               'compiled_seconds': elapsed, 'message_states': states}
        if n <= 16:
            start = time.perf_counter()
            refh, refj, worlds = problem.enumerate_histograms()
            row['enumerated_seconds'] = time.perf_counter()-start
            row['exact_histogram_match'] = (hist == refh and joint == refj)
            assert row['exact_histogram_match']
        rows.append(row)
        print(n, seed, round(elapsed, 4), states, flush=True)
out = root/'results/E007'
out.mkdir(exist_ok=True)
(out/'scaling.json').write_text(json.dumps({'status': 'development baseline; no novelty claim', 'rows': rows}, indent=2)+'\n')
