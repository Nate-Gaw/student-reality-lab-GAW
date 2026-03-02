Swiss Neon Data Impact — Interactive site

Quick start

1. Serve the folder as a static site from the workspace root. If you have Python installed:

```bash
cd "d:\College Classes\IS219\student-reality-lab-GAW\Swiss-Neon-Data-Impact"
python -m http.server 8000
# then open http://localhost:8000 in your browser
```

2. The site expects CSVs to be available under `/data/` relative to server root. By default it attempts to load:
- /data/BadCreditAvgLoanDebt.csv
- /data/CensusAvgIncome.csv
- /data/NerdWalletAvgLoanDebt.csv
- /data/USBureauLabor.csv

If your data files differ, edit `main.js` `CSV_FILES` array.

Features
- Hero with animated stat
- Degree comparison cards
- Break-even interactive timeline
- Salary & Debt charts
- Personal ROI calculator with sliders
- Two Futures narrative panels
- Data Transparency & Sources

Notes & Implementation details
- Uses Chart.js and PapaParse via CDN for charting and CSV parsing.
- The loader is resilient: it skips missing files and displays available sources.
- Data cleaning uses heuristics to find columns like `year`, `degree_level`, `avg_salary`, `avg_grad_debt`.
- Lifetime ROI is a simplified projection for demonstration; refine formulas for production.

Extending
- Swap Chart.js with D3 for more advanced visuals.
- Add server-side CSV listing for automatic discovery of /data/ files.
- Replace projections with CPI-based normalization to 2026 USD (example hooks left in comments).

Accessibility
- Colors have high contrast against dark background; accessible font sizes are used.
- Keyboard-focusable controls and clear labels.

Files
- index.html
- style.css
- main.js

