[Open the architecture diagram](/evidence/issue-1139/benchmark-20261104/runs/openpi-candidate/workspace/output/openpi-subagent.html) · [Source JSON](/evidence/issue-1139/benchmark-20261104/runs/openpi-candidate/workspace/output/openpi-subagent.architecture.json)

OpenPI accepts delegation through `subagent_spawn`, starts a separate Pi session **within the same process**, and returns its ID. Callers can query status, explicitly await results, or receive an automatic follow-up that wakes the parent.

The diagram includes pinned source references, authority boundaries, and persistence uncertainties. Archify checks passed; laptop-size light/dark renders were visually inspected. Application source remains unchanged.