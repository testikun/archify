[Open the architecture diagram](/benchmark/runs/squad-candidate/workspace/output/squad-coordination.html) · [Source JSON](/benchmark/runs/squad-candidate/workspace/output/candidate.json)

Squad coordinates external manager and worker terminals through CLI calls sharing SQLite state—not an autonomous scheduler. Task creation atomically persists an assignment and inbox message; receiving doesn’t acknowledge the task, and completion doesn’t automatically notify the manager.

The diagram retains pinned source references and implementation caveats. Automated checks passed; laptop-size light/dark captures were visually reviewed. Application source remains unchanged.