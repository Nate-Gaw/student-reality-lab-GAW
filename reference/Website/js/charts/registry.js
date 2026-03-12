import { CHART_COLORS, commonLineOptions, xYearsAxis, yCurrencyAxis } from './config.js';

function lineDataset(label, color, data = [], pointRadius = 0) {
  return {
    label,
    data,
    borderColor: color,
    backgroundColor: `${color}22`,
    tension: 0.25,
    pointRadius,
    pointHoverRadius: 6,
    borderWidth: 2,
    fill: false
  };
}

function getContext(canvas) {
  return canvas && canvas.getContext ? canvas.getContext('2d') : null;
}

export function createChartRegistry(selectors, years, options) {
  const pointRadius = options.showPoints ? 3 : 0;

  const registry = {
    annualType: options.annualChartType,
    annualCanvas: selectors.charts.annualAdvantage,
    heroMini: null,
    breakEven: null,
    salaryBar: null,
    debtBar: null,
    roiVsTime: null,
    annualAdvantage: null
  };

  const heroCtx = getContext(selectors.charts.heroMini);
  if (heroCtx) {
    registry.heroMini = new Chart(heroCtx, {
      type: 'line',
      data: {
        labels: years,
        datasets: [
          lineDataset('Bachelor', CHART_COLORS.bachelor, [], pointRadius),
          lineDataset('Master', CHART_COLORS.master, [], pointRadius)
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } }
      }
    });
  }

  const breakCtx = getContext(selectors.charts.breakEven);
  if (breakCtx) {
    registry.breakEven = new Chart(breakCtx, {
      type: 'line',
      data: {
        labels: years,
        datasets: [
          lineDataset('Bachelor Path (Cumulative Net Earnings)', CHART_COLORS.bachelor, [], pointRadius),
          lineDataset('Master Path (Cumulative Net Earnings)', CHART_COLORS.master, [], pointRadius)
        ]
      },
      options: {
        ...commonLineOptions(),
        scales: {
          y: yCurrencyAxis('Cumulative Net Earnings (USD)'),
          x: xYearsAxis()
        }
      }
    });
  }

  const salaryCtx = getContext(selectors.charts.salaryBar);
  if (salaryCtx) {
    registry.salaryBar = new Chart(salaryCtx, {
      type: 'bar',
      data: {
        labels: ['Bachelor', 'Master'],
        datasets: [{
          label: 'Starting Salary (USD)',
          data: [0, 0],
          backgroundColor: [CHART_COLORS.bachelor, CHART_COLORS.master]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: { legend: { position: 'top', labels: { color: '#e0e4e7' } } },
        scales: {
          x: yCurrencyAxis('Salary (USD)'),
          y: { ticks: { color: CHART_COLORS.tick } }
        }
      }
    });
  }

  const debtCtx = getContext(selectors.charts.debtBar);
  if (debtCtx) {
    registry.debtBar = new Chart(debtCtx, {
      type: 'bar',
      data: {
        labels: ['Bachelor', 'Master'],
        datasets: [{
          label: 'Average Debt After Graduation (USD)',
          data: [0, 0],
          backgroundColor: [CHART_COLORS.bachelor, CHART_COLORS.master]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: { legend: { position: 'top', labels: { color: '#e0e4e7' } } },
        scales: {
          x: yCurrencyAxis('Debt (USD)'),
          y: { ticks: { color: CHART_COLORS.tick } }
        }
      }
    });
  }

  const roiCtx = getContext(selectors.charts.roiVsTime);
  if (roiCtx) {
    registry.roiVsTime = new Chart(roiCtx, {
      type: 'line',
      data: {
        labels: years,
        datasets: [lineDataset("Master's Financial Advantage (Cumulative)", CHART_COLORS.bachelor, [], pointRadius)]
      },
      options: {
        ...commonLineOptions(),
        scales: {
          y: yCurrencyAxis('Cumulative Advantage (USD)'),
          x: xYearsAxis()
        }
      }
    });
  }

  registry.annualAdvantage = createAnnualChart(registry.annualCanvas, years, options.annualChartType, pointRadius);
  return registry;
}

export function createAnnualChart(canvas, years, type, pointRadius) {
  const ctx = getContext(canvas);
  if (!ctx) return null;

  return new Chart(ctx, {
    type,
    data: {
      labels: years,
      datasets: [{
        label: 'Annual Net Salary Advantage (Master - Bachelor)',
        data: [],
        backgroundColor: [],
        borderColor: CHART_COLORS.bachelor,
        borderRadius: 4,
        borderSkipped: false,
        pointRadius,
        tension: 0.2,
        fill: false
      }]
    },
    options: {
      ...commonLineOptions(),
      scales: {
        y: yCurrencyAxis('Annual Advantage (USD)'),
        x: xYearsAxis()
      }
    }
  });
}
