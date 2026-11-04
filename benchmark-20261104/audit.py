"""Check retained evidence integrity, not diagram quality or model performance."""
import hashlib,json,re,struct,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(__file__).resolve().parent
read=lambda name:json.loads((root/name).read_text())
plan=read('plan.json');observations=read('observations.json');reviews=read('reviews.json')
captures={r['run_id']:r for r in read('captures/metrics.json')}
replays={r['run_id']:r for r in read('replay/summary.json')}
planned={r['run_id']:r for r in plan['runs']+plan['supplement']['runs']}
checks=[];features=[]
def check(label,condition):checks.append({'check':label,'pass':bool(condition)})
check('All 16 scheduled sessions retained',set(planned)=={r['run_id'] for r in observations})
for r in observations:
    rid=r['run_id'];run=planned[rid];ev=Path(run['evidence']);cap=captures.get(rid)
    check(rid+': source pin and package unchanged',r['source_pin_matches'] and not r['source_status'] and not r['changed_package_files'] and not r['added_package_files'])
    check(rid+': semantic and visual review recorded',rid in reviews)
    check(rid+': exact prompt retained',hashlib.sha256(Path(run['prompt']).read_bytes()).hexdigest()==run['prompt_sha256'])
    check(rid+': final JSON replayed unchanged',r['final_json_sha256']==replays.get(rid,{}).get('input_sha256'))
    for a in r['attempts']:
        check(rid+': submitted '+a['sha256'][:12],hashlib.sha256((ev/a['snapshot']).read_bytes()).hexdigest()==a['sha256'])
    check(rid+': first complete JSON retained',bool(r['first_json']) and (ev/r['first_json']).exists())
    check(rid+': settled native capture',bool(cap) and cap.get('captureVersion',0)>=5)
    if cap:
        png=(root/'captures'/rid/'viewport.light.png').read_bytes()
        check(rid+': 1440x900 primary PNG',struct.unpack('>II',png[16:24])==(1440,900))
        check(rid+': full-page content retained',cap['fullpageViewport']['complete'])
        check(rid+': captured final artifact',hashlib.sha256(Path(r['html'][0]).read_bytes()).hexdigest()==cap['artifactSha256'])
    new={c['id']:c for c in json.loads(Path(r['final_json']).read_text()).get('connections',[]) if c.get('direction') in ['both','none']} if r['final_json'] else {}
    if not new:continue
    observed=cap['featureObservations']['relations'] if cap else []
    check(rid+': new relation identities inspected',set(new)=={v['edge']['id'] for v in observed})
    for v in observed:
        check(rid+': reverse structural Route/Reach/static '+v['edge']['id'],v['reverseRouteFound'] and v['reachesOtherEndpoint'] and v['uniqueReachIds'] and v['routeFlows']==0)
    for theme in ['light','dark']:
        svg=root/'captures'/rid/f'export.{theme}.svg';tree=ET.fromstring(svg.read_text())
        ids={e.get('id') for e in tree.iter() if e.get('id')}
        paths={e.get('data-edge-id'):e for e in tree.iter() if e.tag.split('}')[-1]=='path' and e.get('data-edge-id') in new}
        check(rid+': '+theme+' export retains new identities',set(paths)==set(new))
        for eid,c in new.items():
            e=paths[eid];markers=[e.get('marker-start'),e.get('marker-end')]
            expected=all(markers) if c['direction']=='both' else not any(markers)
            resolved=all(not m or (re.fullmatch(r'url\(#([^)]*)\)',m) and re.fullmatch(r'url\(#([^)]*)\)',m).group(1) in ids) for m in markers)
            check(rid+': '+theme+' export markers '+eid,expected and resolved)
            features.append({'run_id':rid,'theme':theme,'id':eid,'direction':c['direction'],'marker_start':markers[0],'marker_end':markers[1],'definitions_resolved':bool(resolved)})
        png=root/'captures'/rid/f'export.{theme}.png'
        check(rid+': '+theme+' native PNG exists',png.is_file() and png.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n')
result={'checks':checks,'passed':sum(c['pass'] for c in checks),'failed':[c for c in checks if not c['pass']],'export_features':features,'scope':'Evidence integrity and recorded feature behavior only. Does not score semantic correctness or visual quality.'}
(root/'audit-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':result['passed'],'failed':result['failed'],'feature_exports':len(features)}))
raise SystemExit(bool(result['failed']))
