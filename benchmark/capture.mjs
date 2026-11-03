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
  if (cached.get(row.run_id)?.artifactSha256 === artifactSha256) {
    results.push(cached.get(row.run_id));
    continue;
  }
  const browser = new ChromeVisualBrowser(chrome);
  const out = path.join(root, 'captures', row.run_id);
  fs.mkdirSync(out, { recursive: true });
  try {
    const metrics = await browser.inspect({ artifactPath: row.html[0], width: 1440, height: 900, theme: 'light' });
    const session = await browser.sessionPromise;
    const page = await browser.cdp.send('Page.getLayoutMetrics', {}, session);
    for (const [name, height] of [['viewport', 900], ['fullpage', Math.ceil(page.cssContentSize.height)]]) {
      const shot = await browser.cdp.send('Page.captureScreenshot', {
        format: 'png', captureBeyondViewport: true, fromSurface: true,
        clip: { x: 0, y: 0, width: 1440, height, scale: 1 },
      }, session);
      fs.writeFileSync(path.join(out, `${name}.light.png`), Buffer.from(shot.data, 'base64'));
    }
    results.push({ run_id: row.run_id, artifact: row.html[0], artifactSha256, metrics, contentHeight: page.cssContentSize.height });
    console.log(row.run_id, page.cssContentSize.height);
  } finally { await browser.close(); }
}
fs.mkdirSync(path.dirname(metricsPath), { recursive: true });
fs.writeFileSync(metricsPath, JSON.stringify(results, null, 2) + '\n');
