# SkillRoster architecture review

- Deliverable: `skillroster-architecture.html`; editable Archify source: `candidate.json`.
- Repository: selected checkout at `21d14c7cff25c66a016562e238e62d0538eb696f`; component source references are embedded in the diagram's semantic passports and JSON.
- Scope: the local discovery → declarative planning → explicit Apply → Receipt-based Undo path. Logical responsibilities are parts of one CLI, not deployed services. Setup and lifecycle operations appear only where needed to explain safety/recovery.
- Key distinction: inspection and planning do write SkillRoster-owned control state. They do not execute changes to Agent/Skill content. Approved mutable roots, not discovery coverage, define mutation authority.
- Consent qualification: interactive Apply/Undo prompt; JSON mode depends on caller-obtained consent, not a verified approval token (`src/app.rs:345–390`, `src/app.rs:600–605`).
- Uncertainty: this source-only investigation establishes the implemented filesystem checks, synchronization and recovery paths, not support or power-loss guarantees on a particular deployed filesystem. No live Skills or application services were invoked.

## Validation and perceptual review

- Final Archify showcase validation, delivery, strict provenance and Chrome browser checks pass; receipts are in `review-2/`.
- Final screenshot capture checks pass; evidence is in `visual-final/`.
- Personally inspected final 1440×900 light and dark captures: complete topology fits the laptop viewport; relationship labels and arrowheads remain visible; no visible clipping, node collisions or crossing ambiguity. Supporting cards continue below the diagram via ordinary page scroll. Larger captures were generated but not personally inspected.
- Final artifact SHA-256: `e44dd0e9e0a1f3dd4e8c3c51c883ab9b60dd4f0347a98cb1399867e2d272c72f`.

## Ablation experiment

The initial passing diagram enclosed the Apply/Undo gate and execution engine in an additional “Explicit mutation commands” frame. Removed that frame, keeping all components, relationships, conditions and source evidence. The named gate, conditional execution arrow, anchored I/O layer and retained no-content-mutation inspection boundary still convey the same authorization/persistence separation. The simplified version passes all gates and remains clear in both laptop captures, so the redundant frame stays removed. `ablation-baseline.json` retains the original candidate; the only other candidate change extends the preparation citation to include its digest construction.
