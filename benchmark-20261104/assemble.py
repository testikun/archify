"""Assemble evidence links and templates without inventing reviewer outcomes."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent
plan = json.loads((root/'plan.json').read_text())
observations = {r['run_id']:r for r in json.loads((root/'observations.json').read_text())}
def load(name, fallback):
    return json.loads((root/name).read_text()) if (root/name).exists() else fallback
reviews = load('reviews.json', {})
replays = {r['run_id']:r for r in load('replay/summary.json', [])}
captures = {r['run_id']:r for r in load('captures/metrics.json', [])}
template = json.loads((root.parent/'implementation/benchmarks/real-repo-generation/run-template.json').read_text())
def relative(value):
    return str(Path(value).relative_to(root)) if value else None
def link(label, value):
    return f'[{label}]({relative(value)})' if value else f'{label}: unavailable'
def delivery(row):
    if row.get('timeout'): return 'timeout (partial artifacts retained)'
    if row.get('execution_exit_code') != 0: return 'failed / provider error: inspect session'
    if row.get('delivery_verified'): return reviews.get(row['run_id'],{}).get('delivery_note','delivered')
    return 'unverified delivery'
for run in plan['runs']+plan['supplement']['runs']:
    rid=run['run_id'];row=observations.get(rid)
    if not row:continue
    review=reviews.get(rid,{});replay=replays.get(rid,{})
    meta=json.loads((Path(run['evidence'])/'execution.json').read_text())
    events=[json.loads(l) for l in (Path(run['evidence'])/'session.jsonl').read_text().splitlines()]
    out=json.loads(json.dumps(template));out['template']=False
    out.update(suite_id=plan['suite_id'] if run['project_commit'] else 'synthetic-business-supplement',suite_commit=plan['suite_commit'],run_id=rid,project_id=run['project_id'],project_commit=run['project_commit'],diagram_type='architecture',arm=run['arm'])
    out['archify']={'commit':plan['arms'][run['arm']]['commit'],'package_or_tree_sha256':plan['arms'][run['arm']]['tree_sha256'],'preparation_log':'../../../preparation.log'}
    out['agent']={**plan['agent'],'tools':['exec_command','apply_patch','view_image and ordinary Codex client tools; actual calls preserved in session'],'memory_policy':plan['agent']['memory']}
    out['environment']=plan['environment']
    out['prompt']={'path':'../prompt.txt','sha256':run['prompt_sha256'],'substantive_sha256':run['substantive_prompt_sha256']}
    out['session'].update(id=next((e.get('thread_id') for e in events if e.get('type')=='thread.started'),None),export='session.jsonl',capture_method=plan['capture'],completeness='Native JSONL stream through process exit; tool output truncation, if any, remains visible; private reasoning is not requested.')
    out['artifacts'].update(first_json=row['first_json'],attempted_json_versions=row['attempts'],final_json=row['final_json'],html=row['html'],receipts=row['delivery_receipts'],screenshots=[str(p.relative_to(root)) for p in (root/'captures'/rid).glob('*.png')])
    out['observations'].update(delivery=delivery(row),semantics=review.get('semantics','unverified'),readability=review.get('readability','unreviewed'),reviewer='Maintenance Codex' if review else None,review_origin=review.get('review_origin'),findings=review.get('findings',[]),first_draft_check=replay.get('first_draft_validation_exit'),repair_rounds=row['repair_rounds'],tool_calls=row['tool_commands'],usage=row['usage'])
    out['observations'].update(first_draft_semantics=review.get('first_draft_semantics','unverified'),first_draft_visual=review.get('first_draft_visual','unreviewed'),repair_rounds_by_reason=review.get('repair_rounds_by_reason'),tool_count_definition='Completed shell command-execution items; compound shell subcommands are not counted independently. Native sessions retain their output and failures.')
    out['observations']['capability_result']=review.get('capability_result')
    out['timing'].update(dispatched_at=meta['started_at'],finished_at=meta['finished_at'],wall_seconds=row['wall_seconds_descriptive_only'])
    out['timing'].update(time_to_first_json_seconds=row['time_to_first_json_seconds_descriptive_only'],time_to_first_cli_seconds=row['time_to_first_cli_seconds_descriptive_only'])
    out['unavailable']=[row['unavailable_timing_reason'],row['cost_reason'],row['capture_limits'],'No human maintainer or external independent acceptance is claimed.']
    (Path(run['evidence'])/'run.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')

lines=['# #1139 generation benchmark evidence','',f'Completed generation sessions: **{sum(r["run_id"] in observations for r in plan["runs"])}/10 official**, **{sum(r["run_id"] in observations for r in plan["supplement"]["runs"])}/6 supplemental**. Review and replay status is shown per run; a completed session is not an accepted diagram.','',
'Actionable defects are retained separately in [ISSUES.md](ISSUES.md), including reproduction steps, screenshots, affected versions and attribution limits. No GitHub issue has been submitted by this run.','',
'## Frozen comparison','',f'- Base: `{plan["arms"]["base"]["commit"]}`; candidate: `{plan["arms"]["candidate"]["commit"]}`.',
'- Official scope: Architecture on all five pinned repositories; fresh base/candidate sessions. New direction metadata is Architecture-only. Existing saved inputs from ten diagram types and Viewer/Story focused checks cover unchanged shared callers.',
'- Supplemental scope: three synthetic business briefs × two versions. These exercise undirected association, symmetric synchronization, and distinct request/decision messages; they are not official real-project cases.',
'- Codex CLI 0.144.0, `gpt-6.1-sol`, `medium`, serial concurrency 1, 20-minute budget per session. Arm order alternates. No extra agent delegation.',
'- [Frozen plan](plan.json), [setup](preparation.log), [official scheduler](official-run.log), [supplement scheduler](supplement-run.log). Package hashes, project pins, prompt hashes and environment are in the plan.',
'- Credentials are supplied through the existing local gateway environment and are not included in evidence. Sessions are fresh/ephemeral and ignore user configuration; ordinary same-host instructions may remain. Source isolation uses task restrictions plus post-run integrity checks, not an OS read-only sandbox.',
'- The client requests `gpt-6.1-sol` with medium reasoning in both arms. stderr retains client-side model-cache/model-metadata fallback warnings, API-key remote-plugin-catalog warnings and local plugin/state-database warnings. These are environment limitations, not Archify diagnostics; successful sessions do not independently establish the gateway backend identity. No configuration was changed between arms to hide them.',
'- The recorder snapshots complete JSON before CLI entry and polls output every 50 ms. Unsubmitted transient versions between polls cannot be guaranteed. Native events, timed event copies, all submitted versions, errors and receipts are retained.',
'- Review below is author-side maintenance Codex inspection, independently checked against pinned source, not human maintainer acceptance. No overall score or speedup is inferred from one pair. Costs are deferred by user.','',
'## Per-run observations','',
'Input token totals include cached input. The table separates uncached input, cached input and output. Missing reasoning-token details stay unknown. Repair rounds count changed submitted JSON after the first check; voluntary revisions are included. Multiple commands on unchanged bytes are not extra rounds.','',
'| Run | Delivery | Semantics / readability | First JSON check | Revisions | Failed commands / total | Tokens: uncached / cached / output | Directions: forward / both / none |',
'| --- | --- | --- | --- | --- | --- | --- | --- |']
for run in plan['runs']+plan['supplement']['runs']:
    rid=run['run_id'];r=observations.get(rid);v=reviews.get(rid,{})
    if not r:lines.append(f'| {rid} | pending | unverified / unreviewed | — | — | — | — | — |');continue
    u=r['usage'] or {};d=r['relationship_directions'] or {};rp=replays.get(rid,{})
    first=rp.get('first_draft_validation_exit');first='pending' if first is None else ('pass' if first==0 else 'fail')
    lines.append(f'| [{rid}](runs/{rid}/evidence/run.json) | {delivery(r)} | {v.get("semantics","unverified")} / {v.get("readability","unreviewed")} | {first} | {r["repair_rounds"]} | {r["failed_tool_commands"]} / {r["tool_commands"]} | {u.get("uncached_input_tokens")} / {u.get("cached_input_tokens")} / {u.get("output_tokens")} | {d.get("forward")} / {d.get("both")} / {d.get("none")} |')
lines += ['','Command counts cover completed shell command-execution items; compound shell subcommands are not counted independently. Native sessions retain their full output, including failures hidden by a later successful command. Reasoning-token detail, descriptive timings and revision-reason grouping are in each run.json.','',
'## Visual and source comparisons','', 'Primary captures: native 1440 × 900 CSS pixels, device scale 1, zoom 100%, light / Classic / Still, captureBeyondViewport=false. Full-page images use an explicitly taller, settled viewport and may reflow; exact dimensions are in captures/metrics.json. Small viewport-filling diagrams additionally have their settled diagram/SVG box dimensions fixed only during the full-page capture to keep supporting cards within the image; this is marked frozenDiagramSize and never changes original HTML or the primary capture. Earlier captureBeyondViewport=true calls changed capture layout; images are preserved in captures-initial-clip and captures-beyond-viewport and excluded from acceptance. Incomplete expanding-viewport images are retained in captures-incomplete-tall. New direction artifacts also retain dark screenshots, native light/dark SVG/PNG exports and Route/Reach observations. Automated measurements are separate from visual judgment.']
for project in plan['projects']+plan['supplement']['projects']:
    pid=project['id'];lines += ['',f'### {pid}','', '| Base | Candidate |','| --- | --- |']
    images=[]
    for arm in ['base','candidate']:
        rid=pid+'-'+arm
        images.append(f'![{rid}](captures/{rid}/viewport.light.png)' if rid in captures else 'No captured image yet')
    lines.append('| '+' | '.join(images)+' |')
    for arm in ['base','candidate']:
        rid=pid+'-'+arm;r=observations.get(rid)
        if not r:continue
        run=next(x for x in plan['runs']+plan['supplement']['runs'] if x['run_id']==rid)
        evidence=Path(run['evidence']);v=reviews.get(rid,{})
        refs=[link('final JSON',r['final_json']),link('HTML',r['html'][0] if len(r['html'])==1 else None),link('session',r['session_export']),link('first JSON',str(evidence/r['first_json']) if r['first_json'] else None),f'[replay](replay/{rid}/)',f'[full page](captures/{rid}/fullpage.light.png)']
        lines += ['',f'**{arm}** — '+' · '.join(refs)]
        lines += ['- '+f for f in v.get('findings',['Semantic and visual review pending.'])]
        repo=project.get('repository');commit=project.get('commit')
        for check in v.get('source_checks',[]):
            lines.append(f'- Source: [{check["path"]}:{check["line"]}]({repo}/blob/{commit}/{check["path"]}#L{check["line"]}) — {check["fact"]}')
        rp=replays.get(rid)
        if rp:lines.append('- Cross-replay: '+json.dumps(rp,ensure_ascii=False))
lines += ['','## Audit limits and retention','',
'- Full scheduled failures, timeouts, revisions and provider errors remain in native sessions. No successful retry replaces a prior run. Source/package integrity and artifact receipt hashes are recorded in [observations.json](observations.json).',
'- First-draft validation is a replay of captured original bytes on its original arm. First-draft semantics and readability are unverified unless a review explicitly says otherwise. A final passing diagram is not first-draft success.',
'- Base rejection of new fields is reported as unsupported capability, not a regression or proof of fewer repairs. New metadata never gets removed for a passing replay.',
'- Timings are descriptive only: local gateway/network delay and provider queue time are not separated. Reasoning usage is unavailable when the client does not report it. No fabricated cost estimate is supplied.',
'- Active evidence-assembly labor was not separately timed while generation and inspection overlapped; it is unavailable. Maintainer review time is not applicable because no maintainer review has occurred. Capture-method investigation added avoidable collection work, whose unsuccessful outputs remain retained.',
'- Local evidence location: `'+str(root)+'`. No public upload, GitHub comment, or maintainer sign-off is implied. Archive digest and retention are in [bundle-notes.md](bundle-notes.md); the manifest records the literal configured-credential scan and its limits.']
if (root/'CONCLUSIONS.md').exists():
    lines[2:2]=[(root/'CONCLUSIONS.md').read_text().strip(),'']
(root/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('Assembled',len(observations),'finished runs;',len(reviews),'reviews;',len(captures),'captures;',len(replays),'cross-replays')
