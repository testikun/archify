import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const id = process.argv[2] || new Date().toISOString().replace(/[:.]/g, '-');
if (!/^[\w-]+$/.test(id)) throw new Error('Use a simple unique run directory name.');
const run = path.join(root, 'runs', id);
if (fs.existsSync(run)) throw new Error('Run directory exists; use a fresh name to preserve receipts.');
for (const dir of ['logs', 'artifacts', 'browser', 'tmp', 'inputs']) fs.mkdirSync(path.join(run, dir), { recursive: true });
const cli = path.join(root, 'source/archify/bin/archify.mjs');
const env = { ...process.env, TMPDIR: path.join(run, 'tmp') };
const records = [];
const digest = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const manifest = { startedAt: new Date().toISOString(), source: JSON.parse(fs.readFileSync(path.join(root, 'evidence/source.json'))), node: process.version, executable: process.execPath, platform: process.platform, arch: process.arch, osRelease: os.release(), commands: records };
const save = () => fs.writeFileSync(path.join(run, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
function invoke(name, stage, args) {
  const started = Date.now();
  const result = spawnSync(process.execPath, [cli, ...args], { cwd: root, env, encoding: 'utf8', timeout: 180000, maxBuffer: 20 * 1024 * 1024 });
  fs.writeFileSync(path.join(run, 'logs', `${name}.${stage}.stdout.json`), result.stdout || '');
  fs.writeFileSync(path.join(run, 'logs', `${name}.${stage}.stderr.txt`), result.stderr || '');
  records.push({ name, stage, command: [process.execPath, cli, ...args], cwd: root, exitCode: result.status, signal: result.signal, error: result.error?.message, elapsedMs: Date.now() - started });
  save();
  console.log(`${name}: ${stage} exit=${result.status}`);
  return result.status === 0;
}
const cases = process.argv.slice(3);
for (const name of cases.length ? cases : ['minimal', 'public-deployment', 'synthetic-11-cards', 'synthetic-11-no-cards', 'synthetic-11-all-main', 'synthetic-tall', 'invalid-viewbox', 'invalid-yoffset']) {
  if (!/^[\w-]+$/.test(name)) throw new Error('Invalid input name.');
  const input = path.join(run, 'inputs', `${name}.json`);
  const artifact = path.join(run, 'artifacts', `${name}.html`);
  fs.copyFileSync(path.join(root, 'inputs', `${name}.json`), input);
  records.push({ name, input, inputSha256: digest(input) });
  if (!invoke(name, 'validate', ['validate', 'lifecycle', input, '--quality', 'showcase', '--json'])) continue;
  if (!invoke(name, 'deliver', ['deliver', 'lifecycle', input, artifact, '--quality', 'showcase', '--json'])) continue;
  invoke(name, 'visual-check', ['visual-check', artifact, '--require-provenance', '--out-dir', path.join(run, 'browser', name), '--json']);
}
manifest.finishedAt = new Date().toISOString();
save();
console.log(`Saved ${run}`);
