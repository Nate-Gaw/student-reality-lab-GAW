# Sprint 04 - Release and Presentation Readiness

## Objective
Finalize project state for submission, presentation delivery, and repository hygiene.

## Reason
The final stage required stable demos, presentation updates, and clean Git operations for publishing.

## Scope and Major Changes
- Updated `Website/PRESENTATION.md` content for STAR/rubric alignment.
- Moved large demo video strategy to external hosting and linked it from docs.
- Added line-ending normalization support via repository `.gitattributes`.
- Improved ignore rules to prevent large media files from being committed.
- Removed oversized video artifacts from push path by resetting/recommitting clean history for publishable changes.

## Issues Encountered
- GitHub rejected pushes due to oversized committed video artifacts.
- Line-ending warnings (CRLF/LF) created noisy staging messages.
- Needed history cleanup and recommit without large binaries.
- GitHub hard-limit failure included `GH001` and blocked remote pre-receive until large objects were removed from local unpushed commits.

## Tests and Validation
- Verified `git push` success after removing oversized artifacts.
- Confirmed presentation file updated and tracked correctly.
- Validated repository status clean after normalization rules.
- Confirmed no MP4 files remained staged after `.gitignore` updates.

## Risks and Follow-ups
- Keep large media hosted externally (YouTube/Drive) and link from markdown.
- If future binaries are needed, use Git LFS intentionally.

## Files Impacted
- `Website/PRESENTATION.md`
- `.gitattributes`
- `.gitignore`
