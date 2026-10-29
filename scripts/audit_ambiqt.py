"""Official AmbiQT C split: instance equivalence and controlled data changes."""
from pathlib import Path
import json,sqlite3,hashlib,time,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from a2.worlds import Problem
ROOT=Path(__file__).resolve().parents[1]
UP=Path('/data01/fanmeihao-data/A2-research/upstream/AmbiQT')
OUT=Path('/data01/fanmeihao-data/A2-research/ambiqt-audit')
OUT.mkdir(parents=True,exist_ok=True)

def quote(s):return '"'+s.replace('"','""')+'"'
def canonical(rows):
    # Include SQL types, retain duplicates, ignore order for the main endpoint.
    return tuple(sorted((tuple((type(v).__name__,repr(v)) for v in row) for row in rows)))
def build(item):
    source=UP/'db-content/database'/item['db_id']/(item['db_id']+'.sqlite')
    src=sqlite3.connect(f'file:{source}?mode=ro',uri=True)
    db=sqlite3.connect(':memory:');src.backup(db);src.close()
    db.execute('PRAGMA foreign_keys=OFF')
    targets=[]
    for table,mapping in sorted(item['extra_map'].items()):
        cols=[r[1] for r in db.execute(f'PRAGMA table_info({quote(table)})')]
        fields=[]
        for col in cols:
            if col in mapping:
                fields.extend(quote(col)+' AS '+quote(alias) for alias in mapping[col])
                targets.append((table,mapping[col][1]))
            else: fields.append(quote(col))
        temp='_a2_'+table
        db.execute(f'CREATE TABLE {quote(temp)} AS SELECT '+','.join(fields)+f' FROM {quote(table)}')
        db.execute(f'DROP TABLE {quote(table)}')
        db.execute(f'ALTER TABLE {quote(temp)} RENAME TO {quote(table)}')
    return db,targets

def main():
    path=UP/'benchmark/col-synonyms/validation.json'
    items=json.loads(path.read_text())
    records=[];world_records=[]
    for idx,item in enumerate(items):
        row={'id':idx,'db_id':item['db_id'],'orig_example_idx':item['orig_example_idx']}
        db=None
        try:
            db,targets=build(item)
            db.set_progress_handler(lambda: int(time.monotonic()>deadline),10000)
            def execute(sql):
                nonlocal deadline
                deadline=time.monotonic()+3
                return db.execute(sql).fetchall()
            deadline=time.monotonic()+3
            a=execute(item['query1']);b=execute(item['query2'])
            row.update(equal_observed=canonical(a)==canonical(b),ordered_equal_observed=a==b)
            swap=None
            for table,col in targets:
                deadline=time.monotonic()+3
                vals=db.execute(f'SELECT rowid,{quote(col)} FROM {quote(table)} WHERE {quote(col)} IS NOT NULL ORDER BY rowid').fetchall()
                if not vals:continue
                first=vals[0]
                second=next((v for v in vals[1:] if type(v[1]) is type(first[1]) and v[1]!=first[1]),None)
                if second is None:continue
                db.execute(f'UPDATE {quote(table)} SET {quote(col)}=? WHERE rowid=?',(second[1],first[0]))
                db.execute(f'UPDATE {quote(table)} SET {quote(col)}=? WHERE rowid=?',(first[1],second[0]))
                swap={'table':table,'column':col,'rowids':[first[0],second[0]]};break
            if swap is None:
                row.update(status='no_distinct_values');records.append(row);continue
            c=execute(item['query1']);d=execute(item['query2'])
            row.update(status='ok',equal_changed=canonical(c)==canonical(d),swap=swap)
            answers=[canonical(a),canonical(c),canonical(b),canonical(d)]
            p=Problem([(0,0),(0,1),(1,0),(1,1)],answers,name=str(idx))
            row['invariant_all']=len(set(answers))==1
            row['methods']={}
            for method in ['none','ask_all','fixed','repair_first','ec2','optimal','local','observed_then_repair']:
                rr=[p.run(i,method) for i in range(4)]
                row['methods'][method]={key:sum(float(r[key]) for r in rr)/4 for key in ['correct','questions']}
            world_records.append({'id':idx,'db_id':item['db_id'],'question':item['question'],'query1':item['query1'],'query2':item['query2'],'worlds':p.worlds,'answers':answers,'swap':swap})
        except Exception as e:
            row.update(status='error',error=type(e).__name__+': '+str(e))
        finally:
            if db is not None:db.close()
        records.append(row)
    (OUT/'per_item.json').write_text(json.dumps(records,indent=2)+'\n')
    (OUT/'worlds.json').write_text(json.dumps(world_records,indent=2)+'\n')
    ok=[r for r in records if r['status']=='ok']
    summary={'n_total':len(items),'n_ok':len(ok),'n_error':sum(r['status']=='error' for r in records),'n_no_distinct':sum(r['status']=='no_distinct_values' for r in records),
      'n_equal_observed':sum(r.get('equal_observed',False) for r in records),
      'n_equal_then_different':sum(r['equal_observed'] and not r['equal_changed'] for r in ok),
      'n_invariant_all':sum(r['invariant_all'] for r in ok),'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'methods':{m:{k:sum(r['methods'][m][k] for r in ok)/len(ok) for k in ['correct','questions']} for m in ok[0]['methods']} if ok else {'n_total':len(items),'n_ok':0}
    dest=ROOT/'results/E002';dest.mkdir(parents=True,exist_ok=True)
    (dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (dest/'audit_status.json').write_text(json.dumps([{k:v for k,v in r.items() if k not in ['methods','swap']} for r in records],indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
