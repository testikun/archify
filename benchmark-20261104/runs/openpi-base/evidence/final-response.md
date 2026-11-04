[OpenPI delegation architecture](/evidence/issue-1139/benchmark-20261104/runs/openpi-base/workspace/output/openpi-delegation.html) · [Source JSON](/evidence/issue-1139/benchmark-20261104/runs/openpi-base/workspace/output/candidate.json)

`subagent_spawn` returns a handle to an independent, **in-process Pi session**. The manager exposes status snapshots; results reach the parent through explicit `subagent_wait` or an automatic completion follow-up.

The diagram retains source references and distinguishes session independence from filesystem isolation and uncertain persistence guarantees. Project and Archify source remain unchanged.