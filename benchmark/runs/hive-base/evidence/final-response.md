[Open the architecture diagram](</benchmark/runs/hive-base/workspace/output/hive-task-path.html>) · [Source JSON](</benchmark/runs/hive-base/workspace/output/hive-task-path.json>)

The path is explicit: browser input reaches the orchestrator CLI, `team send` creates a dispatch, and Hive injects the task into a worker’s PTY. Results return through `team report` and durable forwarding; recorded progress and live terminal output are distinct channels.

Includes pinned source references, boundaries, queueing conditions, and uncertainty notes. Archify checks passed; desktop captures reviewed. Application and Archify source remain unchanged.