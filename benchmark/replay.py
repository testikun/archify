import hashlib, json, os, re, subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
observations = json.loads((root / 'observations.json').read_text())
plan = json.loads((root / 'plan.json').read_text())
runs = {run['run_id']: run for run in plan['runs']}
summary_path = root / 'replay/summary.json'
cached = {r['run_id']: r for r in json.loads(summary_path.read_text())} if summary_path.exists() else {}
results = []
for observed in observations:
    if not observed['final_json'] or observed['run_id'] not in runs: continue
    run = runs[observed['run_id']]
    input_path = Path(observed['final_json'])
    input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()
    if cached.get(run['run_id'], {}).get('input_sha256') == input_hash:
        results.append(cached[run['run_id']])
        continue
    out = root / 'replay' / run['run_id']
    out.mkdir(parents=True, exist_ok=True)
    row = {'run_id': run['run_id'], 'input_sha256': input_hash}
    if observed['first_json']:
        first = Path(run['evidence']) / observed['first_json']
        cli = root / 'packages' / run['arm'] / 'archify/bin/archify.mjs'
        checked = subprocess.run(['node', str(cli), 'validate', 'architecture', str(first),
                                  '--repo-root', str(Path(run['workspace']) / 'project'), '--json'],
                                 cwd=run['workspace'], env=dict(os.environ, ARCHIFY_UPDATE_CHECK_DISABLED='1'), text=True, capture_output=True)
        (out / 'first-draft.validate.json').write_text(checked.stdout)
        (out / 'first-draft.validate.stderr').write_text(checked.stderr)
        row['first_draft_validation_exit'] = checked.returncode
    for arm in ['base', 'candidate']:
        cli = root / 'packages' / arm / 'archify/bin/archify.mjs'
        repo = str(Path(run['workspace']) / 'project')
        for kind, args in [
            ('layout', ['validate', 'architecture', str(input_path), '--repo-root', repo, '--layout-json']),
            ('deliver', ['deliver', 'architecture', str(input_path), str(out / (arm + '.html')), '--repo-root', repo, '--json']),
        ]:
            result = subprocess.run(['node', str(cli), *args], cwd=run['workspace'],
                                    env=dict(os.environ, ARCHIFY_UPDATE_CHECK_DISABLED='1'), text=True, capture_output=True)
            (out / f'{arm}.{kind}.json').write_text(result.stdout)
            (out / f'{arm}.{kind}.stderr').write_text(result.stderr)
            row[f'{arm}_{kind}_exit'] = result.returncode
        assert hashlib.sha256(input_path.read_bytes()).hexdigest() == input_hash
    row['identical_layout'] = json.loads((out / 'base.layout.json').read_text()) == json.loads((out / 'candidate.layout.json').read_text())
    if (out / 'base.html').exists() and (out / 'candidate.html').exists():
        svg = lambda file: re.search(r'<svg\b[\s\S]*?</svg>', file.read_text()).group(0)
        row['identical_canonical_svg'] = svg(out / 'base.html') == svg(out / 'candidate.html')
    results.append(row)
summary_path.parent.mkdir(exist_ok=True)
summary_path.write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
