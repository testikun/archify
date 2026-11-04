import argparse, datetime, hashlib, json, os, signal, subprocess, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / 'plan.json').read_text())
parser = argparse.ArgumentParser()
parser.add_argument('--start', type=int, default=0)
parser.add_argument('--limit', type=int)
parser.add_argument('--supplement', action='store_true')
args = parser.parse_args()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

selected = PLAN['supplement']['runs'] if args.supplement else PLAN['runs']
for run in selected[args.start:None if args.limit is None else args.start + args.limit]:
    allowed = PLAN.get('preliminary_project_ids')
    if allowed is not None and run['project_id'] not in allowed:
        print('DEFERRED by user scope:', run['run_id'], flush=True)
        continue
    evidence = Path(run['evidence'])
    metadata_path = evidence / 'execution.json'
    if metadata_path.exists():
        raise RuntimeError('Refusing to overwrite previous run: ' + run['run_id'])
    api_key = json.loads((Path.home() / '.codex/auth.json').read_text()).get('OPENAI_API_KEY')
    if not api_key: raise RuntimeError('Missing local gateway credential')
    env = dict(os.environ, ARCHIFY_BENCH_API_KEY=api_key, ARCHIFY_BENCH_EVIDENCE=str(evidence), ARCHIFY_BENCH_OUTPUT=run['output'],
               NODE_OPTIONS='--require=' + str(ROOT / 'recorder.cjs'), ARCHIFY_UPDATE_CHECK_DISABLED='1',
               ARCHIFY_CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    command = ['codex', 'exec', '--ephemeral', '--ignore-user-config', '--skip-git-repo-check', '-m', 'gpt-6.1-sol',
               '-c', 'model_provider="OpenAI"',
               '-c', 'model_providers.OpenAI.name="OpenAI"',
               '-c', 'model_providers.OpenAI.base_url="http://127.0.0.1:8080/v1"',
               '-c', 'model_providers.OpenAI.wire_api="responses"',
               '-c', 'model_providers.OpenAI.requires_openai_auth=false',
               '-c', 'model_providers.OpenAI.env_key="ARCHIFY_BENCH_API_KEY"',
               '-c', 'model_reasoning_effort="medium"', '-c', 'approval_policy="never"',
               '--sandbox', 'danger-full-access', '--cd', run['workspace'], '--json',
               '--output-last-message', str(evidence / 'final-response.md'), '-']
    metadata = {'run': run, 'model': 'gpt-6.1-sol', 'reasoning': 'medium', 'command': command,
                'started_at': now(), 'time_limit_seconds': 1200}
    metadata_path.write_text(json.dumps(metadata, indent=2) + '\n')
    print('START', run['run_id'], metadata['started_at'], flush=True)
    started = time.monotonic()
    with (evidence / 'stderr.log').open('w') as errors:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
                                   env=env, text=True, start_new_session=True)
        process.stdin.write(Path(run['prompt']).read_text())
        process.stdin.close()
        def record_events():
            with (evidence / 'session.jsonl').open('w') as raw, (evidence / 'events-timed.jsonl').open('w') as timed:
                for line in process.stdout:
                    raw.write(line); raw.flush()
                    timed.write(json.dumps({'received_at': now(), 'event': line.rstrip()}) + '\n'); timed.flush()
        thread = threading.Thread(target=record_events)
        thread.start()
        known = set()
        while process.poll() is None:
            for file in Path(run['output']).rglob('*.json'):
                try:
                    data = file.read_bytes(); parsed = json.loads(data)
                    if not isinstance(parsed, dict) or not parsed.get('diagram_type') or not parsed.get('schema_version'): continue
                    sha = hashlib.sha256(data).hexdigest()
                    if (str(file), sha) in known: continue
                    known.add((str(file), sha))
                    (evidence / 'snapshots').mkdir(exist_ok=True)
                    (evidence / 'snapshots' / (sha + '.json')).write_bytes(data)
                    with (evidence / 'file-revisions.jsonl').open('a') as revisions:
                        revisions.write(json.dumps({'at': now(), 'path': str(file), 'sha256': sha}) + '\n')
                except (OSError, ValueError): pass
            if time.monotonic() - started >= 1200:
                metadata['timeout'] = True
                os.killpg(process.pid, signal.SIGTERM)
                break
            time.sleep(0.05)
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL); process.wait()
        thread.join(timeout=10)
    metadata.update(finished_at=now(), wall_seconds=time.monotonic() - started, exit_code=process.returncode)
    metadata_path.write_text(json.dumps(metadata, indent=2) + '\n')
    print('END', run['run_id'], process.returncode, round(metadata['wall_seconds'], 1), flush=True)
