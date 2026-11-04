[Open the SkillRoster architecture diagram](/evidence/issue-1139/benchmark-20261104/runs/skillroster-base/workspace/output/skillroster-architecture.html) · [Source JSON](/evidence/issue-1139/benchmark-20261104/runs/skillroster-base/workspace/output/candidate.json)

Discovery and planning preserve Skill content but persist local state. Explicit Apply crosses into guarded, journaled filesystem operations; Undo reverses receipt-recorded changes through drift-checked compensations.

The diagram includes pinned source references and distinguishes SQLite finalization from filesystem durability—without claiming cross-store atomicity. Archify checks pass; laptop screenshots were reviewed in both themes. Application and Archify source remain unchanged.