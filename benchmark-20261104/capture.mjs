import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
const root = path.dirname(fileURLToPath(import.meta.url));
const observations = JSON.parse(fs.readFileSync(path.join(root, 'observations.json')));
const { ChromeVisualBrowser } = await import(pathToFileURL(path.join(root, 'packages/candidate/archify/bin/visual-check.mjs')));
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const metricsPath = path.join(root, 'captures/metrics.json');
const cached = new Map((fs.existsSync(metricsPath) ? JSON.parse(fs.readFileSync(metricsPath)) : []).map(r => [r.run_id, r]));
const results = [];
for (const row of observations) {
  if (row.html.length !== 1) continue;
  const artifactSha256 = createHash('sha256').update(fs.readFileSync(row.html[0])).digest('hex');
  const newDirections = (row.relationship_directions?.both || 0) + (row.relationship_directions?.none || 0);
  const specification=JSON.parse(fs.readFileSync(row.final_json));
  const needsFeatureEvidence=newDirections||Object.keys(specification.meta?.legend?.entries||{}).some(k=>k.startsWith('relation-'));
  if (cached.get(row.run_id)?.artifactSha256 === artifactSha256 && cached.get(row.run_id)?.captureVersion >= 5 && cached.get(row.run_id)?.fullpageViewport?.complete && (!needsFeatureEvidence || cached.get(row.run_id)?.featureObservations)) {
    results.push(cached.get(row.run_id));
    continue;
  }
  const browser = new ChromeVisualBrowser(chrome);
  const out = path.join(root, 'captures', row.run_id);
  fs.mkdirSync(out, { recursive: true });
  try {
    const session = await browser.sessionPromise;
    const evaluate = async expression => {
      const value = await browser.cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }, session);
      if (value.exceptionDetails) throw Error(value.exceptionDetails.exception?.description || JSON.stringify(value.exceptionDetails));
      return value.result?.value;
    };
    await browser.cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: `
      window.benchmarkDownloads=[];const blobUrls=new Map(),create=URL.createObjectURL.bind(URL);
      URL.createObjectURL=blob=>{const url=create(blob);blobUrls.set(url,blob);return url;};
      HTMLAnchorElement.prototype.click=function(){if(this.download)benchmarkDownloads.push({name:this.download,blob:blobUrls.get(this.href)});};
    ` }, session);
    const metrics = await browser.inspect({ artifactPath: row.html[0], width: 1440, height: 900, theme: 'light' });
    const authoredPreset = await evaluate('document.documentElement.dataset.preset');
    async function classicStill() {
      await evaluate(`(async()=>{document.querySelector('[data-preset-value="classic"]')?.click();
        if(window.Archify?.motionGovernor)Archify.motionGovernor.setMode('still');
        document.documentElement.dataset.motion='still';
        await document.fonts.ready;await Archify.layoutStability?.whenStable();})()`);
      const state = await evaluate(`({preset:document.documentElement.dataset.preset,motion:document.documentElement.dataset.motion,theme:document.documentElement.dataset.theme,scale:devicePixelRatio,zoom:visualViewport.scale})`);
      if (state.preset !== 'classic' || state.motion !== 'still' || state.scale !== 1 || state.zoom !== 1) throw Error(JSON.stringify(state));
      return state;
    }
    const state = await classicStill();
    const page = await browser.cdp.send('Page.getLayoutMetrics', {}, session);
    async function screenshot(filename, expectedHeight) {
      const shot=await browser.cdp.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false,fromSurface:true},session);
      const bytes=Buffer.from(shot.data,'base64');
      fs.writeFileSync(path.join(out,filename),bytes);
      if(bytes.readUInt32BE(16)!==1440||bytes.readUInt32BE(20)!==expectedHeight)throw Error('Unexpected screenshot dimensions: '+filename);
    }
    await screenshot('viewport.light.png',900);
    // An explicit CDP screenshot clip causes a transient layout change in this
    // Chrome build. Keep the primary viewport native and label the tall view.
    let fullpageHeight=Math.max(900,Math.ceil(page.cssContentSize.height));
    let fullpageContentHeight=fullpageHeight;
    let frozenDiagramSize=false;
    for(let attempt=0;attempt<4;attempt++){
      await browser.inspect({artifactPath:row.html[0],width:1440,height:fullpageHeight,theme:'light'});
      await classicStill();
      fullpageContentHeight=Math.ceil((await browser.cdp.send('Page.getLayoutMetrics',{},session)).cssContentSize.height);
      if(fullpageContentHeight<=fullpageHeight)break;
      if(attempt<3)fullpageHeight=fullpageContentHeight;
    }
    if(fullpageContentHeight>fullpageHeight){
      // Small diagrams expand to fill any taller viewport, pushing their cards
      // below it indefinitely. Freeze only the settled diagram/SVG box sizes
      // for this supplemental full-page capture; the primary image stays native.
      await browser.inspect({artifactPath:row.html[0],width:1440,height:900,theme:'light'});
      await classicStill();
      await evaluate(`document.querySelectorAll('.diagram-container,.diagram-container>svg').forEach(e=>{const r=e.getBoundingClientRect();for(const [k,v] of Object.entries({width:r.width+'px',height:r.height+'px','min-height':r.height+'px','max-height':r.height+'px','box-sizing':'border-box'}))e.style.setProperty(k,v,'important')})`);
      frozenDiagramSize=true;
      fullpageHeight=Math.max(900,Math.ceil(page.cssContentSize.height));
      for(let attempt=0;attempt<3;attempt++){
        await browser.cdp.send('Emulation.setDeviceMetricsOverride',{width:1440,height:fullpageHeight,deviceScaleFactor:1,mobile:false},session);
        await evaluate(`new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))`);
        fullpageContentHeight=Math.ceil((await browser.cdp.send('Page.getLayoutMetrics',{},session)).cssContentSize.height);
        if(fullpageContentHeight<=fullpageHeight)break;
        if(attempt<2)fullpageHeight=fullpageContentHeight;
      }
    }
    if(fullpageContentHeight>fullpageHeight)throw Error('Full-page content still exceeds capture height: '+row.run_id);
    await screenshot('fullpage.light.png',fullpageHeight);
    const exports = [];
    let featureObservations = null;
    if (needsFeatureEvidence) {
      for (const theme of ['light', 'dark']) {
        await browser.inspect({ artifactPath: row.html[0], width: 1440, height: 900, theme }); await classicStill();
        const shot = await browser.cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false }, session);
        fs.writeFileSync(path.join(out, `directions.${theme}.png`), Buffer.from(shot.data, 'base64'));
        for (const format of ['svg', 'png']) {
          const data = await evaluate(`(async()=>{benchmarkDownloads.length=0;Archify.exportMenu.run(${JSON.stringify(format)});
            const start=performance.now();while(!benchmarkDownloads[0]?.blob){if(performance.now()-start>15000)throw Error('Export timeout');await new Promise(r=>setTimeout(r,25));}
            return await new Promise(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.readAsDataURL(benchmarkDownloads[0].blob);});})()`);
          const filename = `export.${theme}.${format}`;
          fs.writeFileSync(path.join(out, filename), Buffer.from(data, 'base64'));
          exports.push(filename);
        }
      }
      await browser.inspect({ artifactPath: row.html[0], width: 1440, height: 900, theme: 'light' });
      await classicStill();
      featureObservations = await evaluate(`(()=>{
        const relations=[...document.querySelectorAll('.diagram-container path[data-edge-id]')]
          .filter(p=>['both','none'].includes(p.dataset.edgeDirection))
          .map(p=>({id:p.dataset.edgeId,from:p.dataset.edgeFrom,to:p.dataset.edgeTo,direction:p.dataset.edgeDirection,start:p.getAttribute('marker-start'),end:p.getAttribute('marker-end')}));
        const unique=[...new Map(relations.map(r=>[r.id,r])).values()],results=[];
        Archify.motionGovernor.setMode('live');
        for(const edge of unique){
          Archify.focus.clear();Archify.routeProbe.begin({source:edge.to});
          const found=Archify.routeProbe.choose(edge.from),snapshot=Archify.routeProbe.exportSnapshot();
          const routeFlows=document.querySelectorAll('.route-probe-flow').length;
          Archify.focus.set(edge.to,{toggle:false});Archify.focus.reach('downstream');
          const reach=Archify.focus.reachabilitySnapshot();
          results.push({edge,reverseRouteFound:found,route:snapshot,routeFlows,
            reachesOtherEndpoint:reach?.nodeIds.includes(edge.from),reach,
            uniqueReachIds:reach?new Set(reach.edges.map(e=>e.id)).size===reach.edges.length:null});
          Archify.focus.clearReach();Archify.focus.clear();
        }
        return {relations:results,legend:[...document.querySelectorAll('[data-legend-semantic-kind^="relation-"]')].map(e=>e.textContent.trim()),mode:'live',interpretation:'Structural reachability; no runtime-flow claim. Inspect routes and metadata in the saved observation.'};
      })()`);
      fs.writeFileSync(path.join(out, 'relationship-interactions.json'), JSON.stringify(featureObservations, null, 2)+'\n');
    }
    results.push({ run_id: row.run_id, artifact: row.html[0], artifactSha256, captureVersion: 6, authoredPreset, screenshotState: state, metrics, contentHeight: page.cssContentSize.height, fullpageViewport:{width:1440,height:fullpageHeight,contentHeight:fullpageContentHeight,complete:fullpageContentHeight<=fullpageHeight,frozenDiagramSize,method:'Native screenshot with captureBeyondViewport=false after explicit tall-viewport layout settles; may reflow compared with the primary 1440x900 viewport.'+(frozenDiagramSize?' Diagram/SVG box sizes are temporarily fixed to their settled primary-viewport dimensions so viewport-filling diagrams do not indefinitely push cards below the capture. Original HTML is untouched.':'')}, exports, featureObservations });
    console.log(row.run_id, page.cssContentSize.height);
  } finally { await browser.close(); }
}
fs.mkdirSync(path.dirname(metricsPath), { recursive: true });
fs.writeFileSync(metricsPath, JSON.stringify(results, null, 2) + '\n');

