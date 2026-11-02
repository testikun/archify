import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { ChromeVisualBrowser, findChrome } from '../source/archify/bin/visual-check.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const run = path.join(root, 'runs', process.argv[2] || 'baseline');
const out = path.join(run, 'supplement');
if (fs.existsSync(out)) throw new Error('Supplement exists; preserve it and use a fresh run.');
fs.mkdirSync(out);
process.env.TMPDIR = path.join(run, 'tmp');
const browser = new ChromeVisualBrowser(findChrome());
const results = { measuredAt: new Date().toISOString(), note: 'Agent-operated DOM and reachability measurements; no human or screen-reader review.', observations: [] };
const save = () => fs.writeFileSync(path.join(out, 'measurements.json'), JSON.stringify(results, null, 2) + '\n');
try {
  results.browser = await browser.cdp.send('Browser.getVersion');
  for (const file of fs.readdirSync(path.join(run, 'artifacts')).filter(n => n.endsWith('.html'))) {
    const name = file.slice(0, -5);
    const artifact = path.join(run, 'artifacts', file);
    const input = JSON.parse(fs.readFileSync(path.join(run, 'inputs', `${name}.json`)));
    for (const [width, height] of [[1440, 900], [1920, 1080]]) {
      await browser.resetPage();
      const gateMetrics = await browser.inspect({ artifactPath: artifact, width, height, theme: 'light' });
      const session = await browser.sessionPromise;
      const send = (method, params = {}) => browser.cdp.send(method, params, session);
      const evaluate = async expression => {
        const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
        if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
        return r.result.value;
      };
      const measured = await evaluate(`(() => {
        const svg = document.querySelector('.diagram-container svg');
        const rect = el => { const r = el.getBoundingClientRect(); return { x:r.x, y:r.y, width:r.width, height:r.height, bottom:r.bottom }; };
        const text = el => { const m=el.getScreenCTM(); const style=getComputedStyle(el); return { text:el.textContent.trim(), sourceFontPx:parseFloat(style.fontSize), actualScreenFontPx:parseFloat(style.fontSize)*Math.hypot(m.a,m.b), visible:el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}), box:rect(el) }; };
        return {
          viewport:{width:innerWidth,height:innerHeight}, rawScrollHeight:document.documentElement.scrollHeight,
          rawScrollWidth:document.documentElement.scrollWidth, scrollY,
          rail:document.documentElement.getAttribute('data-reader-rail'),
          readerOverflow:document.documentElement.getAttribute('data-reader-overflow'),
          camera:Archify.view.state(), motion:document.documentElement.getAttribute('data-motion'),
          detail:document.querySelector('.diagram-container').getAttribute('data-detail-level'),
          preset:document.documentElement.getAttribute('data-visual-preset'), theme:document.documentElement.getAttribute('data-theme'),
          svgBox:rect(svg), viewBox:svg.getAttribute('viewBox'),
          primary:[...svg.querySelectorAll('text[data-node-label]')].map(text),
          context:[...svg.querySelectorAll('text[data-detail="context"],g[data-detail="context"] text')].map(text),
          nodeIds:[...svg.querySelectorAll('g[data-node-id]')].map(el=>el.getAttribute('data-node-id')),
          edgeIds:[...svg.querySelectorAll('path[data-edge-id]')].map(el=>el.getAttribute('data-edge-id')),
          edges:[...svg.querySelectorAll('path[data-edge-from][data-edge-to]')].map(el=>({from:el.getAttribute('data-edge-from'),to:el.getAttribute('data-edge-to')})),
          cards:[...document.querySelectorAll('.cards .card')].map(el=>({text:el.innerText,box:rect(el),visible:el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})})),
          cardItems:[...document.querySelectorAll('.cards li')].map(el=>({text:el.textContent.trim(),fontPx:parseFloat(getComputedStyle(el).fontSize),box:rect(el)})),
          railBox:document.querySelector('.reader-rail')?rect(document.querySelector('.reader-rail')):null,
          documentOverflow:[document.documentElement,document.body].map(el=>({tag:el.tagName,x:getComputedStyle(el).overflowX,y:getComputedStyle(el).overflowY}))
        };
      })()`);
      measured.expected = { nodes:input.states.length, edges:input.transitions.length, cards:(input.cards||[]).length, items:(input.cards||[]).flatMap(c=>c.items).length };
      measured.missingStateIds = input.states.map(s=>s.id).filter(id=>!measured.nodeIds.includes(id));
      measured.missingTransitions = input.transitions.filter(t=>!measured.edges.some(e=>e.from===t.from&&e.to===t.to));
      measured.missingCardText = (input.cards||[]).flatMap(c=>[c.title,...c.items]).filter(t=>!measured.cards.some(c=>c.text.includes(t)));
      // Scroll each authored label / note into view, then check its visible intersection.
      // This establishes document reachability, not legibility or assistive-technology usability.
      measured.reachability = await evaluate(`(async () => {
        const elements=[...document.querySelectorAll('.diagram-container svg text[data-node-label],.diagram-container svg g[data-edge-id] text,.cards .card h3,.cards .card-title,.cards .card li')];
        const values=[];
        for(const el of elements){
          el.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'});
          await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
          const b=el.getBoundingClientRect();
          const x=Math.max(0,Math.min(b.right,innerWidth)-Math.max(0,b.left));
          const y=Math.max(0,Math.min(b.bottom,innerHeight)-Math.max(0,b.top));
          values.push({text:el.textContent.trim(),reachable:el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})&&x>0&&y>0,fullyInViewport:b.left>=-1&&b.right<=innerWidth+1&&b.top>=-1&&b.bottom<=innerHeight+1,scrollY});
        }
        window.scrollTo({top:0,behavior:'instant'});
        await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
        return values;
      })()`);
      if (width === 1440 && name !== 'minimal') {
        const layout = await send('Page.getLayoutMetrics');
        const size = layout.cssContentSize;
        const shot = await send('Page.captureScreenshot', { format:'png', captureBeyondViewport:true, clip:{x:0,y:0,width:size.width,height:size.height,scale:1} });
        fs.writeFileSync(path.join(out, `${name}.1440x900.full-page.png`), Buffer.from(shot.data,'base64'));
        await evaluate(`window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'})`);
        await evaluate(`new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))`);
        const bottom = await send('Page.captureScreenshot', { format:'png', captureBeyondViewport:false });
        fs.writeFileSync(path.join(out, `${name}.1440x900.bottom.png`), Buffer.from(bottom.data,'base64'));
      }
      results.observations.push({ name, width, height, artifactSha256:createHash('sha256').update(fs.readFileSync(artifact)).digest('hex'), gateMetrics, measured });
      save();
      console.log(name, width, 'raw document', measured.rawScrollHeight, 'gate',gateMetrics.scrollHeight,'missing',measured.missingCardText.length);
    }
  }
} finally {
  await browser.close();
  save();
}
