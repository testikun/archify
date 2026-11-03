# OpenPI task delegation

- Open `openpi-delegation.html` for the standalone Archify diagram.
- `openpi-delegation.json` is its editable source. Focus a component to inspect its explanation and pinned source ranges.
- Source: `https://github.com/openpi-dev/openpi`, revision `677b4959108976b99fb63fb5029198b04aa51cb5`. Source references are local-only; no live repository lookup was used.

## Reading the diagram

The parent Pi model chooses delegation. The OpenPI tool API accepts a prompt and returns a child id; the manager admits the child and owns its live snapshot. A Pi backend creates and prompts a separate in-process Pi session, translating native events into manager events. The caller can check status, explicitly wait for bounded results, or receive a deduplicated follow-up that wakes the parent after completion. The parent remains responsible for synthesis.

“Independent” means a separate Pi session and bounded tool surface, not a separate OS process or filesystem/network sandbox. The default working directory is shared. An optional requested worktree must be created successfully or spawning fails.

Scope is direct model-origin delegation. The Web adapter's `session.prompt` call grounds task admission; the diagram does not expand Web transport, `/btw`, workflow orchestration, provider internals or the Pi SDK's implementation. Native session storage is called through Pi APIs; physical storage durability cannot be established from this slice. Persistence/evidence failure is distinct from execution failure.

## Review

- Archify showcase validation, delivery, artifact checks and real-Chrome browser checks passed for the final candidate. Receipts are in `review-2/` and beside the HTML.
- Final 1440×900 light and dark screenshots were visually inspected. Larger screenshots were captured but not perceptually reviewed.
- Simplification experiment: removed the redundant parent-runtime frame and narrowed the capability frame to the actual child, leaving the backend adapter outside it. The responsibilities, communication paths and actual process/capability boundaries remain; all gates still pass. The simpler version is delivered.
- Project source is unchanged. Diagram artifacts and review evidence are confined to this output directory. Archify update checks were disabled to avoid live services.
