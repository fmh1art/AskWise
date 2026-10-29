"""Retrieve source-provided citation metadata; never manufacture missing fields."""
from pathlib import Path
from html import unescape
import re, json, hashlib, datetime
import httpx

root=Path(__file__).resolve().parents[1]
out=root/'literature/expanded-metadata';out.mkdir(exist_ok=True)
targets={
 'golovin2011adaptive':('author_html','https://www.cs.cmu.edu/~dgolovin/bibtex.htm'),
 'altwaijry2013query':('doi','10.14778/2556549.2556567'),
 'green2007provenance':('doi','10.1145/1265530.1265535'),
 'deshpande2016stochastic':('doi','10.1145/2876506'),
 'he2024verieql':('doi','10.1145/3649849'),
 'yao2019misp':('bib','https://aclanthology.org/D19-1547.bib'),
 'elgohary2020feedback':('bib','https://aclanthology.org/2020.acl-main.187.bib'),
 'zhong2020testsuite':('bib','https://aclanthology.org/2020.emnlp-main.29.bib'),
 'yu2018spider':('bib','https://aclanthology.org/D18-1425.bib'),
 'min2020ambigqa':('bib','https://aclanthology.org/2020.emnlp-main.466.bib'),
 'javdani2014decision':('pmlr','https://proceedings.mlr.press/v33/javdani14.html'),
 'chu2017cosette':('verified_transcription','https://www.cidrdb.org/cidr2017/papers/p51-chu-cidr17.pdf'),
}
records=[];entries=[]
with httpx.Client(timeout=40,follow_redirects=True) as client:
 for key,(kind,source) in targets.items():
    url='https://api.crossref.org/works/'+source+'/transform/application/x-bibtex' if kind=='doi' else source
    raw=out/(key+'.source')
    try:
        if kind=='verified_transcription':
            # The saved metadata was checked on the original CIDR PDF first page.
            # Do not treat PDF bytes or a failed DBLP HTML response as BibTeX.
            metadata=json.loads(raw.read_text())
            assert metadata['source']==url and metadata['pdf_sha256']
            text=(out/(key+'.bib')).read_text()
        else:
            if not raw.exists():
                response=client.get(url);response.raise_for_status();raw.write_text(response.text)
            text=raw.read_text()
        if kind=='pmlr':
            text=unescape(re.search(r'<code[^>]*id="bibtex"[^>]*>(.*?)</code>',text,re.S).group(1))
        if kind=='author_html':
            text=re.search(r'@article\{jair2011,.*?\n\s*\}',unescape(text),re.S).group()
        if not re.search(r'@\w+\s*\{',text):raise ValueError('No BibTeX entry returned')
        text=re.sub(r'(@\w+\s*\{)[^,]+,',lambda m:m[1]+key+',',text,count=1)
        # Protect source title capitalization; no bibliographic fact changes.
        text=re.sub(r'(\btitle\s*=\s*)\{([^{}]*)\}',lambda m:m[1]+'{{'+m[2]+'}}',text,flags=re.I)
        (out/(key+'.bib')).write_text(text.strip()+'\n')
        entries.append(text.strip())
        records.append({'key':key,'status':'verified_transcription' if kind=='verified_transcription' else 'retrieved','source_url':url,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest()})
        print(key,'retrieved',flush=True)
    except Exception as exc:
        records.append({'key':key,'status':'failed','source_url':url,'error':type(exc).__name__})
        print(key,type(exc).__name__,flush=True)
(out/'manifest.json').write_text(json.dumps({'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records},indent=2)+'\n')
(out/'additional.bib').write_text('\n\n'.join(entries)+'\n')
print('retrieved',len(entries),'of',len(targets))
