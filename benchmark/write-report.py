"""Render the protocol report from observed evidence and explicit author review."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
def read(name, default):
    p = root / name
    return json.loads(p.read_text()) if p.exists() else default

plan = read('plan.json', {})
observed = {r['run_id']: r for r in read('observations.json', [])}
reviews = read('reviews.json', {})
replays = {r['run_id']: r for r in read('replay/summary.json', [])}
runs = {r['run_id']: r for r in plan['runs']}
def link(label, file):
    return f'[{label}]({Path(file).relative_to(root)})' if file else 'unavailable'
def result(run_id):
    o = observed.get(run_id)
    if not o: return 'pending'
    r = reviews.get(run_id, {})
    delivery = 'timeout' if o['timeout'] else ('delivered' if o.get('delivery_verified') and o['execution_exit_code'] == 0 else 'failed / inspect record')
    return f"{r.get('semantics', 'unverified')} / {r.get('readability', 'unreviewed')} / {delivery}"
def first(run_id):
    value = replays.get(run_id, {}).get('first_draft_validation_exit')
    return 'unknown' if value is None else ('pass' if value == 0 else 'fail')
def value(run_id, field):
    return observed.get(run_id, {}).get(field, 'pending')

adoption = sum(o['relative_coordinates_in_final'] or 0 for o in observed.values())
lines = [
    '# Generation comparison: PR #1184', '',
    f"Status: **{len(observed)}/10 sessions completed**. Final semantic/visual reviews recorded: {len(reviews)}/10. This is an author-side maintenance Codex report, not independent human acceptance.", '',
    '## Decision summary', '',
    'All ten scheduled sessions delivered final artifacts with matching current receipts; none timed out or reported a provider-error event. Author-side review marks nine semantically correct and eight readable. These are separate observations, not an aggregate pass score. All ten frozen final JSON inputs pass on both code versions and produce identical layouts and canonical diagram SVG.', '',
    'Quality finding: the Hive base run passes CLI delivery but fails source/visual review. It promotes an uncalled browser HTTP helper to an active UI entry, and long boundary-title masks obscure the top return-route legs. Both defects remain when replaying that exact JSON on candidate; they are not a new renderer regression or evidence that relative coordinates improve fresh generation. The original artifact is retained unchanged. See the paired Hive review below.', '',
    'Candidate-run quality gap: Squad candidate has correct source semantics but its database boundary title masks two incoming route legs. Automated delivery passes; author-side readability is marked issues. The same frozen JSON has identical geometry/SVG on base, so this is an existing presentation/authoring problem rather than a demonstrated PR regression. It remains visible in the report and needs an explicit quality decision; this benchmark is not an all-pass claim.', '',
    'Retained natural validation failure: MCO candidate first places a filesystem node inside an unrelated process boundary, then repairs it after the CLI diagnostic. [Original failure event](runs/mco-candidate/evidence/session.jsonl#L46) and [unchanged failed JSON on base](replay/mco-candidate/first-draft.base.validate.json) remain available. The same pre-existing boundary rule rejects it on both versions; later success does not erase this first attempt.', '',
    'SkillRoster base also retains natural failures: abbreviated endpoint sides fail schema validation, then an over-wide diagram fails projected desktop readability. Two subsequent browser attempts fail because the participant wraps Chrome in a restrictive OS sandbox; successful reruns do not replace those records. [First failure](runs/skillroster-base/evidence/session.jsonl#L48) · [readability failure](runs/skillroster-base/evidence/session.jsonl#L50).', '',
    'The proposed capability preserves required authored corridors when nodes move by resolving endpoint-relative waypoint axes. This real-repository matrix tests fresh source-to-diagram authoring and compatibility. The separate synthetic edit reproduction demonstrates the intended mechanism after bindings are prepared; it does not establish natural adoption or free migration.', '',
    f'Observed relative-coordinate objects in completed final diagrams: **{adoption}**. When the new mechanism is not used, differences in revision count, chosen layout or tokens must not be attributed to it. No speed or stable efficiency claim is made from one pair per project.', '',
    'The earlier exploratory two-project runs are retained separately and are not counted in these ten fresh sessions. The feature remains a partial response to #359; bands layout and automatic migration are outside scope.', '',
    '## Frozen plan', '',
    f"- Base: `{plan['arms']['base']['commit']}`; candidate: `{plan['arms']['candidate']['commit']}`.",
    '- The candidate adds only a regenerated distribution ZIP to implementation commit `41076efb`. Earlier focused/core/browser checks are reused at that original SHA; current-head CI is recorded in [ci.json](ci.json). The original stale-ZIP CI failure is retained in PR history.',
    '- Scope: Architecture on OpenPI, Hive, MCO, Squad and SkillRoster, once per arm. The schema, resolver and new authoring section apply only to Architecture; the shared router and other diagram types are unchanged.',
    '- This is the repository\'s own `real-repo-generation-v1` corpus, not five contributor-selected substitutes. [Protocol audit](protocol-audit.json) verifies every pinned project entry and exact task + Architecture prompt text, both-arm prompt equivalence after path normalization, and prompt hashes. The protocol files are unchanged between base and candidate. The local runner only launches sessions and records evidence; the repository explicitly supplies no Agent launcher.',
    '- Codex CLI 0.144.0; `gpt-6.1-sol`, reasoning `medium`; fresh exec sessions with user config disabled and no maintenance history. One active generation session at a time; alternate arm order between projects. 20 minutes per session; no extra subagents.',
    '- macOS arm64; Node 20.20.2; Chrome 156.0.8078.74; screenshots light/Classic/Still, zoom 100%, 1440×900 CSS pixels, device scale 1, both initial viewport and full page. Each browser capture uses a fresh profile.',
    '- [Plan](plan.json) contains full project pins, clean-source hashes, Archify archive hashes/Git tree identities, exact prompt paths and hashes. Preparation is outside generation time. Source/package mutation checks are recorded per run.',
    '- [recorder.cjs](recorder.cjs) snapshots each complete input before CLI entry; [run.py](run.py) also polls complete JSON revisions every 50ms and records native Codex JSONL plus received timestamps. Transient complete unsubmitted drafts between polls may be missed. Earliest observed draft and first submitted draft are distinct.', '',
    '## Results', '',
    '| Project / Architecture / repetition 1 | Base: semantics / readability / delivery | Candidate: semantics / readability / delivery | First captured draft CLI, base → candidate | Post-check revisions, base → candidate |',
    '| --- | --- | --- | --- | --- |',
]
for p in plan['projects']:
    a, b = p['id'] + '-base', p['id'] + '-candidate'
    lines.append(f"| {p['name']} | {result(a)} | {result(b)} | {first(a)} → {first(b)} | {value(a, 'repair_rounds')} → {value(b, 'repair_rounds')} |")
lines += ['', 'CLI first-draft outcomes above do not imply first-draft semantic/visual acceptance. Revision counts include voluntary revisions; unchanged repeated checks are not new rounds. Pre-check revisions and reasons are detailed below and in [observations.json](observations.json).', '',
          '| Session | Uncached input | Cached input | Output tokens | Tool commands / failures | Pre-check revisions observed |',
          '| --- | ---: | ---: | ---: | ---: | ---: |']
for run_id in runs:
    o = observed.get(run_id)
    if not o: lines.append(f'| {run_id} | pending | pending | pending | pending | pending |'); continue
    u = o['usage'] or {}
    lines.append(f"| {run_id} | {u.get('uncached_input_tokens', 'unknown')} | {u.get('cached_input_tokens', 'unknown')} | {u.get('output_tokens', 'unknown')} | {o['tool_commands']} / {o['failed_tool_commands']} | {o['precheck_revisions_observed']} |")
lines += ['', 'Input columns are disjoint; their sum is total input. Reasoning tokens are already included in output. Usage comes from native turn-completed events. Costs are unknown/deferred by the user.', '',
          '| Session | Wall seconds (descriptive only) | Seconds to first captured JSON |',
          '| --- | ---: | ---: |']
for run_id in runs:
    o = observed.get(run_id, {})
    def seconds(field):
        v = o.get(field)
        return f'{v:.1f}' if isinstance(v, (int, float)) else 'unknown'
    lines.append(f"| {run_id} | {seconds('wall_seconds_descriptive_only')} | {seconds('time_to_first_json_seconds_descriptive_only')} |")
lines += ['', 'These times are descriptive records, not speed comparisons. Local connection instability and unobservable provider queues prevent meaningful speed claims. CLI runtime and queue/wait time are null in observations because native events do not isolate them; setup is outside the generation clock.', '', '## Visual and source comparison', '']
for project in plan['projects']:
    lines += [f"### {project['name']}", '', f"Pinned source: `{project['commit']}`.", '', '| Base screenshot | Candidate screenshot |', '| --- | --- |']
    ids = [project['id'] + '-' + arm for arm in ['base', 'candidate']]
    lines.append('| ' + ' | '.join(f'![{i}](captures/{i}/fullpage.light.png)' if (root/f'captures/{i}/fullpage.light.png').exists() else 'pending' for i in ids) + ' |')
    lines.append('')
    for i in ids:
        o, run, review = observed.get(i), runs[i], reviews.get(i)
        lines.append(f'**{i}**')
        if not o: lines += ['', 'Pending.', '']; continue
        evidence = Path(run['evidence'])
        lines += ['', ' · '.join([link('prompt', run['prompt']), link('session', evidence/'session.jsonl'),
            link('first JSON', evidence/o['first_json']) if o['first_json'] else 'first JSON unavailable',
            link('first submitted', evidence/o['first_submitted_json']) if o['first_submitted_json'] else 'first submission unavailable',
            link('final JSON', o['final_json']), link('original HTML', o['html'][0]) if len(o['html']) == 1 else 'HTML missing/ambiguous',
            link('version/receipt index', evidence/'observations.json')]), '']
        replay = replays.get(i, {})
        lines.append(f"Same-input replay: base delivery exit {replay.get('base_deliver_exit', 'unknown')}, candidate {replay.get('candidate_deliver_exit', 'unknown')}; equal layouts: {replay.get('identical_layout', 'unknown')}; equal canonical SVG: {replay.get('identical_canonical_svg', 'unknown')}. Inputs preserved byte-for-byte. [Replay](replay/{i}/).")
        lines.append('')
        failed_events = []
        for number, text in enumerate((evidence/'session.jsonl').read_text().splitlines(), 1):
            event = json.loads(text)
            item = event.get('item', {})
            if event.get('type') == 'item.completed' and item.get('type') == 'command_execution' and item.get('exit_code') not in (0, None):
                failed_events.append(f"[{item['id']}, exit {item['exit_code']}](runs/{i}/evidence/session.jsonl#L{number})")
        lines.append('Failed command records: ' + (', '.join(failed_events) if failed_events else 'none') + '.')
        lines.append('')
        if review:
            lines += ['Reviewer: maintenance Codex, author-side, separately inspecting the participant output.']
            lines += ['- ' + finding for finding in review['findings']]
            for fact in review['source_checks']:
                url = project['repository'] + '/blob/' + project['commit'] + '/' + fact['path'] + '#L' + str(fact['line'])
                lines.append(f"- Source check: {fact['fact']} [{fact['path']}:{fact['line']}]({url})")
        else: lines.append('Semantic and visual review pending; automated delivery alone is not acceptance.')
        lines.append('')
lines += ['## Audit and cost', '',
    '- [Evidence integrity audit](evidence-integrity.json) checks all ten completed records, original snapshot hashes, current receipt/artifact bindings, source/package immutability and report links. Semantic/readability judgments live in [reviews.json](reviews.json); the automated observations deliberately retain unverified placeholders rather than pretending to score those judgments.',
    '- [Public evidence branch](https://github.com/testikun/archify/tree/codex/pr-1184-evidence) is retained through review and the resulting release cycle. Its manifest identifies original and redacted file hashes. Host paths are replaced consistently, credential-shaped strings are removed if encountered, and no private maintenance conversation/auth files/source checkout is published. Hash changes due to redaction are explicit; original local receipts remain tied to original artifacts.',
    '- Native session events include ordered messages and tool commands/results. Tool failures, first captured drafts, submitted revisions and all scheduled outcomes remain inspectable. Captured outputs may include normal client truncation, which is not filled in retrospectively. Perceptual reviews and source checks are separate from automated validation/browser receipts.',
    '- Required CI and scope classification remain authoritative; passing this report does not authorize merging. Contributor personal review confirmation and maintainer scope acceptance remain separate.',
    '- Cost accounting is deferred. Human maintainer review time is not measured. Evidence assembly is performed by the maintenance Agent and overlaps sequential model runs, so no isolated assembly-time figure is claimed.',
    '- Remaining gaps: the original private #359 JSON is unavailable; prepared bindings have upfront authoring cost; one run per arm cannot establish stable token/repair improvements; fresh generation may not exercise the new API.', '']
(root/'REPORT.md').write_text('\n'.join(lines))
print('Wrote report for', len(observed), 'completed sessions and', len(reviews), 'reviews')
