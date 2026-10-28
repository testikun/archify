#!/usr/bin/env python3
"""Generate synthetic inputs from one fact sheet, without changing product code."""
import copy, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
facts = json.loads((ROOT / 'facts.json').read_text())
out = ROOT / 'inputs'
out.mkdir(exist_ok=True)
def save(name, value):
    (out / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def prefix(c):
    return str(c['stage']) + ('.' + c['member'] if 'member' in c else '')
def label(c):
    return prefix(c) + ' · ' + ('' if 'parallelGroup' in c else 'await ') + c['text'] + (' [parallel P]' if 'parallelGroup' in c else '')

for case, stages in facts['scenarios'].items():
    calls = [c for c in facts['calls'] if c['stage'] in stages]
    ids = {'page'} | {c['to'] for c in calls}
    comps = [c for c in facts['components'] if c['id'] in ids]
    common = {'schema_version':1, 'meta': {
        'title': 'PDF ingest — ' + case + ' (synthetic)',
        'subtitle': 'Author-declared calls; no runtime measurements.',
        'output':case + '.html', 'quality_profile':'standard', 'visual_preset':'classic'
    }, 'cards':[{'dot':'cyan', 'title':'Author facts', 'items':[
        'Synthetic successful path, not captured execution.',
        'Each numbered stage completes before the next is invoked.',
        'Parallel P starts after stage 4; A and B have no declared relative or completion order.' if case=='parallel' else 'The page handler calls classify, extract, then record storage.',
        'Component ownership: Application / Inference provider / Storage services.'
    ]}]}
    arch = copy.deepcopy(common)
    arch['diagram_type'] = 'architecture'
    arch['components'] = []
    for i,c in enumerate(comps):
        arch['components'].append({
            'id':c['id'], 'type':c['type'], 'label':c['label'],
            'sublabel':facts['boundaries'][c['boundary']],
            'pos':[70, 115+55*(len(calls)-1)] if i==0 else [610, 115+(i-1)*110],
            'size':[190,72]
        })
    arch['boundaries'] = [{'kind':'region','label':name,'pad':16,'wraps':[c['id'] for c in comps if c['boundary']==b]}
                          for b,name in facts['boundaries'].items()]
    arch['connections'] = [{'id':c['id'],'from':c['from'],'to':c['to'],
                            'label':label(c),'fromSide':'right','toSide':'left'} for c in calls]
    save(case+'-architecture',arch)
    seq = copy.deepcopy(common)
    seq['diagram_type'] = 'sequence'
    seq['meta']['viewBox'] = [max(800,len(comps)*180), 660 if case=='parallel' else 480]
    seq['participants'] = [{'id':c['id'],'type':c['type'],'label':c['label'],
                            'sublabel':facts['boundaries'][c['boundary']]} for c in comps]
    seq['messages'] = [{'id':c['id'],'from':c['from'],'to':c['to'],'label':label(c),'y':185+i*64} for i,c in enumerate(calls)]
    seq['segments'] = ([{'from':425,'to':540,'label':'P: one parallel batch; A/B rows are not order'}] if case=='parallel' else [])
    save(case+'-sequence',seq)

    if case=='parallel':
        reverse=copy.deepcopy(arch); reverse['connections'].reverse(); save('control-architecture-reversed-array',reverse)
        no_numbers=copy.deepcopy(arch)
        for e,c in zip(no_numbers['connections'],calls):e['label']=('' if 'parallelGroup' in c else 'await ')+c['text']+(' [parallel P]' if 'parallelGroup' in c else '')
        save('ablation-architecture-no-numbers',no_numbers)
        plain=copy.deepcopy(seq);plain['segments']=[]
        for e,c in zip(plain['messages'],calls):e['label']=prefix(c)+' · '+('' if 'parallelGroup' in c else 'await ')+c['text']
        save('ablation-sequence-no-parallel-prose',plain)
        same_y=copy.deepcopy(seq);same_y['messages'][-1]['y']=same_y['messages'][-2]['y']
        save('probe-sequence-same-y',same_y)
        no_cards=copy.deepcopy(arch);no_cards.pop('cards');save('ablation-architecture-no-cards',no_cards)
        legacy=copy.deepcopy(arch);legacy['meta']['views']=[{'id':'calls','label':'Calls','focus':['page','classify','extract','record']}]
        save('probe-retired-views',legacy)
        proposed=copy.deepcopy(arch)
        for e,c in zip(proposed['connections'],calls):e['order']=prefix(c)
        save('probe-unapproved-order',proposed)

        brief={'version':2,'title':'PDF ingest — author-declared calls','intro':'Synthetic successful path. Stages complete before the next stage starts.',
               'outro':'The parallel batch has no declared A/B completion order. No runtime timing is asserted.',
               'scenes':[{'title':'Single caller, declared stages','points':[
                   {'anchor':'page','via':c['id'],'title':prefix(c)+' · '+c['text'],
                    'text':('The page handler starts this scenario by classifying the PDF.' if c['stage']==1 else 'The page handler makes this call after the preceding stage completes.'),'caption':label(c),'action':'trace'}
                   for c in calls if 'parallelGroup' not in c
               ] + [{'anchor':'page','via':['write-a','write-b'],'action':'parallel',
                      'title':'5 · Launch parallel P','text':'After upload completes, launch both writes in one batch. No relative completion order or exact simultaneous clock time is claimed.',
                      'caption':'P: write A and B together; neither is before the other.'}]}]}
        save('parallel-story-brief',brief)
print('Inputs:',len(list(out.glob('*.json'))))
