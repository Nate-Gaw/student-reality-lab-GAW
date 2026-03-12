# Sprint 03 - Key Notes and Layout Refinement

Status: Completed
Date: 2026-03-09

## Goal
Refine layout and side-panel behavior to support editable, removable, and auto-updating key information.

## Deliverables
- Moved baseline information into the top hero section as general information.
- Increased visual emphasis of the `Decision Lens` title.
- Replaced old baseline tile with a bold `Key Notes` panel.
- Added automatic extraction of important stats/general guidance from AI answers into Key Notes.
- Added user controls to:
  - edit notes inline,
  - remove notes,
  - add custom notes manually.

## Files Changed
- `index.html`
- `style.css`
- `main.js`

## Notes
- Chat prompt flow and financial model computation remain intact.
- Key Notes include initial seeded model highlights and continue to update per assistant response.
