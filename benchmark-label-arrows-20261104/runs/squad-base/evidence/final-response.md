[Open the architecture diagram](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/squad-base/workspace/output/squad-coordination.html) · [Source JSON](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/squad-base/workspace/output/candidate.json)

Squad coordinates manager and worker through CLI invocations sharing SQLite task/message state—not a running manager service. Task creation atomically persists an assignment and notification; completion stores results but requires task-list inspection or a separate message to inform the manager.

The diagram includes pinned source references and implementation limits. Archify checks passed, laptop light/dark layouts were visually reviewed, and application source remains unchanged.