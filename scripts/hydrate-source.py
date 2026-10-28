#!/usr/bin/env python3
"""Fill a sparse local snapshot via GitHub blobs, checking every Git object hash."""
import base64, concurrent.futures, hashlib, json, os, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEST=ROOT/'source-pinned'
tree=json.loads((ROOT/'receipts/github/dev-tree.json').read_text())
env=dict(os.environ,NO_PROXY='api.github.com,raw.githubusercontent.com',no_proxy='api.github.com,raw.githubusercontent.com')
def wanted(f):
    p=f['path']
    return f['type']=='blob' and (('/' not in p and p!='archify.zip') or p.startswith(('archify/','viewer/')) or p in ['test/helpers/desktop-browser.mjs','test/story-browser.test.mjs']) and not (p.startswith('archify/examples/') and p.endswith('.html'))
def digest(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def fill(f):
    p=DEST/f['path']
    if p.exists() and digest(p.read_bytes())==f['sha']:return {'path':f['path'],'sha':f['sha'],'fetched':False}
    url='https://raw.githubusercontent.com/tt-a1i/archify/6ca6a5c84439b57ea22e0630fe306e1d91587a6e/'+f['path']
    r=subprocess.run(['curl','--compressed','--fail','--silent','--show-error','--connect-timeout','10','--max-time','120',url],env=env,capture_output=True,timeout=130)
    data=r.stdout
    if r.returncode or digest(data)!=f['sha']:
        r=subprocess.run(['gh','api','repos/tt-a1i/archify/git/blobs/'+f['sha']],env=env,capture_output=True,timeout=130)
        if r.returncode:return {'path':f['path'],'error':r.stderr.decode()}
        blob=json.loads(r.stdout);assert blob['encoding']=='base64';data=base64.b64decode(blob['content'])
    assert digest(data)==f['sha'],f['path']
    p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
    if f.get('mode')=='100755':p.chmod(0o755)
    return {'path':f['path'],'sha':f['sha'],'fetched':True}
selected=[f for f in tree['tree'] if wanted(f)]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(fill,selected))
(ROOT/'receipts/source-files.json').write_text(json.dumps({'tree':tree['sha'],'files':results},indent=2)+'\n')
print('Verified',sum('error' not in x for x in results),'files; fetched',sum(x.get('fetched',False) for x in results))
assert not any('error' in x for x in results), 'Some source files are unavailable; see receipts/source-files.json'
