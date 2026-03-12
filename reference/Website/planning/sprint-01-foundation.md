# Sprint 01 - Foundation

## Objective
Build the first complete version of the Website with a clear visual identity and interactive ROI concept.

## Reason
The project needed a user-facing experience that could explain degree outcomes with data and support classroom presentation goals.

## Scope and Major Changes
- Created core page layout and sections in `Website/index.html`.
- Implemented Swiss-Neon visual system in `Website/style.css`.
- Added baseline data wiring and interactivity in `Website/main.js`.
- Introduced charting and calculator-focused UI structure.
- Added defensive initialization patterns so rendering does not fail when some DOM targets are missing.

## Issues Encountered
- Initial runtime edge cases when data fields were missing or formatted inconsistently.
- Chart re-render timing and instance lifecycle conflicts.
- Need for stronger fallback behavior when source files were unavailable.
- Early chart configuration bugs required safe chart destruction before re-creation.

## Tests and Validation
- Manual load test in local dev server.
- Verified charts rendered without console errors.
- Checked responsive behavior on desktop and mobile widths.
- Confirmed initial calculator updates were reflected in outputs.
- Verified no hard crash when optional UI blocks were removed/hidden.

## Risks and Follow-ups
- Data model assumptions required stronger normalization.
- Needed improved guardrails for partial CSV records.

## Files Impacted
- `Website/index.html`
- `Website/style.css`
- `Website/main.js`
