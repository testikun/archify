[Open the SkillRoster architecture diagram](/benchmark/runs/skillroster-candidate/workspace/output/skillroster-architecture.html) · [Source JSON](/benchmark/runs/skillroster-candidate/workspace/output/candidate.json)

Inspection and planning persist control state but do not mutate Skill packages. Explicit Apply/Undo commands cross into the locked, anchored change engine; Undo uses journaled, fingerprint-guarded compensation—not a single atomic filesystem/database transaction.

Source references are retained in the diagram. Archify checks passed, laptop-sized light/dark views were visually reviewed, and application source remains unchanged.