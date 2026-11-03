[OpenPI delegation architecture diagram](/benchmark/runs/openpi-base/workspace/output/openpi-delegation.html) · [Source JSON](/benchmark/runs/openpi-base/workspace/output/openpi-delegation.json)

The parent model delegates through OpenPI’s tools to a separate **in-process Pi session**, not a separate process. The manager exposes status through check/wait tools; unconsumed results return through a deduplicated follow-up that wakes the parent.

Source references and uncertainties are embedded in the diagram. Validation and laptop-screen visual review passed; application source remains unchanged.