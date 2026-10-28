# #452: author-declared call stages — research evidence

Research for [tt-a1i/archify#452](https://github.com/tt-a1i/archify/issues/452), run on 2026-10-28 against upstream **`6ca6a5c84439b57ea22e0630fe306e1d91587a6e`**. This branch contains investigation artifacts only. No product implementation or proposed schema is included.

**Existing labels and native Story can express this constructed scenario. Direct node Focus/hover still does not play its authored business stages.** These findings support a scope discussion; they do not establish that #452 should be closed.

## Read and try

- [Detailed report (Chinese)](report.zh-CN.md), including screenshots, source references, negative probes and limitations.
- [Shared author-declared facts](facts.json) and [all inputs](inputs). These are synthetic examples inspired by the issue's prose, not the reporter's original application or an execution trace.
- [Architecture HTML](artifacts/parallel-architecture.html), [Sequence HTML](artifacts/parallel-sequence.html), and [native Story HTML](artifacts/parallel-story.html).
- [Native PNG/SVG exports](exports), [28 browser screenshots](screenshots), [browser observations](receipts/browser.json), [additional interaction probes](receipts/browser-probes.json), and [summary assertions](receipts/summary.json).
- [CLI commands and diagnostics](receipts/cli), [source blob identities](receipts/source-files.json), and [reproduction scripts](scripts).

Download the branch/commit ZIP or use **Download raw file** on an HTML file, then open it locally. GitHub's file view displays source rather than running the Viewer. The HTML files are self-contained. In the Story HTML, click **Still** at the top right to enter **Story**, then **Play**; the recorded run used Sound off. Return to Still to inspect the complete component graph. No video was produced or verified.

## What the comparison shows

The serial case has one caller and three awaited calls. The parallel case extends it to four completed stages followed by one batch containing writes A and B. The batch declares no relative A/B order, completion order, exact simultaneous start, or runtime duration. Both renderers preserve the same component IDs, relation IDs, endpoints, labels and ownership facts. Architecture retains enclosing boundaries; Sequence retains ownership as participant text, not the same spatial boundary structure.

| Observation | Result at the pinned revision |
| --- | --- |
| Static declarations | Numbered labels, `await`, and explicit `parallel P` text retain the declared facts. Sequence rows alone do not assert concurrency. |
| Focus / hover | They match the caller's outgoing relations. Passport can preview one relation; neither interaction groups those relations into the author's ordered stages. |
| Ordinary Live | Architecture used zero phase delay for all six relations; Sequence used staggered delays, including separate A/B delays. Neither schedule is execution evidence. |
| Native Story | Existing `via` references, four `trace` points, then `action: "parallel"` with `via: ["write-a", "write-b"]` give the desired presentation sequence. A/B share a presentation start time. |
| Still / reduced motion | All four main native Viewer cases settled to Still with zero sampled animations. Reduced-motion Story hid all native flow animation elements while retaining static relations and text. |
| Native exports | All four main Focus SVG exports equal their default SVG bytes. Four PNGs came from the real Export menu. Story SVG keeps the full graph; its extra CSS means the bytes differ, while XML with style elements removed is identical. |

Story requires a separate authored brief and a mode switch. Its presentation timestamps are not measured application timing. Fixed seek positions supplied comparable screenshots; a separate short Play check established that playback advanced. This was not an end-to-end video export test.

## Ablations and limits

Removing duplicate Architecture cards left the canonical SVG byte-identical, so the minimal candidate and Story base omit them. Removing numeric labels or explicit parallel prose loses the corresponding static declaration. Omitting Story preserves static facts but removes the staged walkthrough.

The records also retain three failed probes: unapproved `connections[].order` is rejected by the current schema; placing Sequence A/B at identical `y` violates spacing; reversing Architecture's connection array causes a label overlap. The latter is a layout failure, not evidence of changed business order. Valid legacy `meta.views` is accepted and ignored, with no restored guided UI.

These are working research examples with visible limits. Parallel Architecture has three label-route-clearance and two ambiguous-corridor warnings; the Sequence case has a desktop readability-budget warning. At the recorded viewport, parallel edge labels are roughly 7.3 px and 9.6 px respectively. No readability acceptance or user comprehension improvement is claimed. No gates were weakened.

The run used Node v20.20.2, Chrome 156.0.8078.48, a 1440×1000 viewport at DPR 1, light theme / Classic / default Read. Eight diagram inputs delivered, three probes failed as recorded, and Story scan/attach succeeded. There was no full regression suite, cross-platform browser matrix, video/print check, screen-reader audit, or human reader study. Initial source-acquisition failures are preserved separately in [cli-incomplete-source](receipts/cli-incomplete-source); they are environment setup failures, not product defects.

## Reproduce

Use a separate copy of this evidence directory: rerunning overwrites the recorded outputs and receipts. Requirements are Git, Python 3, Node.js and Chrome/Chromium. The recorded run used the versions above. No live Archify installation or package installation is needed.

Obtain the pinned upstream source inside the evidence directory:

```sh
git init source-pinned
git -C source-pinned remote add origin https://github.com/tt-a1i/archify.git
git -C source-pinned fetch --depth=1 origin 6ca6a5c84439b57ea22e0630fe306e1d91587a6e
git -C source-pinned checkout --detach FETCH_HEAD

python3 scripts/make-inputs.py
python3 scripts/render.py
node scripts/browser.mjs
node scripts/browser.mjs --probes
python3 scripts/summarize.py
```

Set `ARCHIFY_CHROME` if Chrome is not at the default macOS application path. `render.py` checks the source HEAD before running. The browser harness captures the product's actual download Blobs; SVG serialization and PNG rasterization remain the native implementation. `hydrate-source.py` was used to repair the original sparse snapshot and verify 262 selected Git blob hashes; it is not needed after the full pinned checkout above. `refresh-github.py` performs read-only queries and can return newer discussion/branch state; that does not change the revision tested here.

## Publication provenance

HTML, input JSON, screenshots, native exports, fact sheet and reproduction scripts are copied byte-for-byte from the completed investigation. Machine-local path prefixes in receipts are normalized to `$EVIDENCE`; the Chinese report's links point to this bundle or immutable upstream source. These path changes do not alter the recorded artifact hashes or diagnostics. The original local checksum manifest remains at [receipts/artifact-manifest.json](receipts/artifact-manifest.json) as a historical record; its original README and path-bearing receipt hashes are not hashes of the edited public copies. [manifest-sha256.json](manifest-sha256.json) hashes the actual public files, excluding itself.

The GitHub receipts describe the state observed before this results comment was published. No local source checkout, Git object cache, browser profile, or credentials are included. Upstream runtime/template licensing and font notices accompany the generated artifacts in [licenses](licenses).

AI disclosure: Codex (GPT-6) performed the investigation, generated fixtures, ran the CLI and real-browser checks, inspected representative screenshots, and prepared this report/comment under **@testikun**'s direction. @testikun is the accountable contributor. This is Agent-operated evidence, not human acceptance or a claim of human review.
