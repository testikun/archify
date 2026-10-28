#!/usr/bin/env python3
"""Check preserved author facts and summarize the actual browser/export receipts."""
import hashlib,json,pathlib,struct,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
facts=json.loads((ROOT/'facts.json').read_text())
observations=json.loads((ROOT/'receipts/browser.json').read_text())
by_name={x['name']:x for x in observations if 'name' in x}
NS='{http://www.w3.org/2000/svg}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def svg(name):return ET.parse(ROOT/'exports'/f'{name}.svg').getroot()
def graph(tree):
    nodes={e.get('data-node-id'):e.get('data-node-label') for e in tree.iter() if e.get('data-node-id')}
    edges={e.get('data-edge-id'):[e.get('data-edge-from'),e.get('data-edge-to'),e.get('data-edge-label')] for e in tree.iter() if e.get('data-edge-id') and e.get('data-edge-from')}
    return {'nodes':nodes,'edges':edges}
def without_style(tree):
    for parent in tree.iter():
        for child in list(parent):
            if child.tag==NS+'style':parent.remove(child)
    return ET.tostring(tree)
result={'sourceSha':observations[0]['sourceSha'],'environment':observations[0],'cases':[],'exports':[]}
for case in ['serial','parallel']:
    calls=[x for x in facts['calls'] if x['stage'] in facts['scenarios'][case]]
    ids={x['id'] for x in calls}
    outputs=[]
    for kind in ['architecture','sequence']:
        name=f'{case}-{kind}';s=svg(name);g=graph(s);outputs.append(g)
        assert set(g['edges'])==ids
        for c in calls:assert g['edges'][c['id']][:2]==[c['from'],c['to']]
        b=by_name[name+'-default']; labels={x[2] for x in g['edges'].values()}
        fonts=[x['screenSize'] for x in b['texts'] if x['text'] in labels]
        phases={phase:{'mode':by_name[name+'-'+phase]['motion'],'animations':len(by_name[name+'-'+phase]['animations'])} for phase in ['default','live','still','reduced','reduced-after-motion-click']}
        assert all(v['mode']=='still' and v['animations']==0 for k,v in phases.items() if k!='live')
        assert all(not x.get('errors') for x in observations if x.get('name','').startswith(name) and 'errors' in x)
        node_map={x['id']:x for x in b['nodes']}
        for c in facts['components']:
            if c['id'] in node_map:assert node_map[c['id']]['sublabel']==facts['boundaries'][c['boundary']]
        focus=by_name[name+'-focus-700ms'];focused={e['id'] for e in focus['edges'] if e['focus']}
        assert focused==ids
        assert (ROOT/'exports'/f'{name}.svg').read_bytes()==(ROOT/'exports'/f'{name}-focused.svg').read_bytes()
        png=(ROOT/'exports'/f'{name}.png').read_bytes();w,h=struct.unpack('>II',png[16:24])
        result['cases'].append({'name':name,'nodeCount':len(g['nodes']),'edgeCount':len(g['edges']),'viewBox':b['viewBox'],'screenEdgeFontPx':fonts,'svgRect':b['svgRect'],'phases':phases,'focusMatches':sorted(focused),'focusedExportByteIdentical':True,'pngSize':[w,h]})
    assert outputs[0]==outputs[1],case+' renderer facts differ'
for p in sorted((ROOT/'exports').glob('*.svg')):
    s=ET.parse(p).getroot();assert not any(e.tag in {NS+'script',NS+'animate',NS+'animateMotion'} for e in s.iter())
    leaked=[e.tag for e in s.iter() if any(k in e.attrib for k in ['data-focus-active','data-focus-match','data-story-active','data-ambient-flow-overlay','data-intent-trace-overlay'])]
    assert not leaked,p.name
    result['exports'].append({'file':str(p.relative_to(ROOT)),'sha256':sha(p),'nodes':len(graph(s)['nodes']),'edges':len(graph(s)['edges']),'runtimeElementLeaks':leaked})
base=ROOT/'exports/parallel-architecture.svg'
result['ablations']={name:base.read_bytes()==(ROOT/'exports'/f'{name}.svg').read_bytes() for name in ['ablation-architecture-no-cards','probe-retired-views']}
result['story']=[]
for mode in ['normal','reduced']:
    plan=by_name[f'story-{mode}-plan'];a=[x for x in plan['actions'] if x['shot']==1]
    times={x['edge']:x['start'] for x in a}
    assert times['classify-call']<times['extract-call']<times['save-record']<times['upload-file']<times['write-a']==times['write-b']
    b=by_name[f'story-{mode}-write-a'];p=ROOT/'exports'/f'story-{mode}.svg'
    assert graph(svg('story-'+mode))==graph(svg('parallel-architecture'))
    assert without_style(svg('story-'+mode))==without_style(svg('parallel-architecture'))
    result['story'].append({'mode':mode,'displayStartTimesSeconds':times,'duration':plan['duration'],'flowElements':len(b['flows']),'hiddenFlowElements':sum(f['display']=='none' for f in b['flows']),'nativeAnimationCount':sum(f['animations'] for f in b['flows']),'startedPlaying':by_name[f'story-{mode}-playing']['state']['playing'],'canonicalExportBytesEqual':base.read_bytes()==p.read_bytes(),'canonicalExportDifferenceIsStyleOnly':True})
result['cli']=json.loads((ROOT/'receipts/cli/commands.json').read_text())
result['probes']=json.loads((ROOT/'receipts/browser-probes.json').read_text())
(ROOT/'receipts/summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Author facts preserved across 4 main outputs; native focus exports identical; Still/reduced checks passed; Story timings and export structure checked.')
