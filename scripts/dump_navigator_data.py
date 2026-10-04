# Run `cd navigator && python3 -m web --port 8765` first, then this script, to refresh public/navigator/data.
import json, hashlib, urllib.request, urllib.parse, pathlib, shutil
B="http://localhost:8765"
OUT=pathlib.Path("/dev-server/public/navigator/data")
def get(path, **q):
    q={k:v for k,v in q.items() if v not in ("",None)}
    url=B+path+("?"+urllib.parse.urlencode(q) if q else "")
    with urllib.request.urlopen(url) as r: return r.read().decode()
if OUT.exists(): shutil.rmtree(OUT)
(OUT/"lookup").mkdir(parents=True); (OUT/"source").mkdir()
meta=json.loads(get("/api/meta")); (OUT/"meta.json").write_text(json.dumps(meta,ensure_ascii=False))
for n in ("rules","changes","pipeline"): (OUT/f"{n}.json").write_text(get(f"/api/{n}"))
pairs=set()
def walk(o):
    if isinstance(o,dict):
        d=o.get("doc_id") or o.get("source_doc_id"); q=o.get("quoted_span")
        if d and q is not None: pairs.add((d,q))
        for v in o.values(): walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
walk(json.loads((OUT/"rules.json").read_text()))
for a in meta["addresses"]:
    t=get("/api/lookup",address_id=a["address_id"],as_of=meta["default_date"])
    (OUT/"lookup"/(a["address_id"]+".json")).write_text(t); walk(json.loads(t))
walk(json.loads((OUT/"changes.json").read_text()))
for d,q in sorted(pairs):
    h=hashlib.sha1((d+"|"+q).encode()).hexdigest()[:16]
    (OUT/"source"/(h+".json")).write_text(get("/api/source",doc_id=d,quote=q))
print(len(meta["addresses"]),len(pairs))
