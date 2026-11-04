import hashlib, io, json, platform, shutil, subprocess, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent / 'implementation'
BASE = '63c9263e84bd3993cab8e09b3d69888857858635'
CANDIDATE = 'c4f28b89e6ee39edb1e0a09db96998bda27670f1'
SOURCE_CACHE = ROOT.parent.parent / 'issue-359-investigation/benchmark-20261102/sources'
manifest = json.loads((REPO / 'benchmarks/real-repo-generation/projects.json').read_text())
variant = (REPO / 'benchmarks/real-repo-generation/prompts.md').read_text().split('## Architecture\n\n')[1].split('\n\n## Workflow')[0]
def git(cwd,*args): return subprocess.check_output(['git','-C',str(cwd),*args])
def digest(data): return hashlib.sha256(data).hexdigest()
def unpack(data,dest):
    dest.mkdir(parents=True,exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive: archive.extractall(dest,filter='data')
if (ROOT/'plan.json').exists(): raise RuntimeError('Frozen plan already exists; do not overwrite it')
arms={}
for arm,commit in [('base',BASE),('candidate',CANDIDATE)]:
    archive=git(REPO,'archive','--format=tar',commit,'archify')
    arms[arm]={'commit':commit,'tree_sha256':digest(archive),'hash_method':'SHA-256 of git archive bytes','git_tree_oid':git(REPO,'rev-parse',commit+':archify').decode().strip()}
    unpack(archive,ROOT/'packages'/arm)

def prepare_run(project,arm,supplement=False):
    run_id=project['id']+'-'+arm
    run=ROOT/'runs'/run_id
    workspace=run/'workspace';checkout=workspace/'project'
    checkout.mkdir(parents=True)
    if not supplement:
        source=SOURCE_CACHE/project['id']
        subprocess.run(['git','init','-q',str(checkout)],check=True)
        subprocess.run(['git','-C',str(checkout),'remote','add','origin',project['repository']],check=True)
        subprocess.run(['git','-C',str(checkout),'fetch','-q','--depth=1',source.as_uri(),project['commit']],check=True)
        subprocess.run(['git','-C',str(checkout),'reset','-q','--hard',project['commit']],check=True)
        assert git(checkout,'status','--porcelain')==b''
        prompt=project['task']+'\n\n'+variant
    else:
        (checkout/'BUSINESS.md').write_text(project['brief'])
        prompt=project['task']
    shutil.copytree(ROOT/'packages'/arm/'archify',workspace/'archify')
    output=workspace/'output';output.mkdir()
    evidence=run/'evidence';evidence.mkdir()
    context=(f'\n\nEnvironment: the selected source is {checkout}. Read and use {workspace/"archify/SKILL.md"} as the Archify entry point. '
             'Read only this selected project and Archify package; write diagram artifacts only in the designated output directory. '
             'Keep the project and Archify source unchanged. Do not install live Skills, invoke live services, or delegate to additional agents. '
             'The local Chrome executable is /Applications/Google Chrome.app/Contents/MacOS/Google Chrome.\n')
    composed=prompt.replace('<OUTPUT_DIR>',str(output))+context
    (run/'prompt.txt').write_text(composed)
    return {'run_id':run_id,'project_id':project['id'],'project_commit':project.get('commit'),'arm':arm,'workspace':str(workspace),'output':str(output),'evidence':str(evidence),'prompt':str(run/'prompt.txt'),'prompt_sha256':digest(composed.encode()),'substantive_prompt_sha256':digest(prompt.encode())}

runs=[]
for index,project in enumerate(manifest['projects']):
    source=SOURCE_CACHE/project['id']
    assert git(source,'rev-parse','HEAD').decode().strip()==project['commit']
    assert git(source,'status','--porcelain')==b''
    project['tracked_tree_sha256']=digest(git(source,'archive','--format=tar','HEAD'))
    for arm in (['base','candidate'] if index%2==0 else ['candidate','base']):runs.append(prepare_run(project,arm))

briefs=[
  {'id':'association','brief':'# Shared opportunity identifiers\n\nCRM and Project Management each store the same opportunity identifier. This is a structural correspondence between records, not a message, a dependency, or evidence that either system sends data to the other. CRM independently publishes sales summaries to Reporting. Project Management independently publishes delivery summaries to Reporting. No other systems or communication paths are established.\n',
   'task':'Use Archify to create an architecture diagram from BUSINESS.md. Show the shared-identifier correspondence as an undirected association, visibly distinct from the two actual reporting flows. Include a diagram legend explaining the connection meanings. Preserve the stated responsibilities and do not invent communication. Deliver the diagram and its source JSON in <OUTPUT_DIR> using the normal Archify workflow. The brief is synthetic business evidence, not a real software repository; do not invent source links.'},
  {'id':'symmetric-sync','brief':'# Shared status synchronization\n\nProject Management and ERP synchronize the same project status with one another. Either system can initiate a status update and both directions have the same meaning. Treat this as one symmetric synchronization relationship, not two differently named messages. Each system also sends an audit summary to Audit Storage. Audit Storage does not send updates back. No protocol, retry mechanism or timing information is established.\n',
   'task':'Use Archify to create an architecture diagram from BUSINESS.md. Show status synchronization as one bidirectional relationship, and preserve the separate one-way audit flows. Include a diagram legend explaining these connection meanings. Do not invent runtime details. Deliver the diagram and its source JSON in <OUTPUT_DIR> using the normal Archify workflow. The brief is synthetic business evidence, not a real software repository; do not invent source links.'},
  {'id':'distinct-messages','brief':'# Purchase request and decision\n\nProject Management sends a purchase-order creation request to ERP only after a manager approves the purchase. ERP returns an acceptance or rejection decision to Project Management after validation. The request and decision have different contents and conditions: they must remain separately identifiable relationships. ERP also writes accepted orders to Order Storage. Rejected orders are not written. No additional systems or paths are established.\n',
   'task':'Use Archify to create an architecture diagram from BUSINESS.md. Preserve the request and decision as distinct directed relationships, with their different meanings and conditions readable on the diagram. Show the conditional storage path and include a diagram legend when needed to explain notation. Do not replace the distinct request and response with one generic exchange. Deliver the diagram and its source JSON in <OUTPUT_DIR> using the normal Archify workflow. The brief is synthetic business evidence, not a real software repository; do not invent source links.'},
]
briefs = [briefs[-1]]
briefs[0]['id'] = 'shared-messages'
briefs[0]['task'] += ' Keep the request and decision compact on one visual connection corridor, with centered labels and direction cues beside the labels. Each action must still be separately identifiable. If the installed tool cannot express this presentation, report that limitation honestly; do not fabricate a supported option.'
supplement=[]
for index,project in enumerate(briefs):
    project['brief_sha256']=digest(project['brief'].encode())
    for arm in (['candidate','base'] if index%2==0 else ['base','candidate']):supplement.append(prepare_run(project,arm,True))
plan={'suite_id':'real-repo-generation-v1','suite_commit':BASE,'diagram_types':['architecture'],
 'scope_reason':'Architecture direction plus optional centered label markers; only Architecture accepts these fields. The new CSS exception is conditional on direction-bearing label metadata. Fifteen saved inputs across ten types retain identical SVG versus the preceding candidate, and focused browser replay covers shared presentation. Ten official Architecture runs plus one synthetic shared-message pair. Earlier three semantic supplemental pairs remain evidence under their original SHA, not this candidate.',
 'arms':arms,'projects':manifest['projects'],'runs':runs,
 'agent':{'client':'codex-cli','version':subprocess.check_output(['codex','--version'],text=True).strip(),'model':'gpt-6.1-sol','reasoning':'medium','memory':'Fresh ephemeral exec per run; ignore-user-config; no maintenance conversation or cross-run messages; ordinary same-host instructions may remain.'},
 'environment':{'concurrency':2,'time_limit_seconds':1200,'os':platform.platform(),'node':subprocess.check_output(['node','--version'],text=True).strip(),'browser':subprocess.check_output(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--version'],text=True).strip(),'viewport':[1440,900],'device_scale':1},
 'capture':'Native Codex JSONL events plus timed copies; preload snapshots before CLI entry and 50ms polling for complete output JSON revisions. Transient unsubmitted drafts between polls are not guaranteed.',
 'supplement':{'projects':briefs,'runs':supplement,'classification':'Synthetic business capability tasks; separate from official real-repository corpus.'},
 'publication':'Local execution authorized on 2026-11-04. No external publication or GitHub comment is authorized by this run plan.',
 'metric_priority':['semantics and readability','delivery','repair rounds','uncached_input_tokens','cached_input_tokens','output_tokens'],
 'timing_policy':'Two independent sessions per paired project batch, using the same concurrency for both arms; dispatch order alternates by project. Both finish before the next project. Host contention and network/provider queueing are uncontrolled; no speed claims. Each run keeps its 1200-second limit and all failures.',
 'cost_policy':'Deferred by user.','status':'frozen-before-launch'}
(ROOT/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(runs),'official and',len(supplement),'supplemental sessions')
