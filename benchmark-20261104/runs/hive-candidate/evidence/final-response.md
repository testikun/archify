[Open the Hive architecture diagram](/evidence/issue-1139/benchmark-20261104/runs/hive-candidate/workspace/output/hive-task-path.html)

[Source JSON](/evidence/issue-1139/benchmark-20261104/runs/hive-candidate/workspace/output/candidate.json) · [Source-backed explanation and uncertainties](/evidence/issue-1139/benchmark-20261104/runs/hive-candidate/workspace/output/README.md)

The browser reaches CLI processes through WebSockets and PTYs; the orchestrator delegates through authenticated `team send` calls and stdin injection. Terminal output streams back independently, while explicit `team report` settles the dispatch and queues the result for the orchestrator.

Archify checks passed and rendered captures were visually reviewed. Application and Archify source remain unchanged.