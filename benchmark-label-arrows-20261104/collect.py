"""Collect observable counters; semantic/visual review remains a separate step."""
import datetime, hashlib, json, re, subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
plan = json.loads((root / 'plan.json').read_text())
summary = []
for run in plan['runs'] + plan['supplement']['runs']:
    evidence = Path(run['evidence'])
    execution = evidence / 'execution.json'
    if not execution.exists(): continue
    metadata = json.loads(execution.read_text())
    if not metadata.get('finished_at'): continue
    events = [json.loads(line) for line in (evidence / 'session.jsonl').read_text().splitlines()]
    commands = [event['item'] for event in events if event.get('type') == 'item.completed' and event.get('item', {}).get('type') == 'command_execution']
    usages = [event['usage'] for event in events if event.get('type') == 'turn.completed' and 'usage' in event]
    usage = {key: sum(item[key] for item in usages) if all(key in item for item in usages) else None for key in ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens']} if usages else None
    if usage: usage['uncached_input_tokens'] = usage['input_tokens'] - usage['cached_input_tokens']
    attempts = []
    captures = evidence / 'cli-inputs.jsonl'
    cli_invocations = []
    if captures.exists():
        for line in captures.read_text().splitlines():
            capture = json.loads(line)
            argv = capture['argv']
            if not argv[1].endswith('/bin/archify.mjs') or argv[2] not in ('validate', 'render', 'deliver', 'finalize'): continue
            cli_invocations.append(capture)
            if not attempts or attempts[-1]['sha256'] != capture['sha256']:
                attempts.append(capture)
    revisions_path = evidence / 'file-revisions.jsonl'
    revisions = [json.loads(line) for line in revisions_path.read_text().splitlines()] if revisions_path.exists() else []
    observed_versions = revisions + cli_invocations
    observed_versions.sort(key=lambda item: datetime.datetime.fromisoformat(item['at'].replace('Z', '+00:00')))
    first = observed_versions[0] if observed_versions else None
    precheck_hashes = []
    if attempts:
        first_check = datetime.datetime.fromisoformat(attempts[0]['at'].replace('Z', '+00:00'))
        for version in observed_versions:
            if datetime.datetime.fromisoformat(version['at'].replace('Z', '+00:00')) > first_check: break
            if not precheck_hashes or precheck_hashes[-1] != version['sha256']: precheck_hashes.append(version['sha256'])
    candidates = []
    receipts = []
    for file in Path(run['output']).rglob('*.json'):
        try: data = json.loads(file.read_text())
        except (ValueError, OSError): continue
        if isinstance(data, dict) and data.get('diagram_type') == 'architecture' and data.get('schema_version'):
            candidates.append({'path': str(file), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'data': data})
        if file.name.endswith('.delivery.json'): receipts.append((file, data))
    final = candidates[0] if len(candidates) == 1 else None
    if len(candidates) > 1:
        last_hash = attempts[-1]['sha256'] if attempts else None
        final = next((c for c in candidates if c['sha256'] == last_hash), None)
    html = [str(p) for p in Path(run['output']).rglob('*.html')
            if re.search(r'<svg\b[^>]*aria-labelledby="archify-diagram-title', p.read_text())]
    receipt_integrity = []
    for file, receipt in receipts:
        output = Path(receipt.get('output', ''))
        receipt_integrity.append({
            'path': str(file), 'status': receipt.get('status'),
            'matches_final_json': bool(final and receipt.get('specification', {}).get('sha256') == final['sha256']),
            'matches_artifact': output.is_file() and hashlib.sha256(output.read_bytes()).hexdigest() == receipt.get('artifact', {}).get('sha256'),
        })
    source_status = None
    source_commit_after = None
    source_pin_matches = None
    project = Path(run['workspace']) / 'project'
    if (project / '.git').exists():
        checked = subprocess.run(['git', '-C', str(project), 'status', '--porcelain'], text=True, capture_output=True)
        source_status = checked.stdout
        source_commit_after = subprocess.check_output(['git', '-C', str(project), 'rev-parse', 'HEAD'], text=True).strip()
        source_pin_matches = source_commit_after == run['project_commit']
    else:
        brief = next(p for p in plan['supplement']['projects'] if p['id'] == run['project_id'])
        source_pin_matches = hashlib.sha256((project/'BUSINESS.md').read_bytes()).hexdigest() == brief['brief_sha256']
    package = Path(run['workspace']) / 'archify'
    expected = root / 'packages' / run['arm'] / 'archify'
    changed_package = [str(p.relative_to(expected)) for p in expected.rglob('*') if p.is_file() and (not (package / p.relative_to(expected)).is_file() or p.read_bytes() != (package / p.relative_to(expected)).read_bytes())]
    added_package = [str(p.relative_to(package)) for p in package.rglob('*') if p.is_file() and not (expected / p.relative_to(package)).exists()]
    row = {
        'run_id': run['run_id'], 'project_id': run['project_id'], 'arm': run['arm'],
        'execution_exit_code': metadata.get('exit_code'), 'timeout': metadata.get('timeout', False),
        'wall_seconds_descriptive_only': metadata['wall_seconds'], 'usage': usage,
        'time_to_first_json_seconds_descriptive_only': (datetime.datetime.fromisoformat(first['at'].replace('Z', '+00:00')) - datetime.datetime.fromisoformat(metadata['started_at'])).total_seconds() if first else None,
        'time_to_first_cli_seconds_descriptive_only': (datetime.datetime.fromisoformat(attempts[0]['at'].replace('Z', '+00:00')) - datetime.datetime.fromisoformat(metadata['started_at'])).total_seconds() if attempts else None,
        'cli_execution_seconds': None, 'queue_seconds': None,
        'unavailable_timing_reason': 'Native client events do not isolate CLI runtime or provider queue/network waits; event arrival timestamps are retained without treating them as CPU time.',
        'cost': None, 'cost_reason': 'Cost accounting deferred by user.',
        'tool_commands': len(commands), 'failed_tool_commands': sum(c.get('exit_code') not in (None, 0) for c in commands),
        'provider_error_events': sum(event.get('type') == 'error' for event in events),
        'authoring_cli_invocations_including_nested_deliver': len(cli_invocations),
        'repair_rounds': max(0, len(attempts)-1) if attempts else None,
        'attempts': attempts, 'first_json': ('snapshots/' + first['sha256'] + '.json') if first else None,
        'first_submitted_json': attempts[0]['snapshot'] if attempts else None,
        'precheck_revisions_observed': max(0, len(precheck_hashes)-1) if first else None,
        'final_json': final['path'] if final else None, 'final_json_sha256': final['sha256'] if final else None,
        'html': html, 'delivery_receipts': [str(p) for p, _ in receipts],
        'delivery_receipt_integrity': receipt_integrity,
        'delivery_verified': any(r['status'] == 'current' and r['matches_final_json'] and r['matches_artifact'] for r in receipt_integrity),
        'relationship_directions': {d: sum(c.get('direction','forward') == d for c in final['data'].get('connections',[])) for d in ['forward','both','none']} if final else None,
        'label_arrow_count': sum(c.get('arrowPosition') == 'label' for c in final['data'].get('connections', [])) if final else None,
        'source_status': source_status, 'source_commit_after': source_commit_after, 'source_pin_matches': source_pin_matches,
        'changed_package_files': changed_package, 'added_package_files': added_package,
        'semantics': 'unverified', 'readability': 'unreviewed',
        'session_export': str(evidence / 'session.jsonl'),
        'capture_limits': 'Pre-entry snapshots prove attempted candidate history. Polling also captures unvalidated drafts; transient complete unsubmitted drafts between 50 ms polls are not guaranteed.'
    }
    (evidence / 'observations.json').write_text(json.dumps(row, indent=2) + '\n')
    summary.append(row)
(root / 'observations.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps([{key: r[key] for key in ['run_id','repair_rounds','tool_commands','failed_tool_commands','usage','relationship_directions']} for r in summary], indent=2))
