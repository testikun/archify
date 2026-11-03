import hashlib, io, json, os, shutil, subprocess, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent / 'implementation'
BASE = '63c9263e84bd3993cab8e09b3d69888857858635'
CANDIDATE = 'e7174173cbbd134418a08155c6e1e4a0c8f398cd'
manifest = json.loads((REPO / 'benchmarks/real-repo-generation/projects.json').read_text())
variant = (REPO / 'benchmarks/real-repo-generation/prompts.md').read_text().split('## Architecture\n\n')[1].split('\n\n## Workflow')[0]

def git(cwd, *args):
    return subprocess.check_output(['git', '-C', str(cwd), *args])

def unpack(data, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(destination, filter='data')

arms = {}
for arm, commit in [('base', BASE), ('candidate', CANDIDATE)]:
    archive = git(REPO, 'archive', '--format=tar', commit, 'archify')
    arms[arm] = {'commit': commit, 'tree_sha256': hashlib.sha256(archive).hexdigest(),
                 'hash_method': 'SHA-256 of git archive bytes',
                 'git_tree_oid': git(REPO, 'rev-parse', commit + ':archify').decode().strip()}
    unpack(archive, ROOT / 'packages' / arm)

runs = []
for index, project in enumerate(manifest['projects']):
    source = ROOT.parent / 'benchmark-20261102/sources' / project['id']
    assert git(source, 'rev-parse', 'HEAD').decode().strip() == project['commit']
    assert git(source, 'status', '--porcelain') == b''
    archive = git(source, 'archive', '--format=tar', 'HEAD')
    project['tracked_tree_sha256'] = hashlib.sha256(archive).hexdigest()
    for arm in (['base', 'candidate'] if index % 2 == 0 else ['candidate', 'base']):
        run_id = project['id'] + '-' + arm
        run = ROOT / 'runs' / run_id
        workspace = run / 'workspace'
        checkout = workspace / 'project'
        if (run / 'evidence/execution.json').exists():
            raise RuntimeError('Do not replace an executed workspace')
        if workspace.exists():
            shutil.rmtree(workspace)
        checkout.mkdir(parents=True)
        # Preserve repository identity for Archify source verification, while
        # keeping other project revisions and the other arm out of this workspace.
        subprocess.run(['git', 'init', '-q', str(checkout)], check=True)
        subprocess.run(['git', '-C', str(checkout), 'remote', 'add', 'origin', project['repository']], check=True)
        subprocess.run(['git', '-C', str(checkout), 'fetch', '-q', '--depth=1', source.as_uri(), project['commit']], check=True)
        subprocess.run(['git', '-C', str(checkout), 'reset', '-q', '--hard', project['commit']], check=True)
        assert git(checkout, 'status', '--porcelain') == b''
        shutil.copytree(ROOT / 'packages' / arm / 'archify', workspace / 'archify')
        output = workspace / 'output'
        output.mkdir()
        evidence = run / 'evidence'
        evidence.mkdir(exist_ok=True)
        prompt = project['task'] + '\n\n' + variant.replace('<OUTPUT_DIR>', str(output))
        context = (f'\n\nEnvironment: the pinned source checkout is {checkout}. '
                   f'Read and use {workspace / "archify/SKILL.md"} as the Archify entry point. '
                   'Read only this selected project and Archify package; write diagram artifacts only in the designated output directory. '
                   'Keep the project and Archify source unchanged. Do not install live Skills, invoke live services, or delegate to additional agents. '
                   'The local Chrome executable is /Applications/Google Chrome.app/Contents/MacOS/Google Chrome.\n')
        (run / 'prompt.txt').write_text(prompt + context)
        runs.append({'run_id': run_id, 'project_id': project['id'], 'project_commit': project['commit'],
                     'arm': arm, 'workspace': str(workspace), 'output': str(output),
                     'evidence': str(evidence), 'prompt': str(run / 'prompt.txt'),
                     'prompt_sha256': hashlib.sha256((prompt + context).encode()).hexdigest(),
                     'substantive_prompt_sha256': hashlib.sha256((project['task'] + '\n\n' + variant).encode()).hexdigest()})

plan = {
    'suite_id': 'real-repo-generation-v1', 'suite_commit': BASE, 'diagram_types': ['architecture'],
    'scope_reason': 'Only Architecture accepts or resolves the new coordinates. Architecture-specific documentation is in the shared authoring reference; no other diagram semantics, defaults or shared router changed. Core smoke covers unchanged types.',
    'arms': arms, 'projects': manifest['projects'], 'runs': runs,
    'agent': {'client': 'codex-cli', 'version': subprocess.check_output(['codex','--version'],text=True).strip(), 'model': 'gpt-6.1-sol', 'reasoning': 'medium',
              'memory': 'Fresh exec per run; ignore-user-config; no maintenance conversation or cross-run messages.'},
    'environment': {'concurrency': 1, 'time_limit_seconds': 1200, 'os': 'macOS arm64', 'node': subprocess.check_output(['node','--version'],text=True).strip(),
                    'browser': 'Chrome 156.0.8078.74', 'viewport': [1440,900], 'device_scale': 1},
    'capture': 'Native Codex JSONL events plus timestamped event copies; NODE_OPTIONS preload snapshots each complete JSON before CLI entry. An external poller also captures complete output JSON revisions. Unvalidated writes between poll intervals may be unavailable; never reconstruct first draft from final output.',
    'supplement': {'runs': [], 'reused_evidence': '../latest-dev-20261102/issue359-scenario/REPORT.md'},
    'publication': 'User authorized the PR and full protocol benchmark on 2026-11-03. Publish relevant sanitized evidence separately from product source.',
    'status': 'full-five-project-architecture-comparison',
    'metric_priority': ['semantic correctness and readability', 'delivery', 'repair rounds', 'uncached_input_tokens', 'cached_input_tokens', 'output_tokens'],
    'timing_policy': 'Sequential sessions. Wall time retained descriptively; local connection instability prevents speed claims.',
    'cost_policy': 'Cost accounting deferred by user.',
    'prior_runs': 'Earlier exploratory runs remain separate; all ten formal sessions below are fresh.',
}
(ROOT / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
print('Prepared', len(runs), 'independent generation workspaces')
