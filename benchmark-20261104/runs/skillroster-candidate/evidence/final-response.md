[Open the SkillRoster architecture diagram](/evidence/issue-1139/benchmark-20261104/runs/skillroster-candidate/workspace/output/skillroster-architecture.html) · [Source JSON](/evidence/issue-1139/benchmark-20261104/runs/skillroster-candidate/workspace/output/candidate.json)

Discovery and planning leave Skill files unchanged, but persist SkillRoster-owned state. Apply crosses the guarded filesystem boundary with journaling and verification; undo uses recorded, drift-checked compensations—not an unconditional restore.

The diagram retains pinned source references and explains the separate SQLite/journal commits and recovery limitations. Application source remains unchanged.