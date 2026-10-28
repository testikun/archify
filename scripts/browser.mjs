import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';
import { ChromeVisualBrowser } from '../source-pinned/archify/bin/visual-check.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'screenshots'), exportsDir=path.join(root,'exports'), receipts=path.join(root,'receipts');
for(const p of [out,exportsDir,path.join(root,'tmp')])fs.mkdirSync(p,{recursive:true});
process.env.TMPDIR=path.join(root,'tmp');
const chrome=process.env.ARCHIFY_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const browser=new ChromeVisualBrowser(chrome,{spawnImpl:(cmd,args,opts)=>spawn(cmd,[
  '--blink-settings=availableHoverTypes=2,primaryHoverType=2,availablePointerTypes=4,primaryPointerType=4',...args],opts)});
const records=[];
const probes=process.argv.includes('--probes');
let send,run;
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function shot(name){const x=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(x.data,'base64'));}
async function click(selector){
  const p=await run(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)throw Error('Missing control');const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2};})()`);
  await send('Input.dispatchMouseEvent',{type:'mouseMoved',...p});
  await send('Input.dispatchMouseEvent',{type:'mousePressed',...p,button:'left',clickCount:1});
  await send('Input.dispatchMouseEvent',{type:'mouseReleased',...p,button:'left',clickCount:1});
}
async function load(name,reduced=false){
  await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:reduced?'reduce':'no-preference'}]});
  const loaded=browser.cdp.waitFor('Page.loadEventFired',await browser.sessionPromise);
  await send('Page.navigate',{url:pathToFileURL(path.join(root,'artifacts',name+'.html')).href+'?theme=light'});
  await loaded;
  await run(`(async()=>{await document.fonts.ready;await Archify.readerLayout?.whenStable();await Archify.viewerChromeLayout?.whenStable();})()`);
  await delay(120);
}
async function snapshot(name){
  const data=await run(`(()=>{
    const svg=document.querySelector('.diagram-container svg'),r=svg.getBoundingClientRect();
    const nodes=[...svg.querySelectorAll('[data-node-id]')].map(e=>({id:e.dataset.nodeId,label:e.dataset.nodeLabel,sublabel:e.dataset.nodeSublabel}));
    const edges=[...svg.querySelectorAll('[data-edge-id]')].filter(e=>e.hasAttribute('data-edge-from')).map(e=>({id:e.dataset.edgeId,from:e.dataset.edgeFrom,to:e.dataset.edgeTo,label:e.dataset.edgeLabel,focus:e.hasAttribute('data-focus-match'),opacity:getComputedStyle(e).opacity,step:e.style.getPropertyValue('--step'),d:e.getAttribute('d')}));
    const texts=[...svg.querySelectorAll('text')].map(e=>{const b=e.getBoundingClientRect(),m=e.getScreenCTM();return{text:e.textContent,cssSize:parseFloat(getComputedStyle(e).fontSize),screenSize:parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b),x:b.x,y:b.y,width:b.width,height:b.height,opacity:getComputedStyle(e).opacity};});
    return{motion:document.documentElement.getAttribute('data-motion'),governor:Archify.motionGovernor?.mode(),motionLabel:document.querySelector('#motion-label')?.textContent,reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,focus:svg.getAttribute('data-focus-active'),viewBox:svg.getAttribute('viewBox'),svgRect:{x:r.x,y:r.y,width:r.width,height:r.height},reader:document.querySelector('.diagram-container')?.getAttribute('data-detail-level'),nodes,edges,texts,animations:document.getAnimations().map(a=>({name:a.animationName,state:a.playState,time:a.currentTime,target:a.effect?.target?.getAttribute('class')})),motionOverlays:[...svg.querySelectorAll('[data-motion-overlay],[data-flow-overlay],[data-live-flow]')].map(e=>({tag:e.tagName,attrs:[...e.attributes].map(a=>[a.name,a.value])})),errors:window.__errors,story:Archify.story?.state()};
  })()`);
  records.push({name,...data});return data;
}
async function exportFile(name,format){
  await run('window.__downloads=[]');
  await click('#btn-export');await click(`[data-format="${format}"]`);
  const item=await run(`new Promise((resolve,reject)=>{let n=0;const poll=()=>{if(window.__downloads.length)return resolve(window.__downloads.at(-1));if(n++>200)return reject(Error('No export captured'));setTimeout(poll,25)};poll();})`);
  fs.writeFileSync(path.join(exportsDir,name+'.'+(format.startsWith('svg')?'svg':'png')),Buffer.from(item.data,'base64'));
  records.push({name:name+'-export',format,downloadName:item.name,byteLength:Buffer.from(item.data,'base64').length});
}
try{
  const session=await browser.sessionPromise;
  send=(method,params={})=>browser.cdp.send(method,params,session);
  run=async expression=>{const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||JSON.stringify(r.exceptionDetails));return r.result?.value;};
  records.push({environment:await browser.cdp.send('Browser.getVersion'),viewport:{width:1440,height:1000,deviceScaleFactor:1},node:process.version,sourceSha:'6ca6a5c84439b57ea22e0630fe306e1d91587a6e'});
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await send('Emulation.setFocusEmulationEnabled',{enabled:true});
  await send('Page.addScriptToEvaluateOnNewDocument',{source:`
    try{localStorage.clear()}catch(e){};window.__errors=[];window.__downloads=[];
    addEventListener('error',e=>__errors.push(e.message));addEventListener('unhandledrejection',e=>__errors.push(String(e.reason)));
    const urls=new Map(),create=URL.createObjectURL.bind(URL);URL.createObjectURL=blob=>{const u=create(blob);urls.set(u,blob);return u};
    const click=HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click=function(){if(this.download&&urls.has(this.href)){const name=this.download;const r=new FileReader();r.onload=()=>__downloads.push({name,data:r.result.split(',')[1]});r.readAsDataURL(urls.get(this.href));return;}return click.call(this)};
  `});
  if(!probes){
  for(const name of ['serial-architecture','serial-sequence','parallel-architecture','parallel-sequence']){
    await load(name);await snapshot(name+'-default');await shot(name+'-default');
    await exportFile(name,'svg');await exportFile(name,'png');
    await click('#btn-motion');await delay(300);await snapshot(name+'-live');
    await click('[data-node-id="page"]');await delay(100);await snapshot(name+'-focus-100ms');await delay(600);await snapshot(name+'-focus-700ms');
    await shot(name+'-focus');await exportFile(name+'-focused','svg');
    await click('#btn-motion');await delay(1000);await snapshot(name+'-still');
    await load(name,true);await snapshot(name+'-reduced');await shot(name+'-reduced');
    await click('#btn-motion');await delay(200);await snapshot(name+'-reduced-after-motion-click');
    console.log(name,'captured');
  }
  for(const name of ['ablation-architecture-no-numbers','ablation-sequence-no-parallel-prose','ablation-architecture-no-cards','probe-retired-views']){
    await load(name);await snapshot(name);await shot(name);await exportFile(name,'svg');
  }
  for(const reduced of [false,true]){
    const name='story-'+(reduced?'reduced':'normal');
    await load('parallel-story',reduced);await snapshot(name+'-initial');
    await click('#btn-motion');
    await run(`(async()=>{for(let i=0;i<300&&!document.querySelector('.story-panel iframe')?.contentWindow?.storyReady;i++)await new Promise(r=>setTimeout(r,30));if(!document.querySelector('.story-panel iframe')?.contentWindow?.storyReady)throw Error('Story did not become ready');Archify.story.setSound(false);})()`);
    const plan=await run(`(()=>{const s=document.querySelector('.story-panel iframe').contentWindow.Story;return{plan:s.plan,actions:s.actions,duration:s.duration};})()`);
    records.push({name:name+'-plan',...plan});
    const actions=plan.actions.filter(a=>a.shot===1);
    for(const id of ['classify-call','extract-call','write-a']){
      const at=actions.find(a=>a.edge===id).start+0.5;
      const frame=await run(`(()=>{const w=document.querySelector('.story-panel iframe').contentWindow;const frame=w.Story.seek(${at});const d=w.document;return{frame,state:Archify.story.state(),reduced:w.matchMedia('(prefers-reduced-motion: reduce)').matches,governor:w.Archify.motionGovernor.mode(),caption:d.querySelector('.caption')?.textContent,text:d.body.innerText,flows:[...d.querySelectorAll('.ambient-edge-flow')].map(e=>({display:w.getComputedStyle(e).display,animations:e.getAnimations().length})),metrics:w.Story.metrics()};})()`);
      records.push({name:name+'-'+id,...frame});await shot(name+'-'+id);
    }
    await click('.story-panel-controls button');await delay(500);
    records.push({name:name+'-playing',state:await run('Archify.story.state()')});
    await click('.story-panel-controls button');
    await exportFile(name,'svg');
    await run('Archify.story.setView("still")');await delay(1000);
    await snapshot(name+'-back-to-still');await shot(name+'-back-to-still');
    console.log(name,'captured');
  }
  }else{
    for(const name of ['parallel-architecture','parallel-sequence']){
      await load(name);await click('#btn-motion');await delay(250);
      const schedule=await run(`(()=>{const svg=document.querySelector('.diagram-container svg');return{choreography:svg.dataset.motionChoreography||'relay',flows:[...svg.querySelectorAll('path[data-animate="edge"]')].map(e=>{const owner=e.closest('[data-edge-id]');let h=e.nextElementSibling;while(h&&!h.classList.contains('ambient-flow-head'))h=h.nextElementSibling;return{id:owner?.dataset.edgeId,label:owner?.dataset.edgeLabel,step:e.style.getPropertyValue('--step'),delay:h?.style.getPropertyValue('--flow-delay'),animationDelay:h?getComputedStyle(h).animationDelay:null};})};})()`);
      records.push({name:name+'-live-schedule',...schedule});
      const p=await run(`(()=>{const r=document.querySelector('[data-node-id="page"]').getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2};})()`);
      await send('Input.dispatchMouseEvent',{type:'mouseMoved',...p});await delay(220);
      records.push({name:name+'-hover',...await run(`(()=>{const s=document.querySelector('.diagram-container svg');return{active:s.getAttribute('data-intent-trace-active'),edges:[...s.querySelectorAll('[data-edge-id][data-intent-trace-match]')].map(e=>e.dataset.edgeId),focus:s.getAttribute('data-focus-active')};})()`)});
      await shot(name+'-hover');
      await click('[data-node-id="page"]');
      await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:1350,y:105});await delay(900);
      records.push({name:name+'-focus-without-row-hover',...await run(`(()=>{const s=document.querySelector('.diagram-container svg');return{focus:s.getAttribute('data-focus-active'),edges:[...s.querySelectorAll('[data-edge-id]')].filter(e=>e.hasAttribute('data-edge-from')).map(e=>({id:e.dataset.edgeId,tag:e.tagName,match:e.hasAttribute('data-focus-match'),opacity:getComputedStyle(e).opacity})),rows:[...document.querySelectorAll('button[data-relationship-target]')].map(e=>({id:e.dataset.relationshipId,text:e.innerText}))};})()`)});
      await shot(name+'-focus-without-row-hover');
      await run(`document.querySelector('button[data-relationship-id="write-a"]').focus()`);
      const before=await run('document.activeElement.dataset.relationshipId');
      await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowDown',code:'ArrowDown',windowsVirtualKeyCode:40});
      await send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowDown',code:'ArrowDown',windowsVirtualKeyCode:40});
      records.push({name:name+'-passport-keyboard-preview',before,after:await run('document.activeElement.dataset.relationshipId')});
    }
    await load('probe-retired-views');records.push({name:'retired-views',...await run(`({guidedCount:Archify.guidedViews?.count,ui:!!document.getElementById('guided-views'),data:document.getElementById('archify-guided-views-data')?.textContent})`)});
  }
}catch(error){records.push({harnessError:String(error.stack)});throw error;}
finally{fs.writeFileSync(path.join(receipts,probes?'browser-probes.json':'browser.json'),JSON.stringify(records,null,2)+'\n');await browser.close();}
