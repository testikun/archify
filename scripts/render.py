#!/usr/bin/env python3
"""Run the public CLI on the pinned source and preserve successes and failures."""
import datetime, json, os, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source-pinned'
SHA = '6ca6a5c84439b57ea22e0630fe306e1d91587a6e'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip() == SHA
OUT = ROOT / 'artifacts'
LOG = ROOT / 'receipts' / 'cli'
OUT.mkdir(exist_ok=True); LOG.mkdir(parents=True,exist_ok=True)
cli = SOURCE / 'archify' / 'bin' / 'archify.mjs'
(ROOT/'tmp').mkdir(exist_ok=True)
os.environ['TMPDIR']=str(ROOT/'tmp')
records = []
def run(name,args):
    cmd=['node',str(cli),*map(str,args)]
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    (LOG/(name+'.stdout.txt')).write_text(p.stdout)
    (LOG/(name+'.stderr.txt')).write_text(p.stderr)
    records.append({'name':name,'command':cmd,'exit':p.returncode})
    print(name,p.returncode,flush=True)
    return p

for f in sorted((ROOT/'inputs').glob('*.json')):
    d=json.loads(f.read_text())
    if 'diagram_type' not in d:continue
    t=d['diagram_type']; stem=f.stem
    v=run(stem+'.validate',['validate',t,f,'--json'])
    if v.returncode:continue
    p=run(stem+'.deliver',['deliver',t,f,OUT/(stem+'.html'),'--json'])
    if not p.returncode:run(stem+'.check',['check',OUT/(stem+'.html'),'--json'])

run('story-scan',['story','scan',OUT/'parallel-architecture.html','--json'])
run('story-attach',['story','attach',OUT/'ablation-architecture-no-cards.html',ROOT/'inputs'/'parallel-story-brief.json',OUT/'parallel-story.html','--json'])
(LOG/'commands.json').write_text(json.dumps({'sourceSha':SHA,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':records},indent=2)+'\n')
