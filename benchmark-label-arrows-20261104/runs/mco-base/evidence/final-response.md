Created [MCO review architecture diagram](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/mco-base/workspace/output/mco-review.html) and [source JSON](/evidence/issue-1139/benchmark-label-arrows-20261104/runs/mco-base/workspace/output/mco-review.json).

CLI and MCP requests share an invocation engine that runs selected providers concurrently and returns individual outcomes in declaration order—not a synthesized review. The diagram includes pinned source references, the subprocess boundary, and explicit uncertainties about provider internals.

Scope: default parallel/shim path. Project and Archify source remain unchanged.