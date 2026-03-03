export function getSelectors() {
  const byId = (id) => document.getElementById(id);

  return {
    ranges: {
      bachelorDebt: byId('bachelor-debt'),
      masterDebt: byId('master-debt'),
      repaymentYears: byId('repayment-period'),
      interestRate: byId('interest'),
      bachelorSalary: byId('bachelor-salary'),
      masterSalary: byId('master-salary'),
      growthRate: byId('growth'),
      taxRate: byId('tax-rate')
    },
    numbers: {
      bachelorDebt: byId('bachelor-debt-num'),
      masterDebt: byId('master-debt-num'),
      repaymentYears: byId('repayment-period-num'),
      interestRate: byId('interest-num'),
      bachelorSalary: byId('bachelor-salary-num'),
      masterSalary: byId('master-salary-num'),
      growthRate: byId('growth-num'),
      taxRate: byId('tax-rate-num')
    },
    valueDisplays: {
      bachelorDebt: byId('bachelor-debt-val'),
      masterDebt: byId('master-debt-val'),
      repaymentYears: byId('repayment-period-val'),
      interestRate: byId('interest-val'),
      bachelorSalary: byId('bachelor-salary-val'),
      masterSalary: byId('master-salary-val'),
      growthRate: byId('growth-val'),
      taxRate: byId('tax-rate-val'),
      costIndex: byId('location-tier-val')
    },
    selects: {
      costIndex: byId('location-tier'),
      annualChartType: byId('annual-chart-type'),
      worklifePriority: byId('q-worklife'),
      careerPriority: byId('q-career'),
      debtTolerance: byId('q-debt')
    },
    toggles: {
      showPoints: byId('chart-show-points')
    },
    outputs: {
      roiBreak: byId('roi-break'),
      bachelorMonthly: byId('bachelor-monthly'),
      masterMonthly: byId('master-monthly'),
      roiProfit: byId('roi-profit'),
      bachelorTotal: byId('roi-bachelor-total'),
      masterTotal: byId('roi-master-total'),
      summary15: byId('summary-15y'),
      summaryBreakEven: byId('summary-breakeven'),
      summaryRetirement: byId('summary-retirement'),
      storyAnnotation: byId('story-annotation'),
      quickAdvantage: byId('quick-advantage'),
      lifetimeDiff: byId('lifetime-diff'),
      qualitativeInsight: byId('qualitative-insight'),
      cardBSalary: byId('b-salary'),
      cardMSalary: byId('m-salary'),
      cardBDebt: byId('b-debt'),
      cardMDebt: byId('m-debt'),
      cardBRoi: byId('b-roi'),
      cardMRoi: byId('m-roi')
    },
    charts: {
      heroMini: byId('heroMiniChart'),
      breakEven: byId('breakEvenChart'),
      salaryBar: byId('salaryBar'),
      debtBar: byId('debtArea'),
      roiVsTime: byId('roiVsTimeChart'),
      annualAdvantage: byId('annualAdvantageChart')
    },
    actions: {
      startExplore: byId('start-explore'),
      compareScenario: byId('compare-scenario')
    },
    sourcesList: byId('sources-list')
  };
}
