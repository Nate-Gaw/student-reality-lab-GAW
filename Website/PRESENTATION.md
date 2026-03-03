# STAR Presentation Script

## S — Situation (20–30 sec)
Many CS students are being told that a Master’s degree is always worth it, but tuition costs and debt levels have changed faster than wages. Students need a clearer, data-backed way to compare the Bachelor and Master paths under realistic assumptions.

## T — Task (10–15 sec)
I answered one question: **when does a Master’s degree break even financially for CS students?**
The viewer should be able to adjust debt, salary, growth, tax, and cost-of-living assumptions and immediately see how break-even timing and 30-year outcomes change.

## A — Action (60–90 sec)
I built an interactive one-page data story with three evidence views and one control panel.

- **Key data transformation**
  - Raw CSVs are transformed into a stable contract at `data/processed.json`.
  - The transform script (`scripts/build-processed.mjs`) extracts salary/debt baseline metrics and stores them with definitions and source metadata.
  - The schema contract (`src/lib/schema.ts`) defines required fields and validates numeric integrity.

- **Interaction choices and why**
  - Slider controls for debt, salary, growth, taxes, and repayment period let users model personal scenarios.
  - A cost-of-living selector normalizes purchasing power across locations.
  - A chart point toggle and annual chart-type switch help users inspect trend vs magnitude.

- **Engineering decisions**
  - Refactored to clean architecture modules (`domain`, `ui`, `charts`, `services`, `app`).
  - Domain layer is pure and testable (no DOM or chart dependencies).
  - Chart layer receives computed arrays only; no business logic in rendering code.

## R — Result (60–90 sec)
The data shows that the Master path can outperform over a 30-year horizon, but only under certain debt and salary assumptions. In baseline settings, the dashboard shows a clear break-even year and a 30-year advantage metric.

- **Headline numbers**
  - Break-even year: dynamically computed from cumulative net earnings.
  - 30-year advantage: dynamically computed as Master cumulative net minus Bachelor cumulative net.

- **What changes with interaction**
  - Raising debt or taxes delays break-even and can eliminate the 30-year advantage.
  - Increasing salary growth or reducing debt accelerates break-even.

- **One limitation**
  - The model is financial-only; it does not quantify non-financial outcomes (job satisfaction, burnout, employer tuition support, or career preference).
