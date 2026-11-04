[Open the architecture diagram](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/hive-candidate/workspace/output/hive-task-path.html) · [Source JSON](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/hive-candidate/workspace/output/candidate.json)

The orchestrator dispatches work through `team send`, which reaches the worker’s PTY stdin. Progress is recorded without waking the orchestrator; final reports are persisted and forwarded through a durable outbox.

The diagram includes source references, process boundaries, and delivery limitations. Automated checks passed, light/dark laptop captures were visually reviewed, and application source remains unchanged.