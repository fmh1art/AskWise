from pathlib import Path
import sys,json,hashlib,time,sqlite3,concurrent.futures,collections
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from a2.api import Client,parse_json
from scripts.audit_ambiqt import build,canonical,quote,UP
ROOT=Path(__file__).resolve().parents[1]
DATA=Path('/data01/fanmeihao-data/A2-research')
OUT=DATA/'E003';OUT.mkdir(exist_ok=True)

def freeze():
    p=ROOT/'experiments/E003-plan.json'
    if p.exists():return json.loads(p.read_text())
    audit=json.loads((DATA/'ambiqt-audit/per_item.json').read_text())
    groups=collections.defaultdict(list)
    for r in audit:
        if r['status']=='ok':groups[r['db_id']].append(r)
    ids=[]
    for db,rows in sorted(groups.items()):
        seen=set();chosen=[]
        for r in sorted(rows,key=lambda r:hashlib.sha256(('A2-E003-20261029'+str(r['id'])).encode()).hexdigest()):
            if r['orig_example_idx'] in seen:continue
            seen.add(r['orig_example_idx']);chosen.append(r['id'])
            if len(chosen)==8:break
        ids.extend(chosen)
    plan={'ids':ids,'n':len(ids),'seed':'A2-E003-20261029','audit_sha256':hashlib.sha256((DATA/'ambiqt-audit/per_item.json').read_bytes()).hexdigest()}
    p.write_text(json.dumps(plan,indent=2)+'\n');return plan

def execute(db,sql):
    deadline=time.monotonic()+4
    db.set_progress_handler(lambda:int(time.monotonic()>deadline),10000)
    db.execute('PRAGMA query_only=ON')
    allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_RECURSIVE}
    db.set_authorizer(lambda action,*_:sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
    try:
        rows=db.execute(sql).fetchmany(10001)
        if len(rows)>10000:raise ValueError('result_row_limit')
        return canonical(rows)
    finally:
        db.set_authorizer(None);db.set_progress_handler(None,0)
        db.execute('PRAGMA query_only=OFF')

def perturb(db,swap):
    t,c=swap['table'],swap['column'];i,j=swap['rowids']
    a=db.execute(f'SELECT {quote(c)} FROM {quote(t)} WHERE rowid=?',(i,)).fetchone()[0]
    b=db.execute(f'SELECT {quote(c)} FROM {quote(t)} WHERE rowid=?',(j,)).fetchone()[0]
    db.execute(f'UPDATE {quote(t)} SET {quote(c)}=? WHERE rowid=?',(b,i))
    db.execute(f'UPDATE {quote(t)} SET {quote(c)}=? WHERE rowid=?',(a,j))

def score(item,swap,queries):
    db,_=build(item)
    try:
        gold0=[execute(db,item[k]) for k in ['query1','query2']]
        cand0=[];errors=[]
        for q in queries:
            try:cand0.append(execute(db,q))
            except Exception as e:cand0.append(None);errors.append(type(e).__name__)
        perturb(db,swap)
        gold1=[execute(db,item[k]) for k in ['query1','query2']]
        cand1=[]
        for q in queries:
            try:cand1.append(execute(db,q))
            except Exception as e:cand1.append(None);errors.append(type(e).__name__)
        gold=set(zip(gold0,gold1))
        valid=[(a,b) for a,b in zip(cand0,cand1) if a is not None and b is not None]
        stable=set(valid)
        observed={}
        for a,b in valid:observed.setdefault(a,(a,b))
        observed=set(observed.values())
        def metrics(s):return {'recall':len(s&gold)/len(gold),'precision':len(s&gold)/len(s) if s else 0,'all_found':gold<=s,'support_size':len(s)}
        return {'stable':metrics(stable),'observed':metrics(observed),'gold_support_size':len(gold),'n_queries':len(queries),'n_valid':len(valid),'sql_errors':errors}
    finally:db.close()

def main():
    plan=freeze()
    if '--freeze-only' in sys.argv:
        print(json.dumps(plan,indent=2));return
    items=json.loads((UP/'benchmark/col-synonyms/validation.json').read_text())
    audit={r['id']:r for r in json.loads((DATA/'ambiqt-audit/per_item.json').read_text())}
    for label in ['doubao_seed2_lite','gpt5_6_sol_hydra']:
        client=Client('/home/fanmeihao/projects/_llm_configs/'+label+'.yaml',OUT/'api'/label)
        dest=OUT/label;dest.mkdir(exist_ok=True)
        def run(idx):
            target=dest/(str(idx)+'.json')
            if target.exists():return json.loads(target.read_text())
            item=items[idx]
            prompt='''Translate an ambiguous question into the distinct plausible SQLite SELECT queries it can mean. Use the schema exactly. Return JSON only: {"interpretations":[{"meaning":"short explanation", "sql":"SELECT ..."}]}. Include up to four genuinely different plausible readings; do not invent columns or irrelevant interpretations. No data modification. The schema may contain columns with overlapping names.\nSchema:\n'''+item['schema_without_content']+'\nQuestion:\n'+item['question']
            r={'id':idx,'db_id':item['db_id'],'label':label}
            try:
                response=client.call(prompt,4096)
                r.update(signature=response['signature'],model=response['response'].get('model'),usage=response['response'].get('usage'),elapsed_seconds=response['elapsed_seconds'])
                result=parse_json(response['response']['choices'][0]['message']['content'])
                queries=[x['sql'] for x in result['interpretations']]
                if not (1<=len(queries)<=4) or not all(isinstance(q,str) for q in queries):raise ValueError('invalid_interpretation_count_or_type')
                r.update(status='ok',metrics=score(item,audit[idx]['swap'],queries))
            except Exception as e:r.update(status='failure',error=type(e).__name__)
            target.write_text(json.dumps(r,indent=2)+'\n')
            return r
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for n,f in enumerate(concurrent.futures.as_completed([pool.submit(run,i) for i in plan['ids']]),1):
                r=f.result()
                (OUT/'progress.json').write_text(json.dumps({'model':label,'completed':n,'total':plan['n'],'last_status':r['status'],'updated_at':time.time()},indent=2)+'\n')
                print(label,n,plan['n'],r['status'],flush=True)
    print('E003 completed',flush=True)

if __name__=='__main__':main()
