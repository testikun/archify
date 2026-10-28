import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'inputs');
fs.mkdirSync(out, { recursive: true });
const write = (name, value) => fs.writeFileSync(path.join(out, `${name}.json`), JSON.stringify(value, null, 2) + '\n');
const meta = (title, output) => ({ title, output: `${output}.html`, quality_profile: 'showcase' });
write('minimal', {
  schema_version: 3, diagram_type: 'lifecycle', meta: meta('Minimal Lifecycle', 'minimal'),
  mainPath: ['queued', 'done'],
  states: [{ id: 'queued', type: 'start', label: 'Queued' }, { id: 'done', type: 'success', label: 'Done' }],
  transitions: [{ from: 'queued', to: 'done', label: 'finish' }],
});
// Public project example: byte-for-byte copy, with output location overridden only by CLI.
fs.copyFileSync(path.join(root, 'source/archify/examples/deployment-release.lifecycle.json'), path.join(out, 'public-deployment.json'));

// Synthetic only. Its 11/11/3 counts do not reconstruct the reporter's private JSON.
const phases = ['queued', 'checked', 'ready', 'running', 'done', 'audit', 'archive', 'retained', 'expired', 'purging', 'removed'];
const base = {
  schema_version: 3, diagram_type: 'lifecycle', meta: meta('Synthetic Retention Lifecycle', 'synthetic-11-cards'),
  mainPath: phases.slice(0, 5),
  states: phases.map((id, i) => ({ id, type: i === 0 ? 'start' : i === 10 ? 'success' : 'active', label: id[0].toUpperCase() + id.slice(1), sublabel: 'record phase' })),
  transitions: phases.slice(0, -1).map((from, i) => ({ id: `t${i}`, from, to: phases[i + 1], label: 'advance' })).concat([{ id: 'restart', from: 'removed', to: 'queued', label: 'new cycle' }]),
  cards: [
    { dot: 'cyan', title: 'Primary path', items: ['Queued through Done is the primary reading path.', 'Every record phase remains in the diagram.'] },
    { dot: 'amber', title: 'Retention detail', items: ['Audit, archive and expiry are secondary phases.', 'The automatic layout places them below the primary path.'] },
    { dot: 'rose', title: 'Cycle boundary', items: ['Removed starts a new cycle through the explicit return.', 'This is a synthetic investigation fixture.'] },
  ],
};
write('synthetic-11-cards', base);
write('synthetic-11-no-cards', { ...base, cards: [] });
write('synthetic-11-all-main', { ...base, mainPath: phases });
// Dedicated tall control: no return shortcut that would reduce graph distance.
write('synthetic-tall', {
  ...base,
  meta: meta('Synthetic Tall Lifecycle', 'synthetic-tall'),
  mainPath: phases.slice(0, 2),
  transitions: base.transitions.slice(0, -1),
  cards: [],
});
// Invalid current-contract probes: isolate retired fields rather than run a false height sweep.
const minimal = JSON.parse(fs.readFileSync(path.join(out, 'minimal.json')));
write('invalid-viewbox', { ...minimal, meta: { ...minimal.meta, viewBox: [1075, 585] } });
write('invalid-yoffset', { ...minimal, states: minimal.states.map((state, i) => i ? state : { ...state, yOffset: 20 }) });
