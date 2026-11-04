[Open the architecture diagram](output/squad-coordination.html) · [Source JSON](output/squad-coordination.json)

Squad coordinates independent manager and worker agents through CLI calls backed by shared SQLite task/message state—not a manager daemon. Task completion persists a summary but sends no automatic notification; the manager must inspect task state or receive an explicitly sent message.

Source references and implementation caveats are embedded. Automated checks passed, light/dark screenshots were visually reviewed, and application source remains unchanged.