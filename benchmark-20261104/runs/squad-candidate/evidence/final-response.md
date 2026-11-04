[Open the architecture diagram](/evidence/issue-1139/benchmark-20261104/runs/squad-candidate/workspace/output/squad-coordination.html) · [Source JSON](/evidence/issue-1139/benchmark-20261104/runs/squad-candidate/workspace/output/candidate.json)

Squad coordinates manager and worker through CLI invocations sharing local SQLite state—not a manager daemon. Creating a task atomically persists its assignment message; receiving, acknowledging, and completing are separate operations, and completion sends no automatic reply.

The diagram retains source references and implementation limits. Automated checks passed; laptop-sized light/dark captures were visually inspected. Application and Archify source remain unchanged.