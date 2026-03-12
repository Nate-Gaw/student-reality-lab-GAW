# Sprint 03 - UI Iteration and Information Architecture

## Objective
Refine the story flow and simplify the UI so audiences can compare outcomes faster.

## Reason
Presentation readability and rubric alignment required fewer distractions and clearer ordering of insights.

## Scope and Major Changes
- Removed lower-value visual sections (including "Two Futures"-style complexity).
- Reordered chart sections to emphasize salary and debt before timeline interpretation.
- Simplified degree cards by removing low-signal rows.
- Updated source attribution loading from `Website/data/sources.txt`.
- Tightened defensive UI checks to avoid null element errors.
- Fixed Net ROI card behavior so values reflect projection math instead of stale/intermediate objects.
- Removed break-even/data-row clutter from degree cards for cleaner presentation.

## Issues Encountered
- Some components expected now-removed data fields and needed cleanup.
- Chart containers required update order changes after section moves.
- Data-source rendering needed robust handling for blank/comment lines.
- Card totals briefly displayed incorrect values after slider interactions until update sequencing was corrected.

## Tests and Validation
- Full page smoke test after each section move.
- Verified source list renders and links resolve.
- Validated no chart initialization errors after layout refactor.
- Confirmed readability improvements in live walkthrough.
- Verified updated Net ROI values changed correctly with slider and button-driven recalculation.

## Risks and Follow-ups
- Future UI changes should keep section IDs stable to avoid script coupling.
- Recommend adding lightweight component-level tests for rendering guards.

## Files Impacted
- `Website/index.html`
- `Website/main.js`
- `Website/data/sources.txt`
