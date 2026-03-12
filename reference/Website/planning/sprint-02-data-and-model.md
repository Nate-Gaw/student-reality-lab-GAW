# Sprint 02 - Data and Financial Model

## Objective
Stabilize data ingestion and implement reliable long-range financial projection logic.

## Reason
Project outcomes depended on trustworthy ROI comparisons across degree paths; inconsistent input formats caused incorrect calculations.

## Scope and Major Changes
- Prioritized updated data files under `Website/data/`.
- Migrated data access to the consolidated structure: `salary_by_degree.csv`, `debt_by_degree.csv`, and `payback_analysis.csv`.
- Added robust numeric parsing for currency, commas, and percent values.
- Improved degree-level classification and fallback rules.
- Implemented/updated projection logic for salary growth, debt repayment, and cumulative outcomes.
- Improved chart update behavior after calculator interactions.
- Added source-aware loading behavior so calculations still run when one dataset is partially populated.

## Issues Encountered
- NaN and object-display issues when values were pulled from wrong data shapes.
- Divergent labels for degree level from different CSV sources.
- Synchronization gaps between slider/button events and chart redraws.
- Break-even and payback values required explicit fallback when raw rows did not include expected columns.

## Tests and Validation
- Manual test with multiple slider combinations and boundary values.
- Verified no `[object Object]` values in UI metrics.
- Confirmed debt/salary charts and ROI values updated together.
- Spot-checked projections against expected directional outcomes.
- Confirmed financial outputs stay numeric after CSV header/name variations.

## Risks and Follow-ups
- CSV schema drift remains a risk if external datasets change headers.
- Recommend adding automated data schema checks in a future sprint.

## Files Impacted
- `Website/main.js`
- `Website/data/salary_by_degree.csv`
- `Website/data/debt_by_degree.csv`
- `Website/data/payback_analysis.csv`
