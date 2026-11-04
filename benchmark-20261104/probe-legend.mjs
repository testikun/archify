import fs from 'node:fs';
import {ChromeVisualBrowser} from './packages/candidate/archify/bin/visual-check.mjs';
const out='issues/squad-legend-observation';fs.mkdirSync(out,{recursive:true});
const b=new ChromeVisualBrowser('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');
const records=[];
try{
  const metrics=await b.inspect({artifactPath:process.cwd()+'/runs/squad-candidate/workspace/output/squad-coordination.html',width:1440,height:900,theme:'light'});
  const session=await b.sessionPromise;
  const run=async expression=>{
    const r=await b.cdp.send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true},session);
    if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result?.value;
  };
  async function snap(name){
    const state=await run(`(()=>{const rect=e=>e?.getBoundingClientRect().toJSON();return {
      legend:rect(document.querySelector('[data-legend]')),
      directed:rect(document.querySelector('[data-legend-semantic-kind="relation-forward"]')),
      dock:rect(document.querySelector('.diagram-nav')),
      restingDock:Archify.viewerChromeLayout.dockRect(),stage:Archify.viewerChromeLayout.stageRect(),receipt:Archify.viewerChromeLayout.receipt(),
      scrollX,scrollY,innerWidth,innerHeight,html:{...document.documentElement.dataset}
    };})()`);
    records.push({name,state});
    const shot=await b.cdp.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},session);
    fs.writeFileSync(out+'/'+name+'.png',Buffer.from(shot.data,'base64'));
  }
  await snap('01-native-inspect');
  await run(`document.querySelector('[data-preset-value="classic"]').click();`);
  await run(`Archify.layoutStability.whenStable()`);
  await snap('02-preset-click');
  await run(`Archify.motionGovernor.setMode('still');document.documentElement.dataset.motion='still';document.fonts.ready.then(()=>Archify.layoutStability.whenStable())`);
  await snap('03-motion-still');
  await run(`new Promise(r=>setTimeout(r,1000)).then(()=>Archify.layoutStability.whenStable())`);
  await snap('04-settled');
  const clipped=await b.cdp.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,fromSurface:true,clip:{x:0,y:0,width:1440,height:900,scale:1}},session);
  fs.writeFileSync(out+'/05-explicit-clip.png',Buffer.from(clipped.data,'base64'));
  await snap('06-after-clip');
  await run(`new Promise(r=>setTimeout(r,1000)).then(()=>Archify.layoutStability.whenStable())`);
  await snap('07-after-clip-settled');
  const second=await b.cdp.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,fromSurface:true,clip:{x:0,y:0,width:1440,height:900,scale:1}},session);
  fs.writeFileSync(out+'/08-explicit-clip-again.png',Buffer.from(second.data,'base64'));
  await snap('09-after-second-clip');
  fs.writeFileSync(out+'/observations.json',JSON.stringify({nativeMetrics:metrics,records},null,2)+'\n');
  console.log(records.map(r=>({name:r.name,directed:r.state.directed,dock:r.state.dock,restingDock:r.state.restingDock})))
}finally{await b.close();}
