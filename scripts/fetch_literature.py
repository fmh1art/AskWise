"""Fetch publisher-supplied bibliography and primary PDFs; no inferred DOIs."""
from pathlib import Path
import httpx,json,time
root=Path(__file__).resolve().parents[1]
out=Path('/data01/fanmeihao-data/A2-research/literature');out.mkdir(exist_ok=True)
sources={
 'ambiqt':('https://aclanthology.org/2023.emnlp-main.436.pdf','https://aclanthology.org/2023.emnlp-main.436.bib'),
 'disambiguate':('https://aclanthology.org/2025.findings-acl.863.pdf','https://aclanthology.org/2025.findings-acl.863.bib'),
 'practiq':('https://aclanthology.org/2025.naacl-long.13.pdf','https://aclanthology.org/2025.naacl-long.13.bib'),
 'ec2':('https://proceedings.neurips.cc/paper/2010/file/1e6e0a04d20f50967c64dac2d639a577-Paper.pdf',None),
 'cleaning':('https://i.cs.hku.hk/~ckcheng/papers/icde13-uncertain.pdf','https://api.crossref.org/works/10.1109/ICDE.2013.6544820/transform/application/x-bibtex'),
 'sphinteract':('https://www.vldb.org/pvldb/vol18/p1145-zhao.pdf',None)}
receipt=[];bib=[]
for name,(pdf,biburl) in sources.items():
    for suffix,url in [('pdf',pdf),('bib',biburl)]:
        if url is None:continue
        try:
            r=httpx.get(url,follow_redirects=True,timeout=50)
            record={'name':name,'url':url,'status':r.status_code,'bytes':len(r.content)}
            if r.status_code==200:
                (out/(name+'.'+suffix)).write_bytes(r.content)
                if suffix=='bib':bib.append(r.text)
        except Exception as e:record={'name':name,'url':url,'error':type(e).__name__}
        receipt.append(record);print(record,flush=True)
(root/'literature/fetch-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(root/'literature/publisher.bib').write_text('\n\n'.join(bib))
