[Open the Squad coordination diagram](/benchmark/runs/squad-base/workspace/output/squad-coordination.html) · [Source JSON](/benchmark/runs/squad-base/workspace/output/candidate.json)

Manager and worker coordinate through independent CLI invocations backed by shared SQLite state. Assignment atomically creates a task and message; receiving that message does **not** acknowledge the task. Completion persists the result without automatically notifying the manager.

The diagram includes pinned source references and implementation caveats. Automated checks passed, laptop-size light/dark views were visually reviewed, and application source remains unchanged.