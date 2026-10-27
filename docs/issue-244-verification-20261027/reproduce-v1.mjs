import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync, execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';

const evidence = path.dirname(fileURLToPath(import.meta.url));
const checkout = path.resolve(evidence, '../archify-244-v1');
const sha = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: checkout, encoding: 'utf8' }).trim();
assert.equal(sha, '2bfb47132c057195d8dddb3e25ae966dd7c7a72e');
const output = path.join(evidence, 'v1-original');
fs.mkdirSync(output, { recursive: true });
const runs = [];
for (const number of [243, 244]) {
  const input = path.join(evidence, `issue-${number}.lifecycle.json`);
  for (const command of ['validate', 'deliver']) {
    const args = [path.join(checkout, 'archify/bin/archify.mjs'), command, 'lifecycle', input];
    if (command === 'deliver') args.push(path.join(output, `issue-${number}.html`));
    args.push('--quality', 'showcase', '--json');
    const result = spawnSync(process.execPath, args, { cwd: path.join(checkout, 'archify'), encoding: 'utf8' });
    fs.writeFileSync(path.join(output, `${number}-${command}.stdout.json`), result.stdout || '');
    fs.writeFileSync(path.join(output, `${number}-${command}.stderr.log`), result.stderr || '');
    runs.push({ number, command, executable: process.execPath, args, exitCode: result.status });
    console.log(number, command, 'exit=' + result.status);
  }
}
fs.writeFileSync(path.join(output, 'generation-runs.json'), JSON.stringify({ sha, node: process.version, cwd: path.join(checkout, 'archify'), runs }, null, 2) + '\n');
