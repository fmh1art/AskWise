"""Minimal bounded API client. Credentials never enter provenance or errors."""
import hashlib
import json
from pathlib import Path
import time
import httpx
import yaml


class Client:
    def __init__(self, config_path, cache_dir):
        self.config=yaml.safe_load(Path(config_path).read_text())
        self.cache=Path(cache_dir)
        self.cache.mkdir(parents=True,exist_ok=True)
        self.label=Path(config_path).stem

    def call(self, prompt, max_tokens=4096):
        cfg=self.config
        base=cfg['openai_base_url'].rstrip('/')
        hydra='aidp.bytedance.net' in base
        token_key='max_completion_tokens' if hydra else 'max_tokens'
        payload={'model':cfg['llm_name'],'messages':[{'role':'user','content':prompt}], token_key:max_tokens}
        identity={'payload':payload,'endpoint_hash':hashlib.sha256(base.encode()).hexdigest(),'config_label':self.label}
        sig=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        target=self.cache/(sig+'.json')
        if target.exists():
            saved=json.loads(target.read_text())
            if saved.get('valid_text'):
                return saved
        headers={'Authorization':'Bearer '+cfg['key'],'api-key':cfg['key'],'Content-Type':'application/json'}
        params={'api-version':str(cfg['api_version'])} if cfg.get('api_version') else {}
        for attempt in range(3):
            start=time.time()
            record={**identity,'signature':sig,'attempt':attempt,'started_at':start}
            try:
                resp=httpx.post(base+'/chat/completions',headers=headers,params=params,json=payload,timeout=240,trust_env=not hydra)
                record['http_status']=resp.status_code
                if resp.status_code==200:
                    data=resp.json()
                    choice=data.get('choices',[{}])[0]
                    record.update(response=data,valid_text=bool(choice.get('message',{}).get('content')) and choice.get('finish_reason')!='length')
                else:
                    record['valid_text']=False
                    # Avoid raw error bodies which may contain reflected credentials.
                    record['error']='http_failure'
            except Exception as exc:
                record.update(valid_text=False,error=type(exc).__name__)
            record['elapsed_seconds']=time.time()-start
            (self.cache/(sig+f'.attempt{attempt}.{int(start)}.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
            if record['valid_text']:
                target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
                return record
            if record.get('http_status') not in [429,500,502,503,504,None]:
                break
            time.sleep(65 if record.get('http_status')==429 else 5*(attempt+1))
        raise RuntimeError(f'{self.label}: request failed; see sanitized attempts for {sig}')


def parse_json(text):
    text=text.strip()
    if text.startswith('```'):
        text=text.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(text)
