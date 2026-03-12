# Swiss Neon Data Impact — Website

Interactive data story answering: **Is grad school worth it for CS majors?**

## Deployment
- Vercel/Netlify Link: **TBD — add your live URL here**

## Quick Start

```bash
cd "d:\College Classes\IS219\student-reality-lab-GAW\Website"
npm install
npm run dev
```

Build for production:

```bash
npm run build
npm run preview
```

## Phase 2 — Data Pipeline + Contract

### Deliverables
- Data loading + transform module: `src/lib/loadData.ts`
- Lightweight schema/contract: `src/lib/schema.ts`
- Processed dataset: `data/processed.json`
- Build-time transform script: `scripts/build-processed.mjs`

### Cleaning & Transform Notes
- Debt values are normalized by stripping currency symbols and commas before numeric conversion.
- Baseline salary/debt metrics are extracted from:
	- `data/cs_degree_comparison.csv`
	- `data/NerdWalletAvgLoanDebt.csv`
- Processed output is written as a stable contract (`contractVersion`, `units`, `definitions`, `metrics`, `sources`).
- Transform runs before dev and build (`predev`, `build:data`).

### Definitions
- **Break-even**: First year where Master cumulative net earnings are greater than or equal to Bachelor cumulative net earnings.
- **ROI (30-year)**: `Master cumulative net at year 30 - Bachelor cumulative net at year 30`.
- **Debt**: Graduation debt treated as loan principal in amortized repayment.
- **Cost Index**: Multiplier used to normalize purchasing power by location.

### Engineering Acceptance
- `npm run dev` works.
- `npm run build` works.
- No unexplained magic constants: key assumptions are explicitly defined in schema/notes and scenario bounds.

## Phase 3 — Prototype App (One View)

### One View Requirements Covered
- Clear axes/units/labels on all charts.
- One meaningful interaction: scenario sliders/selectors/toggles.
- One annotation tied to data: `story-annotation` updates from computed break-even state.
- Story text included in-view (`What to Notice` section, ~180 words).

### Interaction Design
The interaction model is purpose-built to answer the question, not just add motion. Sliders adjust debt, salary, growth, tax, and repayment assumptions; location tier adjusts purchasing-power normalization. This helps users test whether the claim still holds under realistic personal constraints. Chart toggles support deeper inspection (trend continuity vs yearly magnitude), while summary cards convert technical outputs into decision-ready statements.

## Phase 4 — Full Story (2–4 Views + STAR)

### Narrative Structure
- **Context**: Why CS students face an uncertain grad-school decision.
- **Evidence**: Break-even, ROI-over-time, and annual-advantage views.
- **Segmentation/Counterpoint**: Location cost-index and scenario controls expose where conclusions reverse.
- **Takeaway**: Financial outcomes are conditional; break-even depends on debt/salary/tax assumptions.

### STAR Artifact
- Required STAR script: `PRESENTATION.md`

## Architecture Overview

- `js/domain/finance.js`: Pure finance math.
- `js/domain/scenario.js`: Scenario normalization/validation.
- `js/ui/selectors.js`: Element mapping only.
- `js/ui/formatters.js`: Display formatting.
- `js/ui/state.js`: Read raw state, write outputs.
- `js/ui/bindings.js`: Event wiring only.
- `js/charts/config.js`: Shared chart config.
- `js/charts/registry.js`: Create chart instances once.
- `js/charts/update.js`: Dataset/label updates only.
- `js/services/sources.js`: Source list population.
- `js/app.js`: Orchestrator (`initialize` + recompute pipeline).

## Testing

Finance regression tests:

```bash
npm run test:finance
```

Covers:
- loan payment behavior,
- projection length and cumulative series,
- break-even detection,
- annual advantage derivation.

