"""Dispatch the frozen matrix in pairs, never exceeding two Codex sessions."""
import concurrent.futures, datetime, json, subprocess, sys, time
from pathlib import Path

root = Path(__file__).resolve().parent
plan = json.loads((root / 'plan.json').read_text())
records = []
def execute(index, supplemental):
    args = [sys.executable, str(root / 'run.py'), '--start', str(index), '--limit', '1']
    if supplemental: args += ['--supplement']
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = time.monotonic()
    result = subprocess.run(args, cwd=root)
    return {'supplemental': supplemental, 'index': index, 'dispatch_at': started,
            'runner_exit_code': result.returncode, 'wall_seconds': time.monotonic() - before}

for supplemental, runs in [(False, plan['runs']), (True, plan['supplement']['runs'])]:
    for start in range(0, len(runs), 2):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(execute, i, supplemental) for i in range(start, min(start + 2, len(runs))) ]
            records += [f.result() for f in futures]
        (root / 'dispatch.json').write_text(json.dumps(records, indent=2) + '\n')
        if any(r['runner_exit_code'] for r in records):
            raise SystemExit('Runner infrastructure failure retained; inspect before further dispatch.')
