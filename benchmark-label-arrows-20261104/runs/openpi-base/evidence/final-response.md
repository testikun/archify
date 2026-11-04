[Open the architecture diagram](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/openpi-base/workspace/output/openpi-subagents.html) · [Source JSON](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/openpi-base/workspace/output/openpi-subagents.json)

OpenPI accepts delegation through `subagent_spawn`, creates an independent **in-process Pi session**, and folds its events into manager-owned status snapshots. The caller can check status, explicitly wait for results, or receive an automatic one-shot follow-up.

The diagram includes pinned source references and distinguishes session independence from optional filesystem isolation. It starts at the parent tool-call boundary; upstream Pi internals and unproven durability guarantees are explicitly excluded.

Archify validation and browser checks passed. Application and Archify source remain unchanged.