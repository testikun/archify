import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
process.chdir(path.resolve(import.meta.dirname, '../implementation'));
// Reuse the original evidence recipe; the original log and script stay immutable.
execFileSync(process.execPath, ['../implementation-evidence/refresh-artifacts.mjs'], {stdio:'inherit'});
// Preserve hand-authored diagram geometry. Only refresh the changed Viewer rule.
const original = '.diagram-container[data-detail-level="map"] svg [data-detail="context"],';
const replacement = '.diagram-container[data-detail-level="map"] svg [data-detail="context"]:not([data-label-direction]),';
for (const file of execFileSync('git', ['ls-files', 'examples/*.html', 'archify/examples/*.html'], {encoding:'utf8'}).trim().split('\n')) {
  const source = fs.readFileSync(file, 'utf8');
  if (source.includes(original)) fs.writeFileSync(file, source.replaceAll(original, replacement));
}
