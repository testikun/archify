[Open the Hive task-path architecture diagram](/evidence/issue-1139/benchmark-20261104/runs/hive-base/workspace/output/hive-task-path.html)

[Source JSON](/evidence/issue-1139/benchmark-20261104/runs/hive-base/workspace/output/candidate.json) · [Source evidence and uncertainties](/evidence/issue-1139/benchmark-20261104/runs/hive-base/workspace/output/source-notes.md)

The orchestrator explicitly delegates through authenticated `team send`; Hive delivers the task into a worker CLI’s PTY stdin. Silent progress is stored for team reads, legacy status is injected into the orchestrator, and completion returns through a durable report outbox.

Archify checks passed and laptop captures were visually reviewed. Application source remains unchanged.