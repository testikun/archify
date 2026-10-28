#!/usr/bin/env python3
"""Extract immutable GitHub sources without touching any shared checkout."""
import hashlib
import json
import pathlib
import subprocess
import tarfile

root = pathlib.Path(__file__).resolve().parents[1]
sha = '6ca6a5c84439b57ea22e0630fe306e1d91587a6e'
archive = root / 'source-6ca6a5c.tar.gz'
url = f'https://codeload.github.com/tt-a1i/archify/tar.gz/{sha}'
if not archive.exists():
    subprocess.run(['curl', '-L', '--fail', '--max-time', '300', '-o', str(archive), url], check=True)
source = root / 'source'
if source.exists():
    raise SystemExit('source already exists; preserve it and use a fresh investigation copy.')
source.mkdir()
prefix = f'archify-{sha}/'
selected = []
with tarfile.open(archive, 'r:gz') as tar:
    for item in tar:
        if not item.name.startswith(prefix):
            continue
        relative = item.name[len(prefix):]
        head = relative.split('/')[0]
        if head not in {'.agents', 'archify', 'test', 'scripts', 'viewer'} and '/' in relative:
            continue
        if head == 'archify.zip' or not relative or item.issym() or item.islnk():
            continue
        if relative.startswith('archify/examples/') and relative.endswith('.html'):
            continue
        item.name = relative
        tar.extract(item, source, filter='data')
        if item.isfile():
            selected.append(relative)
manifest = {'sha': sha, 'url': url, 'archiveSha256': hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest(), 'files': {p: hashlib.sha256((source / p).read_bytes()).hexdigest() for p in selected}}
(root / 'evidence/source.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Extracted {len(selected)} fixed-version files at {sha}')
