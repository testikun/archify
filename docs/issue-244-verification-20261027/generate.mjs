import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync, execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';

const evidence = path.dirname(fileURLToPath(import.meta.url));
const checkout = process.argv[2];
assert.ok(checkout, 'Usage: node generate.mjs /absolute/dev-checkout');
const testedSha = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: checkout, encoding: 'utf8' }).trim();
assert.equal(testedSha, JSON.parse(fs.readFileSync(path.join(evidence, 'remote-dev.json'))).sha);
const cli = path.join(checkout, 'archify/bin/archify.mjs');
const runs = [];
function invoke(name, args) {
  const result = spawnSync(process.execPath, [cli, ...args], { cwd: checkout, encoding: 'utf8' });
  fs.writeFileSync(path.join(evidence, name + '.stdout.json'), result.stdout || '');
  fs.writeFileSync(path.join(evidence, name + '.stderr.log'), result.stderr || '');
  runs.push({ name, executable: process.execPath, args: [cli, ...args], cwd: checkout, exitCode: result.status });
  console.log(name, 'exit=' + result.status);
}
for (const number of [243, 244]) {
  const input = path.join(evidence, `issue-${number}.lifecycle.json`);
  invoke(`${number}-original-validate`, ['validate', 'lifecycle', input, '--quality', 'showcase', '--json']);
  invoke(`${number}-original-deliver`, ['deliver', 'lifecycle', input, path.join(evidence, `issue-${number}.original.html`), '--quality', 'showcase', '--json']);
  const original = JSON.parse(fs.readFileSync(input));
  // Preserve every authored state and transition. This is a v3 control, not an
  // identical reproduction: v3 has no lanes, columns, explicit viewBox or route.
  // #244's only actual edge is reviewing -> blocked. No implied phase edges are added.
  const converted = {
    schema_version: 3, diagram_type: 'lifecycle',
    meta: { title: original.meta.title, quality_profile: original.meta.quality_profile, output: `issue-${number}.v3.html` },
    mainPath: number === 243 ? ['a', 'b'] : ['reviewing', 'blocked'],
    states: original.states.map(({ lane, col, ...state }) => state),
    transitions: original.transitions.map(({ route, ...transition }) => transition),
  };
  const convertedInput = path.join(evidence, `issue-${number}.v3.lifecycle.json`);
  fs.writeFileSync(convertedInput, JSON.stringify(converted, null, 2) + '\n');
  invoke(`${number}-v3-validate`, ['validate', 'lifecycle', convertedInput, '--quality', 'showcase', '--json']);
  invoke(`${number}-v3-deliver`, ['deliver', 'lifecycle', convertedInput, path.join(evidence, `issue-${number}.v3.html`), '--quality', 'showcase', '--json']);
  if (number === 244) {
    const samePhaseOrder = { ...converted, mainPath: ['queued', 'planning', 'executing', 'reviewing', 'completed'] };
    const phaseInput = path.join(evidence, 'issue-244.v3-original-phase-order.lifecycle.json');
    fs.writeFileSync(phaseInput, JSON.stringify(samePhaseOrder, null, 2) + '\n');
    invoke('244-v3-original-phase-order-validate', ['validate', 'lifecycle', phaseInput, '--quality', 'showcase', '--json']);
  }
}
fs.writeFileSync(path.join(evidence, 'generation-runs.json'), JSON.stringify({ testedSha, runs }, null, 2) + '\n');
