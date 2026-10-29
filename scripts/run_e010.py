from pathlib import Path
from itertools import product
import sys, random, json, hashlib, time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from a2.evaluation import METHODS, evaluate_episode
from a2.worlds import sales_task

root = Path(__file__).resolve().parents[1]
out = root/'results/E010'
out.mkdir(exist_ok=True)
worlds = tuple(product((0, 1), repeat=4))
tasks = []
for seed in range(10000, 10040):
    for family in ['top_region', 'customer_count', 'threshold_count']:
        p = sales_task(seed, family)
        if family == 'top_region':
            labels = [int(('East',) in a) for a in p.answers]
        else:
            threshold = 6 if family == 'customer_count' else 5
            labels = [int(a[0][0] >= threshold) for a in p.answers]
        tasks.append({'cohort': 'fresh_sales', 'family': family, 'seed': seed, 'labels': labels})
for seed in range(20000, 20008):
    rng = random.Random(seed)
    active = rng.randrange(4)
    coeff = [rng.randint(1, 3) for _ in range(4)]
    tests = {
        'constant': lambda w: seed % 2,
        'single_bit': lambda w: w[active],
        'nuisance_xor': lambda w: w[2] ^ w[3],
        'rare_conjunction': lambda w: int(all(w)),
        'threshold': lambda w: int(sum(a*b for a, b in zip(coeff, w)) >= sum(coeff)//2),
        'intent_branch': lambda w: (w[1] and w[2]) if w[0] else w[3],
    }
    for family, fn in tests.items():
        tasks.append({'cohort': 'stress', 'family': family, 'seed': seed, 'labels': [int(fn(w)) for w in worlds]})
records = []
start = time.monotonic()
for ti, task in enumerate(tasks):
    for method in METHODS:
        episodes = [evaluate_episode(worlds, task['labels'], true, method) for true in range(16)]
        row = {k: task[k] for k in ['cohort', 'family', 'seed']}
        row.update(method=method, episodes=16, constant=len(set(task['labels'])) == 1)
        row.update({k: sum(e[k] for e in episodes)/16 for k in episodes[0]})
        records.append(row)
    if (ti+1) % 30 == 0:
        print('tasks', ti+1, len(tasks), flush=True)
(out/'per_task.json').write_text(json.dumps(records, indent=2)+'\n')
(out/'tasks.json').write_text(json.dumps(tasks, indent=2)+'\n')
manifest = {'protocol_sha256': hashlib.sha256((root/'experiments/E010-protocol.md').read_bytes()).hexdigest(),
            'tasks': len(tasks), 'fresh_sales_tasks': 120, 'stress_tasks': 48,
            'policies': len(METHODS), 'hidden_worlds_per_task': 16,
            'policy_episodes': len(tasks)*len(METHODS)*16, 'api_requests': 0,
            'elapsed_seconds': time.monotonic()-start,
            'per_task_sha256': hashlib.sha256((out/'per_task.json').read_bytes()).hexdigest()}
(out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(json.dumps(manifest, indent=2))
