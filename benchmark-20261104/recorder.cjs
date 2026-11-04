// External benchmark recorder, loaded before the CLI main module. It does not
// change Archify code, candidate bytes, arguments, output or exit status.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const evidence = process.env.ARCHIFY_BENCH_EVIDENCE;
const output = process.env.ARCHIFY_BENCH_OUTPUT;
if (evidence && output) {
  for (const arg of process.argv.slice(2)) {
    const source = path.resolve(arg);
    if (!source.startsWith(output + path.sep) || !source.endsWith('.json')) continue;
    try {
      const bytes = fs.readFileSync(source);
      const value = JSON.parse(bytes);
      if (!value.diagram_type || !value.schema_version) continue;
      const sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
      fs.mkdirSync(path.join(evidence, 'snapshots'), { recursive: true });
      fs.writeFileSync(path.join(evidence, 'snapshots', sha256 + '.json'), bytes);
      fs.appendFileSync(path.join(evidence, 'cli-inputs.jsonl'), JSON.stringify({
        at: new Date().toISOString(), pid: process.pid, argv: process.argv,
        source, sha256, snapshot: 'snapshots/' + sha256 + '.json',
      }) + '\n');
    } catch { /* A missing or invalid input is reported by the unmodified CLI. */ }
  }
}

