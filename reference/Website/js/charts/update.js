import { CHART_COLORS } from './config.js';
import { createAnnualChart } from './registry.js';

export function updateCharts(registry, payload, options) {
  const {
    years,
    bachelorCumulative,
    masterCumulative,
    roiOverTime,
    annualAdvantage,
    bachelorSalary,
    masterSalary,
    bachelorDebt,
    masterDebt
  } = payload;

  const pointRadius = options.showPoints ? 3 : 0;

  if (registry.heroMini) {
    registry.heroMini.data.labels = years;
    registry.heroMini.data.datasets[0].data = bachelorCumulative;
    registry.heroMini.data.datasets[1].data = masterCumulative;
    registry.heroMini.data.datasets[0].pointRadius = pointRadius;
    registry.heroMini.data.datasets[1].pointRadius = pointRadius;
    registry.heroMini.update();
  }

  if (registry.breakEven) {
    registry.breakEven.data.labels = years;
    registry.breakEven.data.datasets[0].data = bachelorCumulative;
    registry.breakEven.data.datasets[1].data = masterCumulative;
    registry.breakEven.data.datasets[0].pointRadius = pointRadius;
    registry.breakEven.data.datasets[1].pointRadius = pointRadius;
    registry.breakEven.update();
  }

  if (registry.salaryBar) {
    registry.salaryBar.data.datasets[0].data = [bachelorSalary, masterSalary];
    registry.salaryBar.update();
  }

  if (registry.debtBar) {
    registry.debtBar.data.datasets[0].data = [bachelorDebt, masterDebt];
    registry.debtBar.update();
  }

  if (registry.roiVsTime) {
    registry.roiVsTime.data.labels = years;
    registry.roiVsTime.data.datasets[0].data = roiOverTime;
    registry.roiVsTime.data.datasets[0].pointRadius = pointRadius;
    registry.roiVsTime.update();
  }

  if (registry.annualType !== options.annualChartType && registry.annualCanvas) {
    if (registry.annualAdvantage) registry.annualAdvantage.destroy();
    registry.annualAdvantage = createAnnualChart(registry.annualCanvas, years, options.annualChartType, pointRadius);
    registry.annualType = options.annualChartType;
  }

  if (registry.annualAdvantage) {
    const colors = annualAdvantage.map((value) => (value >= 0 ? `${CHART_COLORS.bachelor}CC` : `${CHART_COLORS.master}CC`));
    registry.annualAdvantage.data.labels = years;
    registry.annualAdvantage.data.datasets[0].data = annualAdvantage;
    registry.annualAdvantage.data.datasets[0].backgroundColor = colors;
    registry.annualAdvantage.data.datasets[0].pointRadius = pointRadius;
    registry.annualAdvantage.update();
  }
}
