"""Create a local review archive after all scheduled sessions have finished."""
import hashlib,json,tarfile
from pathlib import Path
root=Path(__file__).resolve().parent
plan=json.loads((root/'plan.json').read_text())
for run in plan['runs']+plan['supplement']['runs']:
    meta=Path(run['evidence'])/'execution.json'
    if not meta.exists() or not json.loads(meta.read_text()).get('finished_at'):
        raise SystemExit('Scheduled generation still pending: '+run['run_id'])
excluded={'__pycache__','evidence-archive.tar.gz','evidence-archive.sha256','bundle-manifest.json','bundle-notes.md'}
files=[]
for file in sorted(root.rglob('*')):
    if not file.is_file():continue
    parts=file.relative_to(root).parts
    if any(part in excluded for part in parts):continue
    if parts[0]=='runs' and len(parts)>3 and parts[2]=='workspace':
        if parts[3]=='archify':continue
        if parts[3]=='project' and not (len(parts)==5 and parts[4]=='BUSINESS.md' and parts[1] in {r['run_id'] for r in plan['supplement']['runs']}):continue
    files.append(file)
key=json.loads((Path.home()/'.codex/auth.json').read_text()).get('OPENAI_API_KEY','')
secret_matches=[str(p.relative_to(root)) for p in files if key and key.encode() in p.read_bytes()]
if secret_matches:raise SystemExit('Known gateway credential detected; preserve originals and prepare a redacted archive before publishing. Affected file count: '+str(len(secret_matches)))
manifest={'files':[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
 'known_gateway_credential_matches':len(secret_matches),
 'exclusions':['Public source-project checkouts are linked by pinned commit, not redistributed.','Per-run package copies are excluded; both frozen canonical Archify packages are included once.','Python caches and the archive itself are excluded.'],
 'publication':'Local archive only. No external upload or GitHub posting.',
 'sanitization_limit':'Checks the configured gateway credential literally. This is not an independent audit for every possible sensitive string. Original native events and meaningful failures are preserved.'}
(root/'bundle-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=root/'evidence-archive.tar.gz'
with tarfile.open(archive,'w:gz') as bundle:
    for p in files+[root/'bundle-manifest.json']:bundle.add(p,arcname='benchmark-20261104/'+str(p.relative_to(root)),recursive=False)
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
(root/'evidence-archive.sha256').write_text(sha+'  '+archive.name+'\n')
(root/'bundle-notes.md').write_text('# Local evidence archive\n\n[Download archive](evidence-archive.tar.gz) · [file manifest](bundle-manifest.json) · [SHA-256](evidence-archive.sha256)\n\nSHA-256: `'+sha+'`\n\nLocation: `'+str(archive)+'`. Retain this directory and archive through review and the resulting release cycle. No public upload has been performed. Source-project checkouts are excluded; use the pinned source links in the report. The two frozen Archify packages are included once. No configured gateway credential was found in bundled bytes. Native traces, failed commands and prior JSON revisions remain intact.\n')
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha,'files':len(files)}))
