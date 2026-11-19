"""Replay E003, draw the blinded E011 error sample, and tabulate its labels."""

import argparse
from collections import Counter
import hashlib
from itertools import permutations
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from a2.api import parse_json
from scripts.audit_ambiqt import UP, build
from scripts.run_e003 import DATA, execute, perturb

OUT = ROOT / 'results' / 'E011'
MODELS = ('doubao_seed2_lite', 'gpt5_6_sol_hydra')
LABELS = ('projection', 'relation', 'filter', 'aggregation', 'ranking', 'other', 'unresolved')
SAMPLE_SIZE = 50


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def run_state(db, references, queries):
    gold = [execute(db, sql) for sql in references]
    outputs = []
    for sql in queries:
        try:
            outputs.append(execute(db, sql))
        except (sqlite3.Error, ValueError):
            outputs.append(None)
    return gold, outputs


def matches_after_reordering(pair, reference):
    # Check one fixed column permutation on both states. Canonical rows retain types and duplicates.
    if any(len(rows) != len(gold) for rows, gold in zip(pair, reference)):
        return False
    nonempty = [(rows, gold) for rows, gold in zip(pair, reference) if rows]
    if not nonempty:
        return False  # Already an exact match.
    width = len(nonempty[0][0][0])
    if width < 2 or any(len(gold[0]) != width for _, gold in nonempty):
        return False
    fields = tuple(range(width))
    for order in permutations(fields):
        if order == fields:
            continue
        if all(tuple(sorted(tuple(row[i] for i in order) for row in rows)) == gold
               for rows, gold in nonempty):
            return True
    return False


def replay(item, swap, queries, recorded):
    references = [item['query1'], item['query2']]
    db, _ = build(item)
    try:
        original, first = run_state(db, references, queries)
        perturb(db, swap)
        modified, second = run_state(db, references, queries)
    finally:
        db.close()
    gold = set(zip(original, modified))
    pairs = list(zip(first, second))
    valid = [pair for pair in pairs if None not in pair]
    observed = {}
    for pair in valid:
        observed.setdefault(pair[0], pair)
    expected = (recorded['gold_support_size'], recorded['n_queries'], recorded['n_valid'])
    if (len(gold), len(queries), len(valid)) != expected:
        raise ValueError('Candidate or reference counts differ from E003')
    for rule, kept in [('observed', set(observed.values())), ('stable', set(valid))]:
        hits = len(gold & kept)
        metrics = {
            'recall': hits / len(gold), 'precision': hits / len(kept) if kept else 0,
            'all_found': gold <= kept, 'support_size': len(kept),
        }
        if metrics != recorded[rule]:
            raise ValueError(f'{rule} pruning metrics differ from E003')
    outcomes = []
    for pair in pairs:
        if None in pair:
            outcomes.append(('invalid', False))
        elif pair in gold:
            outcomes.append(('match', False))
        else:
            reordered = any(matches_after_reordering(pair, ref) for ref in gold)
            outcomes.append(('mismatch', reordered))
    return outcomes


def load_queries(model, idx, item):
    record = read(DATA / 'E003' / model / f'{idx}.json')
    if (record['id'], record['db_id'], record['label'], record['status']) != (
        idx, item['db_id'], model, 'ok'
    ):
        raise ValueError(f'E003 record mismatch for {model} {idx}')
    raw = read(DATA / 'E003' / 'api' / model / (record['signature'] + '.json'))
    identity = {k: raw[k] for k in ('payload', 'endpoint_hash', 'config_label')}
    if (digest(json.dumps(identity, sort_keys=True)) != record['signature']
            or raw['response']['model'] != record['model']):
        raise ValueError(f'Cached generation mismatch for {model} {idx}')
    generated = parse_json(raw['response']['choices'][0]['message']['content'])
    return [entry['sql'] for entry in generated['interpretations']], record['metrics']


def prepare(folder):
    plan = read(ROOT / 'experiments' / 'E003-plan.json')
    audit_file = DATA / 'ambiqt-audit' / 'per_item.json'
    if hashlib.sha256(audit_file.read_bytes()).hexdigest() != plan['audit_sha256']:
        raise ValueError('AmbiQT interventions differ from the E003 plan')
    audit = {row['id']: row for row in read(audit_file)}
    items = read(UP / 'benchmark' / 'col-synonyms' / 'validation.json')
    selected, packet, population = [], [], {}
    for model in MODELS:
        counts, eligible = Counter(), []
        for idx in plan['ids']:
            item = items[idx]
            queries, recorded = load_queries(model, idx, item)
            outcomes = replay(item, audit[idx]['swap'], queries, recorded)
            for pos, (sql, (outcome, reordered)) in enumerate(zip(queries, outcomes), 1):
                counts[outcome] += 1
                if outcome != 'mismatch':
                    continue
                counts['match_after_column_reordering'] += reordered
                key = digest(f'AskWise-E011-v1|{model}|{idx}|{pos}')
                public = {
                    'model': model, 'item_id': idx, 'position': pos, 'database': item['db_id'],
                    'sql_sha256': digest(sql), 'match_after_column_reordering': reordered,
                }
                blind = {
                    'question': item['question'], 'candidate': sql,
                    'references': [item['query1'], item['query2']],
                }
                eligible.append((key, public, blind))
        if len(eligible) < SAMPLE_SIZE:
            raise ValueError(f'Too few eligible SQL queries for {model}')
        for key, public, blind in sorted(eligible, key=lambda entry: entry[0])[:SAMPLE_SIZE]:
            case_id = digest('blind|' + key)[:12]
            selected.append({'case': case_id, **public, **blind})
            schema = items[public['item_id']]['schema_without_content']
            packet.append({'case': case_id, **blind, 'schema': schema})
        population[model] = dict(counts)
    selected.sort(key=lambda row: row['case'])
    packet.sort(key=lambda row: row['case'])
    if len({r['case'] for r in packet}) != len(packet):
        raise ValueError('Blinded ID collision')
    write(folder / 'packet.json', packet)
    write(OUT / 'sample.json', {'population': population, 'sample': selected})


def summarize():
    manifest = read(OUT / 'sample.json')
    notes = read(OUT / 'annotations.json')
    by_case = {row['case']: row for row in notes}
    if len(notes) != len(by_case) or set(by_case) != {r['case'] for r in manifest['sample']}:
        raise ValueError('Annotations must cover the sampled cases exactly once')
    groups = {}
    for group in (*MODELS, 'balanced_sample'):
        rows = [r for r in manifest['sample'] if group == 'balanced_sample' or r['model'] == group]
        counts = Counter()
        multilabel = 0
        for row in rows:
            note = by_case[row['case']]
            tags = note['labels']
            if (not tags or set(tags) - set(LABELS) or len(tags) != len(set(tags))
                    or not note['rationale'].strip() or ('unresolved' in tags and len(tags) != 1)):
                raise ValueError(f'Invalid annotation for {row["case"]}')
            counts.update(tags)
            multilabel += len(tags) > 1
        groups[group] = {
            'n': len(rows), 'distinct_questions': len({r['item_id'] for r in rows}),
            'databases': len({r['database'] for r in rows}), 'multilabel_queries': multilabel,
            'match_after_column_reordering': sum(r['match_after_column_reordering'] for r in rows),
            'labels': {k: {'count': counts[k], 'percent': 100 * counts[k] / len(rows)} for k in LABELS},
        }
    write(OUT / 'summary.json', groups)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('prepare').add_argument('folder', type=Path)
    sub.add_parser('summarize')
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.folder)
    else:
        summarize()
