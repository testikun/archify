[Open the MCO review architecture diagram](/evidence/issue-1139/benchmark-20261104/runs/mco-base/workspace/output/mco-review.html) · [Source JSON](/evidence/issue-1139/benchmark-20261104/runs/mco-base/workspace/output/mco-review.architecture.json)

MCO validates the request, runs selected provider invocations concurrently through adapters, and returns separate results in declaration order—not a merged answer. The diagram includes source references, streaming output, failure handling, and the subprocess boundary.

Scope: default CLI/shim path; optional transports and coordination modes are noted, while provider internals remain explicitly unknown. Automated checks passed, laptop screenshots were visually reviewed, and application source is unchanged.