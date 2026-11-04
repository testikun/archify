[View the architecture diagram](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/openpi-candidate/workspace/output/openpi-subagent.html) · [Source JSON](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/openpi-candidate/workspace/output/openpi-subagent.architecture.json)

OpenPI delegates through `subagent_spawn` into a separate **in-process Pi session**, not an OS-isolated worker. The manager exposes status through `subagent_check`; results return through explicit `subagent_wait` or automatic follow-up delivery that wakes the parent.

Source references and uncertainties are embedded. Archify validation passed; laptop-sized light/dark captures were visually reviewed. Application and Archify source remain unchanged.