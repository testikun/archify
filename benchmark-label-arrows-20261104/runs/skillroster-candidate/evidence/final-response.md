[View the architecture diagram](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/skillroster-candidate/workspace/output/skillroster-architecture.html) · [Source JSON](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/skillroster-candidate/workspace/output/candidate.json)

Inspection and planning preserve installed Skill contents while persisting local state. Explicit Apply/Undo commands cross validation and handle-bound filesystem gates, using durable journals and compensations rather than a single filesystem/SQLite transaction.

Source references are attached to components. Application source remains unchanged.