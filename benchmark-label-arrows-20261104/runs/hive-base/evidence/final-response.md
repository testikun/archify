[Open the architecture diagram](output/hive-task-path.html) · [Source JSON](output/hive-task-path.json) · [Source evidence and uncertainties](output/source-notes.md)

The browser reaches CLI processes through Hive’s PTY runtime. The orchestrator dispatches work using `team send`; live output returns over WebSockets, while structured progress and final reports pass through authenticated team APIs and persistent outboxes.

The diagram covers stopped-worker queuing and delayed result delivery, and distinguishes `.hive/tasks.md` from executable dispatches. Archify checks passed; laptop light-theme and larger dark-theme captures were visually reviewed. Application and Archify source remain unchanged.