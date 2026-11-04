[View the MCO review architecture diagram](/evidence/issue-1139/benchmark-20261104/runs/mco-candidate/workspace/output/mco-review.html) · [Source JSON](/evidence/issue-1139/benchmark-20261104/runs/mco-candidate/workspace/output/candidate.json)

MCO validates one request, runs selected provider/model invocations concurrently through adapters, and returns individual results in selection order. Provider failures remain separate; the default path does not synthesize answers.

The diagram covers the default CLI/shim path, retains source references, and marks provider internals as outside the available evidence. Archify checks passed, the laptop layout was visually inspected, and application source remains unchanged.