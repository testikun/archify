[Open the SkillRoster architecture diagram](/benchmark/runs/skillroster-base/workspace/output/skillroster-architecture.html) · [Source JSON](/benchmark/runs/skillroster-base/workspace/output/candidate.json)

Scan and Plan persist local metadata without changing Skill files. Explicit Apply/Undo commands cross the guarded mutation boundary; Undo reverses journaled compensations rather than replanning.

Source references and safety conditions are embedded in the diagram. Automated checks and visual review passed; application source remains unchanged.