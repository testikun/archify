[Open the MCO review architecture diagram](/benchmark/runs/mco-base/workspace/output/mco-review.html) · [Source JSON](/benchmark/runs/mco-base/workspace/output/mco-review.json)

CLI and MCP requests converge on the shared invocation runtime, which runs selected providers concurrently and returns their individual results in selection order—without default synthesis.

The diagram includes pinned source references, process/filesystem boundaries, and explicit uncertainties about provider internals. Archify checks passed; light/dark captures were visually inspected. Application and Archify source remain unchanged.