import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { desktopBrowser, desktopPointerCheck } from '../archify-244-dev/test/helpers/desktop-browser.mjs';

// Only the CDP transport is reused from dev. Every loaded HTML file below was
// generated unchanged by the issue's pinned v2.16.0 renderer.
const output = path.join(path.dirname(fileURLToPath(import.meta.url)), 'v1-original');
const browser = desktopBrowser('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');
const records = [];
const environment = { rendererSha: '2bfb47132c057195d8dddb3e25ae966dd7c7a72e', version: '2.16.0', node: process.version, viewport: '1440x900 @1', input: 'native CDP pointer and Tab; original issue JSON unchanged' };
try {
  const session = await browser.sessionPromise;
  const send = (method, params = {}) => browser.cdp.send(method, params, session);
  const checkPointer = await desktopPointerCheck(browser, session);
  environment.browser = await browser.cdp.send('Browser.getVersion');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Emulation.setFocusEmulationEnabled', { enabled: true });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  async function run(expression) {
    const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    assert.equal(r.exceptionDetails, undefined, r.exceptionDetails?.exception?.description);
    return r.result.value;
  }
  async function settled() { await run('document.fonts.ready'); await run('new Promise(r=>setTimeout(r,450))'); }
  async function point(selector) {
    return run(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)throw new Error('Missing target');
      if(e instanceof SVGGeometryElement && e.getTotalLength()>0){const p=e.getPointAtLength(e.getTotalLength()/2),q=new DOMPoint(p.x,p.y).matrixTransform(e.getScreenCTM());return {x:q.x,y:q.y};}
      const r=e.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()`);
  }
  async function move(selector) { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...(selector ? await point(selector) : { x: 2, y: 2 }) }); }
  async function click(selector) {
    const p = await point(selector); await move(selector);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...p, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...p, button: 'left', clickCount: 1 }); await settled();
  }
  async function tabTo(selector) {
    for (let i = 0; i < 100; i++) {
      if (await run(`document.activeElement.matches(${JSON.stringify(selector)})`)) return;
      for (const type of ['keyDown','keyUp']) await send('Input.dispatchKeyEvent', { type, key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
    }
    throw new Error('Cannot Tab to ' + selector);
  }
  let serial = 0;
  for (const number of [243, 244]) for (const theme of ['dark','light']) {
    const origin = number === 243 ? 'a' : 'reviewing';
    for (const scenario of ['read','node-hover','node-keyboard','relationship-hover','relationship-keyboard','committed-focus','reach-downstream','focus-url']) {
      await move();
      const loaded = browser.cdp.waitFor('Page.loadEventFired', session);
      await send('Page.navigate', { url: pathToFileURL(path.join(output, `issue-${number}.html`)).href + `?theme=${theme}&run=${++serial}` + (scenario === 'focus-url' ? `#focus=${origin}` : '') });
      await loaded; await checkPointer(); await settled();
      const node = `.diagram-container > svg [data-node-id="${origin}"]`;
      if (scenario === 'node-hover') await move(node);
      if (scenario === 'node-keyboard') await tabTo(node);
      if (scenario === 'relationship-hover') await move('[data-relationship-hit-key]');
      if (scenario === 'relationship-keyboard') await tabTo('[data-relationship-hit-key]');
      if (['committed-focus','reach-downstream'].includes(scenario)) await click(node);
      if (scenario === 'reach-downstream') await click('#btn-reach-downstream');
      await settled();
      const state = await run(`(()=>{
        const svg=document.querySelector('.diagram-container > svg'),walk=document.createTreeWalker(svg,NodeFilter.SHOW_COMMENT);let c,rail;
        while(c=walk.nextNode()){if(c.textContent.includes('Primary lifecycle rail')){rail=c.nextSibling;while(rail&&rail.nodeType!==1)rail=rail.nextSibling;break;}}
        if(!rail||rail.tagName!=='path')throw new Error('Original rail not located');
        const attrs=e=>Object.fromEntries([...e.attributes].map(a=>[a.name,a.value]));
        const box=rail.getBBox();
        return {svg:attrs(svg),focus:Archify.focus.active(),intent:Archify.intentTrace.active(),reach:Archify.focus.reachability(),
          rail:{markup:rail.outerHTML,attrs:attrs(rail),opacity:getComputedStyle(rail).opacity,display:getComputedStyle(rail).display,visibility:getComputedStyle(rail).visibility,bbox:{x:box.x,y:box.y,width:box.width,height:box.height}},
          nodes:[...svg.querySelectorAll('[data-node-id]')].map(n=>({id:n.dataset.nodeId,opacity:getComputedStyle(n).opacity,attrs:attrs(n)})),
          edges:[...svg.querySelectorAll('[data-edge-from]')].map(e=>({from:e.dataset.edgeFrom,to:e.dataset.edgeTo,key:e.dataset.edgeKey,opacity:getComputedStyle(e).opacity}))};
      })()`);
      if (scenario.startsWith('node-')) assert.equal(state.intent, origin);
      if (scenario.startsWith('relationship-')) assert.ok('data-relationship-preview-active' in state.svg);
      if (['committed-focus','focus-url'].includes(scenario)) assert.equal(state.focus, origin);
      if (scenario === 'reach-downstream') assert.ok(state.reach);
      records.push({ number, theme, scenario, ...state });
      const { data } = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
      fs.writeFileSync(path.join(output, `${number}-${theme}-${scenario}.png`), Buffer.from(data, 'base64'));
      console.log(number, theme, scenario, 'rail opacity=' + state.rail.opacity, 'nodes=' + state.nodes.map(n=>`${n.id}:${n.opacity}`).join(','));
    }
  }
} catch (error) { environment.failure = error.stack; throw error; }
finally {
  fs.writeFileSync(path.join(output, 'observations.json'), JSON.stringify({ environment, records }, null, 2) + '\n');
  await browser.close();
}
