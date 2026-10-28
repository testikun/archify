#!/usr/bin/env python3
"""Read-only GitHub refresh; every response stays in this investigation."""
import datetime, json, os, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'receipts' / 'github'
OUT.mkdir(parents=True, exist_ok=True)
queries = {
    'issue-452': 'repos/tt-a1i/archify/issues/452',
    'comments-452': 'repos/tt-a1i/archify/issues/452/comments?per_page=100',
    'timeline-452': 'repos/tt-a1i/archify/issues/452/timeline?per_page=100',
    'dev': 'repos/tt-a1i/archify/branches/dev',
    'related-prs': 'search/issues?q=repo%3Att-a1i%2Farchify+is%3Apr+%22452%22&per_page=100',
    'ordered-prs': 'search/issues?q=repo%3Att-a1i%2Farchify+is%3Apr+%22ordered%22&per_page=100',
    'open-prs': 'repos/tt-a1i/archify/pulls?state=open&per_page=100',
    'issue-1045': 'repos/tt-a1i/archify/issues/1045',
    'comments-1045': 'repos/tt-a1i/archify/issues/1045/comments?per_page=100',
    'pr-1036': 'repos/tt-a1i/archify/pulls/1036',
    'comments-pr-1036': 'repos/tt-a1i/archify/issues/1036/comments?per_page=100',
    'issue-1047': 'repos/tt-a1i/archify/issues/1047',
    'comments-1047': 'repos/tt-a1i/archify/issues/1047/comments?per_page=100',
    'pr-1047': 'repos/tt-a1i/archify/pulls/1047',
    'pr-289': 'repos/tt-a1i/archify/pulls/289',
}
env = dict(os.environ, NO_PROXY='api.github.com', no_proxy='api.github.com')
manifest = {'fetchedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'requests': []}
for name, endpoint in queries.items():
    p = subprocess.run(['gh', 'api', '--paginate', endpoint], env=env, capture_output=True, text=True)
    (OUT / (name + '.json')).write_text(p.stdout)
    (OUT / (name + '.stderr.txt')).write_text(p.stderr)
    manifest['requests'].append({'name': name, 'endpoint': endpoint, 'exit': p.returncode})
    print(name, p.returncode)
(OUT / 'refresh.json').write_text(json.dumps(manifest, indent=2) + '\n')
