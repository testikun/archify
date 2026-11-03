"""Collect/replay/capture newly completed sessions without touching active runs."""
from pathlib import Path
import json
import subprocess

root = Path(__file__).resolve().parent
plan = json.loads((root / 'plan.json').read_text())
completed = []
active = []
for run in plan['runs']:
    p = Path(run['evidence']) / 'execution.json'
    if not p.exists():
        continue
    data = json.loads(p.read_text())
    (completed if data.get('finished_at') else active).append(run['run_id'])
metrics = root / 'observations.json'
observed = json.loads(metrics.read_text()) if metrics.exists() else []
new = set(completed) - {r['run_id'] for r in observed}
if new:
    for name, command in [('collect', ['python3', 'collect.py']), ('replay', ['python3', 'replay.py']), ('capture', ['node', 'capture.mjs'])]:
        with (root / (name + '.log')).open('a') as output:
            subprocess.run(command, cwd=root, stdout=output, stderr=subprocess.STDOUT, check=True)
    observed = json.loads(metrics.read_text())
print(json.dumps({'completed': len(completed), 'planned': len(plan['runs']), 'active': active, 'newly_collected': sorted(new),
                  'results': [{k: row[k] for k in ['run_id', 'execution_exit_code', 'timeout', 'repair_rounds', 'relative_coordinates_in_final']} for row in observed]}, indent=2))
