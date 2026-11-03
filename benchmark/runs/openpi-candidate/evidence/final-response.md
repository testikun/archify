[OpenPI delegation architecture diagram](/benchmark/runs/openpi-candidate/workspace/output/openpi-subagents.html) · [Source JSON](/benchmark/runs/openpi-candidate/workspace/output/openpi-subagents.json)

OpenPI accepts delegation through `subagent_spawn`, starts a separate **in-process Pi session**, and returns its ID. The caller reads status through check/list, retrieves results through explicit wait, or receives an automatic completion follow-up that wakes the parent.

The diagram retains source references and flags uncertainty around persistence and termination. Automated checks passed; laptop-size light/dark captures were visually inspected. Project and Archify source remain unchanged.