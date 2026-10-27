import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';

const evidence = path.dirname(fileURLToPath(import.meta.url));
const checkout = process.argv[2];
assert.ok(checkout, 'Usage: node verify-browser.mjs /absolute/dev-checkout');
const { desktopBrowser, desktopPointerCheck } = await import(pathToFileURL(path.join(checkout, 'test/helpers/desktop-browser.mjs')));
const chrome = process.env.ARCHIFY_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const directExit = process.env.ARCHIFY_VERIFY_DIRECT_EXIT === '1';
const output = path.join(evidence, directExit ? 'direct-exit' : 'browser');
fs.mkdirSync(output, { recursive: true });
const browser = desktopBrowser(chrome);
const records = [];
const environment = {
  sha: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: checkout, encoding: 'utf8' }).trim(),
  node: process.version, os: `${os.type()} ${os.release()} ${os.arch()}`,
  viewport: { width: 1440, height: 900, deviceScaleFactor: 1 },
  runner: 'Agent-operated real headless Chrome via CDP; native mouse and Tab/Enter/Escape input',
  mode: directExit ? 'direct exit without exporting first' : 'canonical export, then exit',
  timestamp: new Date().toISOString(),
};
const sha = text => createHash('sha256').update(text).digest('hex');
try {
  const session = await browser.sessionPromise;
  const send = (method, params = {}) => browser.cdp.send(method, params, session);
  const pointerCheck = await desktopPointerCheck(browser, session);
  environment.browser = await browser.cdp.send('Browser.getVersion');
  await browser.cdp.send('Browser.setDownloadBehavior', { behavior: 'deny' });
  await send('Emulation.setFocusEmulationEnabled', { enabled: true });
  await send('Emulation.setDeviceMetricsOverride', { ...environment.viewport, mobile: false });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  async function run(expression) {
    const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    assert.equal(result.exceptionDetails, undefined, result.exceptionDetails?.exception?.description);
    return result.result?.value;
  }
  await send('Page.addScriptToEvaluateOnNewDocument', { source: `
    window.verificationErrors=[];
    addEventListener('error',e=>verificationErrors.push(e.message));
    addEventListener('unhandledrejection',e=>verificationErrors.push(String(e.reason)));
    window.verificationWait=predicate=>new Promise((resolve,reject)=>{
      const start=performance.now();function poll(){if(predicate())return resolve();
      if(performance.now()-start>10000)return reject(new Error('State not reached: '+predicate));
      requestAnimationFrame(poll);}requestAnimationFrame(poll);
    });
  ` });
  async function wait(expression) { await run(`verificationWait(()=>(${expression}))`); }
  async function stable() {
    await run('document.fonts.ready');
    await run('Archify.viewerChromeLayout.whenStable()');
    await wait(`!document.querySelector('.diagram-container').hasAttribute('data-camera-transaction')`);
    await run('new Promise(resolve=>setTimeout(resolve,250))');
  }
  async function key(name, code = name, keyCode = { Tab: 9, Enter: 13, Escape: 27 }[name]) {
    await send('Input.dispatchKeyEvent', { type: 'keyDown', key: name, code, windowsVirtualKeyCode: keyCode, ...(name === 'Enter' ? { text: '\r' } : {}) });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', key: name, code, windowsVirtualKeyCode: keyCode });
  }
  async function point(selector) {
    return run(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)throw new Error('Missing target '+${JSON.stringify(selector)});
      if(e instanceof SVGGeometryElement && e.getTotalLength()>0){const p=e.getPointAtLength(e.getTotalLength()/2);const q=new DOMPoint(p.x,p.y).matrixTransform(e.getScreenCTM());return {x:q.x,y:q.y};}
      const r=e.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()`);
  }
  async function move(selector) { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...(selector ? await point(selector) : { x: 2, y: 2 }) }); }
  async function click(selector) {
    const p = await point(selector);
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...p });
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...p, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...p, button: 'left', clickCount: 1 });
    await stable();
  }
  async function tabTo(selector) {
    for (let i = 0; i < 100; i++) {
      if (await run(`document.activeElement.matches(${JSON.stringify(selector)})`)) return i;
      await key('Tab');
    }
    throw new Error('Tab did not reach ' + selector);
  }
  let navigationId = 0;
  async function load(number, theme, hash = '') {
    await move();
    const loaded = browser.cdp.waitFor('Page.loadEventFired', session);
    await send('Page.navigate', { url: pathToFileURL(path.join(evidence, `issue-${number}.v3.html`)).href + `?theme=${theme}&verification=${++navigationId}` + hash });
    await loaded; await pointerCheck(); await stable();
  }
  async function snapshot() {
    return run(`(()=>{
      const svg=document.querySelector('.diagram-container > svg');
      const attrs=e=>Object.fromEntries([...e.attributes].map(a=>[a.name,a.value]));
      const geometry=e=>({tag:e.tagName,attrs:Object.fromEntries([...e.attributes].filter(a=>['d','x','y','x1','y1','x2','y2','width','height','points','transform','marker-end','marker-start'].includes(a.name)).map(a=>[a.name,a.value]))});
      const semantic=e=>({id:e.dataset.nodeId,key:e.dataset.edgeKey,from:e.dataset.edgeFrom,to:e.dataset.edgeTo,attrs:attrs(e),opacity:getComputedStyle(e).opacity});
      return {svg:attrs(svg),focus:Archify.focus.active(),intent:Archify.intentTrace.active(),reach:Archify.focus.reachability(),hash:location.hash,
        activeElement:{tag:document.activeElement.tagName,attrs:attrs(document.activeElement)},
        nodes:[...svg.querySelectorAll('[data-node-id]')].map(semantic),edges:[...svg.querySelectorAll('[data-edge-from]')].map(semantic),
        drawnRailCount:svg.querySelectorAll('[data-lifecycle-rail],[data-decorative="lifecycle-rail"]').length,
        unownedArrowMarks:[...svg.querySelectorAll('[marker-end],[marker-start]')].filter(e=>!e.closest('defs,[data-edge-from],[data-intent-trace-overlay],[data-relationship-pulse-overlay],[data-relationship-hit-overlay]')).map(e=>e.outerHTML),
        geometry:[...svg.querySelectorAll('[data-node-id], [data-edge-from]')].map(e=>({id:e.dataset.nodeId,key:e.dataset.edgeKey,items:[e,...e.querySelectorAll('path,line,polyline,rect,circle,ellipse,polygon,text')].map(geometry)})),
        errors:verificationErrors,external:performance.getEntriesByType('resource').map(e=>e.name).filter(x=>/^https?:/.test(x)),
        pointer:__archifyTestPointer.sample(),theme:document.documentElement.getAttribute('data-theme'),
        panels:{finderHidden:document.getElementById('node-finder').hidden,passportHidden:document.getElementById('focus-chip').hidden}};
    })()`);
  }
  async function screenshot(name) {
    const { data } = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    fs.writeFileSync(path.join(output, name + '.png'), Buffer.from(data, 'base64'));
  }
  async function canonicalExport(name) {
    const svgText = await run(`(async()=>{
      const original=URL.createObjectURL;let blob;
      URL.createObjectURL=function(value){if(value.type.startsWith('image/svg+xml'))blob=value;return original.call(this,value);};
      try{await Archify.exportMenu.run('svg');}finally{URL.createObjectURL=original;}
      if(!blob)throw new Error('No SVG export produced');return await blob.text();
    })()`);
    fs.writeFileSync(path.join(output, name + '.svg'), svgText);
    const inspection = await run(`(()=>{const doc=new DOMParser().parseFromString(${JSON.stringify(svgText)},'image/svg+xml'),s=doc.documentElement;
      return {parseErrors:doc.querySelectorAll('parsererror').length,rail:s.querySelectorAll('[data-lifecycle-rail]').length,
      transient:[s,...s.querySelectorAll('*')].flatMap(e=>[...e.attributes].filter(a=>/^data-(focus|reach|relationship|intent-trace)/.test(a.name)).map(a=>a.name)),
      nodes:[...s.querySelectorAll('[data-node-id]')].map(e=>e.dataset.nodeId),edges:[...s.querySelectorAll('[data-edge-from]')].map(e=>[e.dataset.edgeFrom,e.dataset.edgeTo])};})()`);
    assert.equal(inspection.parseErrors, 0); assert.equal(inspection.rail, 0); assert.deepEqual(inspection.transient, []);
    return { sha256: sha(svgText), ...inspection };
  }
  for (const number of [243, 244]) for (const theme of ['dark', 'light']) {
    const source = JSON.parse(fs.readFileSync(path.join(evidence, `issue-${number}.lifecycle.json`)));
    const origin = number === 243 ? 'a' : 'reviewing';
    const target = number === 243 ? 'b' : 'blocked';
    const node = id => `.diagram-container > svg [data-node-id="${id}"]`;
    const relationship = '[data-relationship-hit-key]';
    await load(number, theme);
    const baseline = await snapshot();
    const prefix = `${number}-${theme}`;
    await screenshot(prefix + '-read');
    const canonical = directExit ? null : await canonicalExport(prefix + '-read');
    const scenarios = ['node-hover','node-keyboard','relationship-hover','relationship-keyboard','committed-focus','reach-downstream','reach-upstream','focus-url','reach-url'];
    if (number === 244) scenarios.push('isolated-node');
    records.push({ number, theme, scenario: 'read', state: baseline, canonical });
    for (const scenario of scenarios) {
      const name = `${prefix}-${scenario}`;
      const hash = scenario === 'focus-url' ? `#focus=${origin}` : scenario === 'reach-url' ? `#focus=${origin}&reach=downstream` : '';
      await load(number, theme, hash);
      if (scenario === 'node-hover') { await move(node(origin)); await wait(`Archify.intentTrace.active()===${JSON.stringify(origin)}`); }
      if (scenario === 'node-keyboard') { await tabTo(node(origin)); await wait(`Archify.intentTrace.active()===${JSON.stringify(origin)}`); }
      if (scenario === 'relationship-hover') { await move(relationship); await wait(`document.querySelector('svg[data-relationship-preview-active]')`); }
      if (scenario === 'relationship-keyboard') { await tabTo(relationship); await wait(`document.querySelector('svg[data-relationship-preview-active]')`); }
      if (['committed-focus','reach-downstream','reach-upstream','isolated-node'].includes(scenario)) {
        await click(node(scenario === 'reach-upstream' ? target : scenario === 'isolated-node' ? 'planning' : origin));
        if (scenario.startsWith('reach-')) await click('#btn-' + scenario);
      }
      await move(scenario.endsWith('-hover') ? scenario.startsWith('node-') ? node(origin) : relationship : null);
      await stable();
      const state = await snapshot();
      const record = { number, theme, scenario, state };
      records.push(record);
      assert.deepEqual(state.errors, []); assert.deepEqual(state.external, []);
      assert.equal(state.drawnRailCount, 0); assert.deepEqual(state.unownedArrowMarks, []);
      assert.deepEqual(state.geometry, baseline.geometry);
      assert.deepEqual(state.nodes.map(n=>n.id).sort(), source.states.map(n=>n.id).sort());
      assert.deepEqual([...new Map(state.edges.map(e=>[e.key,[e.from,e.to]])).values()], source.transitions.map(e=>[e.from,e.to]));
      if (scenario.startsWith('reach-')) {
        assert.ok(state.reach, 'Reachability must actually be active');
        assert.deepEqual([...state.reach.nodeIds].sort(), [origin,target].sort());
        assert.equal(state.reach.edgeKeys.length, 1);
      }
      if (['committed-focus','focus-url'].includes(scenario)) assert.equal(state.focus, origin);
      if (scenario === 'isolated-node') assert.equal(state.focus, 'planning');
      if (scenario === 'isolated-node') {
        assert.equal(state.reach, null);
        assert.deepEqual(await run(`['upstream','downstream'].map(x=>document.getElementById('btn-reach-'+x).disabled)`), [true,true]);
      }
      await screenshot(name);
      if (!directExit) {
        record.canonical = await canonicalExport(name);
        record.canonicalBytesEqualRead = record.canonical.sha256 === canonical.sha256;
        assert.deepEqual(record.canonical.nodes, canonical.nodes); assert.deepEqual(record.canonical.edges, canonical.edges);
      }
      await key('Escape'); await key('Escape');
      await click('h1'); await move(); await stable();
      record.restored = await snapshot();
      assert.equal(record.restored.focus, null); assert.equal(record.restored.intent, null); assert.equal(record.restored.reach, null);
      assert.equal(record.restored.svg['data-relationship-preview-active'], undefined);
      assert.deepEqual(record.restored.geometry, baseline.geometry);
      assert.deepEqual(record.restored.nodes.map(n=>n.opacity), baseline.nodes.map(n=>n.opacity));
      assert.deepEqual(record.restored.edges.map(n=>n.opacity), baseline.edges.map(n=>n.opacity));
      assert.deepEqual(record.restored.panels, baseline.panels);
      await screenshot(name + '-restored');
      record.passed = true;
      console.log('PASS', name, directExit ? 'direct exit restored READ' : 'canonicalBytesEqualRead=' + record.canonicalBytesEqualRead);
    }
  }
} catch (error) {
  environment.failure = error.stack;
  throw error;
} finally {
  fs.writeFileSync(path.join(output, 'observations.json'), JSON.stringify({ environment, records }, null, 2) + '\n');
  await browser.close();
}
