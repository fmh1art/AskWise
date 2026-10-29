"""Verify completed evidence without issuing model requests."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,yaml
root=Path(__file__).resolve().parents[1]
data=Path('/data01/fanmeihao-data/A2-research')
plan=json.loads((root/'experiments/E003-plan.json').read_text())
receipt={'planned_per_model':plan['n'],'models':{},'source_databases_verified':0,'secret_scan':'pending'}
up=data/'upstream/AmbiQT'
dbs={r['db_id'] for r in json.loads((up/'benchmark/col-synonyms/validation.json').read_text())}
with zipfile.ZipFile(up/'db-content.zip') as z:
    for db in dbs:
        member=f'db-content/database/{db}/{db}.sqlite'
        assert hashlib.sha256(z.read(member)).digest()==hashlib.sha256((up/member).read_bytes()).digest()
        receipt['source_databases_verified']+=1
for model in ['doubao_seed2_lite','gpt5_6_sol_hydra']:
    stats={'completed':0,'verified_response':0,'failed':0}
    for idx in plan['ids']:
        path=data/'E003'/model/(str(idx)+'.json')
        if not path.exists():continue
        r=json.loads(path.read_text());assert r['id']==idx and r['label']==model
        stats['completed']+=1;stats['failed']+=int(r['status']!='ok')
        if r.get('signature'):
            raw=json.loads((data/'E003/api'/model/(r['signature']+'.json')).read_text())
            identity={k:raw[k] for k in ['payload','endpoint_hash','config_label']}
            sig=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
            assert sig==r['signature'] and raw['response']['model']==r['model']
            assert raw['response']['usage']==r['usage']
            stats['verified_response']+=1
    receipt['models'][model]=stats
# Scan the exact tracked publication boundary, not external data or home files.
keys=[str(yaml.safe_load((Path('/home/fanmeihao/projects/_llm_configs')/(name+'.yaml')).read_text())['key']).encode() for name in ['gpt5_6_sol_hydra','doubao_seed2_lite']]
for repo in [root,root.parent/'A2-paper']:
    names=subprocess.check_output(['git','-C',str(repo),'ls-files','-z']).split(b'\0')
    for n in names:
        if not n:continue
        content=(repo/n.decode()).read_bytes()
        assert not any(k in content for k in keys),'credential detected in tracked artifact'
receipt['secret_scan']='passed'
receipt['complete']=all(v['completed']==plan['n'] for v in receipt['models'].values())
(root/'results/verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
