# Archify #244: latest-dev verification, 2026-11-02

**No false relationship reproduced with graph-preserving v3 controls at `dev@63c9263e84bd3993cab8e09b3d69888857858635` (`3.2.1-dev.1`). No additional rail-hiding patch is indicated.** I recommend closing #244 as resolved for the currently supported Lifecycle implementation, with the compatibility distinction below recorded.

The historical v2.16.0 defect is real. The [previous pinned reproduction](https://github.com/testikun/archify/blob/db4095168e2a2591467b05dc065fc2b22fbe62a5/docs/issue-244-verification-20261027/README.md) supplies the historical control; it was not rerun in this session. The current renderer no longer draws the old primary decorative rail. #253's earlier hiding fix is already merged.

## Compatibility and topology

Both unchanged original schema-v1 inputs are rejected by current `validate` and `deliver` (exit 1). This is **not an unchanged-input compatibility pass**.

The two v3 controls retain every original state, authored transition and label. #243 uses `mainPath: ["a", "b"]`. #244 uses `mainPath: ["reviewing", "blocked"]`, its only real relationship; Queued, Planning, Executing and Completed remain disconnected. This changes layout and the initial-marker owner. Keeping the old five-phase mainPath without inventing edges is rejected with four `lifecycle/main-path-gap` diagnostics. Old-format support or old-layout preservation would be a separate migration/compatibility decision.

## Fresh results

| Check | Result |
| --- | --- |
| v3 showcase validation and delivery | Both cases pass, 9/9 checks each |
| Browser interaction matrix | 38/38, plus four READ baselines |
| Canonical SVG export | 38/38 byte-identical to the corresponding READ export |
| Exit after export | 38/38 restore READ state, geometry, opacity and panel visibility |
| Independent exit without exporting | 38/38 restore READ |
| Existing focused tests | 25 passed, 0 failed, 0 skipped |

The matrix covers both inputs in dark/light: native mouse and Tab node preview, relationship preview, committed focus, upstream/downstream Authored Reachability, cold focus/reach URLs, and isolated Planning for #244. Actual SVG elements contain no old rail and no unowned marker arrow. Deduplicated edge identities match authored transitions. #244 Reach contains only Reviewing, Blocked and one edge; the four unrelated nodes dim to 0.09 without a line crossing them. Planning has no reachable neighbors. Browser error and external-resource records are empty.

Environment: real headless Chrome 156.0.8078.74, Node 20.20.2, Darwin 25.6.0 arm64, 1440×900, Classic, dark/light, reduced motion. Fonts and Viewer layout were allowed to settle; semantic state attributes were not injected. The remote dev SHA was checked again after testing and remained unchanged.

## Evidence

- [Machine-readable summary and artifact hashes](verification-summary.json), [generation commands and exits](generation-runs.json), [generation log](generation.log), [focused test log](focused-tests.log).
- [Browser observations](browser/observations.json), [independent exit observations](direct-exit/observations.json), [browser log](browser-run.log), [exit log](direct-exit-run.log).
- #244: [READ](browser/244-dark-read.png), [hover](browser/244-dark-node-hover.png), [committed focus](browser/244-dark-committed-focus.png), [Reach](browser/244-dark-reach-downstream.png), [direct exit](direct-exit/244-dark-reach-downstream-restored.png).
- #243: [Reach](browser/243-light-reach-downstream.png).
- Generated HTML: [#244](issue-244.v3.html), [#243](issue-243.v3.html). Download before opening locally.
- Inputs, CLI receipts, representative canonical SVGs and replay scripts are in this directory. `manifest.json` binds all other published files by SHA-256 and byte count.

The original/v3 JSON and replay scripts are byte-identical to the previous verification. Only machine-local path prefixes in published logs/receipts are redacted to `$DEV` and `$EVIDENCE`; input JSON, HTML, SVG and PNG bytes are unchanged. HTML hashes still match delivery receipts.

To replay, check out the exact dev SHA and install its root and `archify/` dependencies. Save this directory to `$EVIDENCE` and set `$DEV` to that checkout:

```sh
cd "$EVIDENCE"
node generate.mjs "$DEV"
ARCHIFY_CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' node verify-browser.mjs "$DEV"
ARCHIFY_CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' ARCHIFY_VERIFY_DIRECT_EXIT=1 node verify-browser.mjs "$DEV"
cd "$DEV"
npm run test:focus -- test/lifecycle-layout.test.mjs test/authored-reachability.test.mjs test/relationship-lens.test.mjs
```

AI disclosure: Codex performed the verification, representative screenshot inspection, evidence preparation and drafting under @testikun's direction. This is Agent-operated browser evidence, not human acceptance or full CI. No product implementation was changed. Other browsers, presets, mobile, continuous animation and other export formats were not tested. New and old layouts are not claimed to be visually equivalent. No issue closure is performed by this publication.
