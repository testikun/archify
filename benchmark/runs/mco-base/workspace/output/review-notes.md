# MCO review architecture — review notes

- Artifact: `mco-review.html`; source: `mco-review.json`.
- Repository: `https://github.com/mco-org/mco`, revision `3cfce130362dbcc2aedda6170d1a31e39cf67d3e`.
- Scope: normal CLI `review` and MCP `mco_review`, default shim transport, no chain, debate or synthesis. Node source references retain the exact source ranges used for each responsibility.
- Latest finalization: `review-2/mco-review.finalize.json`. Validation, delivery, strict artifact checks and automated browser checks passed.
- Perceptual review: inspected the finalized 1440×900 light and 2048×1320 dark captures under `visual-check/`. Main labels, request/reply arrows and the process/filesystem separation are legible; no visible node or label clipping. This human-style image inspection is separate from the automated browser receipt.
- Simplification experiment: removed the redundant “One request → separate answers” summary card. Provider identity, ordering and no-default-synthesis behavior remain in the collection node and its sourced explanation. Re-finalization passed, so the card stays removed. Also made adapter replies explicit without adding another component or service abstraction.
- Limits: read-only is mapped to provider-specific permissions; this checkout does not prove each executable's isolation guarantees or its model/network/auth internals. These are stated as limits, not invented infrastructure.
- No provider was executed, no dependency was installed, and the update check was disabled to avoid live services. Project and Archify source were not modified.
