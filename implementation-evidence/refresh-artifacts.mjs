import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
process.chdir(path.resolve(import.meta.dirname,'../implementation'));
execFileSync(process.execPath,['scripts/generate-viewer.mjs']);
execFileSync(process.execPath,['archify/scripts/generate-validators.mjs']);
const golden=fs.readFileSync('test/golden.mjs','utf8').match(/const GOLDEN = (\[[\s\S]*?\n\]);/)[1];
const mappings=Function('return '+golden)();
for(const input of fs.readdirSync('archify/examples').filter(f=>f.endsWith('.json'))){
  const d=JSON.parse(fs.readFileSync(path.join('archify/examples',input),'utf8'));
  if(d.diagram_type&&d.meta?.output){const output=path.basename(d.meta.output);if((fs.existsSync(path.join('archify/examples',output))||fs.existsSync(path.join('examples',output)))&&!mappings.some(m=>m[2]===output))mappings.push([d.diagram_type,input,output]);}
}
for(const [type,input,output] of mappings)for(const dir of ['examples','archify/examples']){
  const target=path.join(dir,output);if(fs.existsSync(target))execFileSync(process.execPath,[`archify/renderers/${type}/render-${type}.mjs`,path.join('archify/examples',input),target],{stdio:'pipe'});
}
execFileSync(process.execPath,['archify/bin/archify.mjs','compare','architecture','archify/examples/checkout-platform.base.architecture.json','archify/examples/checkout-platform.head.architecture.json','examples/checkout-platform-delta.html','--receipt','examples/checkout-platform-delta.receipt.json','--quality','showcase','--json'],{stdio:'pipe'});
execFileSync(process.execPath,['scripts/build-gallery.mjs','docs'],{stdio:'pipe'});
// The original hand-authored sample retains its geometry and refreshes only Viewer runtime/data.
const template=fs.readFileSync('archify/assets/template.html','utf8');
const scripts=[...template.matchAll(/<script\b[^>]*>[\s\S]*?<\/script>/g)].map(m=>m[0]).filter(s=>!s.includes('type="application/json"'));
let scriptIndex=0;
let sample=fs.readFileSync('examples/web-app.html','utf8').replace(/<script\b[^>]*>[\s\S]*?<\/script>/g,s=>s.includes('type="application/json"')?s:scripts[scriptIndex++]);
if(scriptIndex!==scripts.length)throw Error('Unexpected legacy sample script inventory');
const catalog=[...fs.readFileSync('archify/examples/web-app-rendered.html','utf8').matchAll(/<script\b[^>]*>[\s\S]*?<\/script>/g)].map(m=>m[0]).find(s=>s.includes('id="archify-i18n-data"'));
sample=sample.replace(/<script\b[^>]*id="archify-i18n-data"[^>]*>[\s\S]*?<\/script>/,()=>catalog);
fs.writeFileSync('examples/web-app.html',sample);
console.log('Regenerated template, validators, examples, Checkout Delta and Gallery.');
