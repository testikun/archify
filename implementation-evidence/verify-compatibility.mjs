import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { extractSvgs } from '../implementation/test/helpers/xml.mjs';
const base = path.resolve(import.meta.dirname, '../latest-dev-20261103/source');
const candidate = path.resolve(import.meta.dirname, '../implementation');
const output = path.join(import.meta.dirname, 'same-input'); fs.mkdirSync(output, {recursive:true});
const golden = fs.readFileSync(path.join(candidate,'test/golden.mjs'),'utf8').match(/const GOLDEN = (\[[\s\S]*?\n\]);/)[1];
const cases = Function('return '+golden)();
const sha = s => createHash('sha256').update(s).digest('hex');
const report = [];
for(const [type, input, name] of cases) {
  const row = {type,input, inputSha256:sha(fs.readFileSync(path.join(candidate,'archify/examples',input)))};
  for(const [arm, source] of [['base',base],['candidate',candidate]]) {
    const htmlPath = path.join(output,arm+'-'+name);
    const run = spawnSync(process.execPath,[path.join(source,`archify/renderers/${type}/render-${type}.mjs`),path.join(candidate,'archify/examples',input),htmlPath],{encoding:'utf8'});
    row[arm]={exitCode:run.status,diagnostics:run.stderr.trim(),htmlPath};
    if(run.status===0) {
      const svg = extractSvgs(fs.readFileSync(htmlPath,'utf8')).direct.find(s=>s.includes('data-node-id'));
      if(!svg) throw Error('Missing native SVG: '+htmlPath);
      row[arm].svgSha256=sha(svg);
    }
  }
  row.identicalSvg=!!row.base.svgSha256&&row.base.svgSha256===row.candidate.svgSha256;
  report.push(row);
}
const newInput=path.join(candidate,'test/fixtures/architecture-directions.json');
const unsupported=spawnSync(process.execPath,[path.join(base,'archify/bin/archify.mjs'),'validate','architecture',newInput,'--json'],{encoding:'utf8'});
fs.writeFileSync(path.join(output,'base-new-capability.json'),unsupported.stdout||unsupported.stderr);
fs.writeFileSync(path.join(output,'comparison.json'),JSON.stringify({base:'63c9263e84bd3993cab8e09b3d69888857858635',candidate:'uncommitted local implementation',rows:report,newCapabilityBaseExitCode:unsupported.status},null,2)+'\n');
console.log(JSON.stringify({cases:report.length,identicalSvg:report.filter(r=>r.identicalSvg).length,newCapabilityBaseExitCode:unsupported.status}));
if(report.some(r=>!r.identicalSvg)||unsupported.status===0)process.exitCode=1;
