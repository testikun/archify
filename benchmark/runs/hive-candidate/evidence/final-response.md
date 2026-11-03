[Open the Hive architecture diagram](/benchmark/runs/hive-candidate/workspace/output/hive-task-roundtrip.html)

Browser input reaches the orchestrator through WebSocket/PTY transport; authenticated `team send` commands create dispatches and inject tasks into worker CLIs. Terminal output streams back live, while explicit reports persist in SQLite and return through the orchestrator’s delivery outbox.

- [Source JSON](/benchmark/runs/hive-candidate/workspace/output/candidate.json)
- [Source trace and uncertainties](/benchmark/runs/hive-candidate/workspace/output/source-notes.md)

The diagram distinguishes non-waking progress, status updates, and completion reports. Archify validation and browser checks pass; laptop layout visually reviewed. Application and Archify source remain unchanged.