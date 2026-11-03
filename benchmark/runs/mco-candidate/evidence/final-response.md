[Open the MCO review architecture diagram](/benchmark/runs/mco-candidate/workspace/output/mco-review.html) · [Source JSON](/benchmark/runs/mco-candidate/workspace/output/candidate.json)

MCO validates one request, runs selected providers through bounded parallel workers and adapters, then returns each provider’s answer and status in selection order—not a synthesized consensus.

The diagram includes pinned source references, subprocess/filesystem boundaries, and explicit uncertainty about provider internals. Archify checks pass; laptop light/dark renders were visually inspected. Application source remains unchanged.