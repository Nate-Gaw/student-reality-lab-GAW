import {
  formatCompactCurrency,
  formatCurrency,
  formatMonthly,
  formatPercent,
  formatYears
} from './formatters.js';

export function readRawState(selectors) {
  const valueOf = (element, fallback = 0) => {
    if (!element) return fallback;
    return element.type === 'checkbox' ? element.checked : element.value;
  };

  return {
    bachelorDebt: valueOf(selectors.ranges.bachelorDebt),
    masterDebt: valueOf(selectors.ranges.masterDebt),
    repaymentYears: valueOf(selectors.ranges.repaymentYears),
    interestRate: valueOf(selectors.ranges.interestRate),
    bachelorSalary: valueOf(selectors.ranges.bachelorSalary),
    masterSalary: valueOf(selectors.ranges.masterSalary),
    growthRate: valueOf(selectors.ranges.growthRate),
    taxRate: valueOf(selectors.ranges.taxRate),
    costIndex: valueOf(selectors.selects.costIndex, 1),
    annualChartType: valueOf(selectors.selects.annualChartType, 'bar'),
    showPoints: valueOf(selectors.toggles.showPoints, false),
    worklifePriority: valueOf(selectors.selects.worklifePriority, 2),
    careerPriority: valueOf(selectors.selects.careerPriority, 2),
    debtTolerance: valueOf(selectors.selects.debtTolerance, 2)
  };
}

export function writeInputDisplays(selectors, scenario) {
  const map = [
    ['bachelorDebt', formatCurrency(scenario.bachelorDebt), true],
    ['masterDebt', formatCurrency(scenario.masterDebt), true],
    ['repaymentYears', formatYears(scenario.repaymentYears), false],
    ['interestRate', formatPercent(scenario.interestRate, 1), false],
    ['bachelorSalary', formatCurrency(scenario.bachelorSalary), true],
    ['masterSalary', formatCurrency(scenario.masterSalary), true],
    ['growthRate', formatPercent(scenario.growthRate, 1), false],
    ['taxRate', formatPercent(scenario.taxRate, 1), false]
  ];

  map.forEach(([key, text, isCurrency]) => {
    const display = selectors.valueDisplays[key];
    if (display) display.innerText = text;

    const numInput = selectors.numbers[key];
    if (numInput) {
      numInput.value = isCurrency
        ? Math.round(scenario[key]).toLocaleString('en-US')
        : String(scenario[key]);
    }
  });

  if (selectors.valueDisplays.costIndex) {
    selectors.valueDisplays.costIndex.innerText = `x${Number(scenario.costIndex).toFixed(2)}`;
  }
}

export function writeComputedOutputs(selectors, computed) {
  const {
    breakEvenYear,
    bachelorMonthly,
    masterMonthly,
    advantage30,
    bachelorTotal30,
    masterTotal30,
    advantage15,
    retirementEstimate,
    qualitativeInsight,
    bachelorSalary,
    masterSalary,
    bachelorDebt,
    masterDebt
  } = computed;

  if (selectors.outputs.roiBreak) selectors.outputs.roiBreak.innerText = breakEvenYear === null ? 'Not Possible' : String(breakEvenYear);
  if (selectors.outputs.bachelorMonthly) selectors.outputs.bachelorMonthly.innerText = formatMonthly(bachelorMonthly);
  if (selectors.outputs.masterMonthly) selectors.outputs.masterMonthly.innerText = formatMonthly(masterMonthly);
  if (selectors.outputs.roiProfit) selectors.outputs.roiProfit.innerText = `${advantage30 >= 0 ? 'Gain' : 'Loss'} ${formatCurrency(Math.abs(advantage30))}`;
  if (selectors.outputs.bachelorTotal) selectors.outputs.bachelorTotal.innerText = formatCurrency(bachelorTotal30);
  if (selectors.outputs.masterTotal) selectors.outputs.masterTotal.innerText = formatCurrency(masterTotal30);

  if (selectors.outputs.summary15) {
    selectors.outputs.summary15.innerText = `After 15 years: ${advantage15 >= 0 ? 'Master leads by' : 'Bachelor leads by'} ${formatCurrency(Math.abs(advantage15))}.`;
  }

  if (selectors.outputs.summaryBreakEven) {
    selectors.outputs.summaryBreakEven.innerText = breakEvenYear === null
      ? 'Break-even outlook: Master path does not break even within 30 years under current assumptions.'
      : `Break-even outlook: Master path overtakes Bachelor in year ${breakEvenYear}.`;
  }

  if (selectors.outputs.summaryRetirement) {
    selectors.outputs.summaryRetirement.innerText = `Projected additional retirement value: ${formatCurrency(retirementEstimate)} (illustrative 7% growth estimate).`;
  }

  if (selectors.outputs.storyAnnotation) {
    selectors.outputs.storyAnnotation.innerText = breakEvenYear === null
      ? 'Annotation: Under current assumptions, the Master path does not cross the Bachelor path within 30 years.'
      : `Annotation: The break-even crossing occurs in year ${breakEvenYear}, where cumulative Master earnings first match/exceed Bachelor earnings.`;
  }

  if (selectors.outputs.quickAdvantage) {
    selectors.outputs.quickAdvantage.innerText = `${advantage30 >= 0 ? '' : '-'}${formatCurrency(Math.abs(advantage30))}`;
  }

  if (selectors.outputs.lifetimeDiff) {
    selectors.outputs.lifetimeDiff.innerText = formatCompactCurrency(advantage30);
  }

  if (selectors.outputs.qualitativeInsight) {
    selectors.outputs.qualitativeInsight.innerText = qualitativeInsight;
  }

  if (selectors.outputs.cardBSalary) selectors.outputs.cardBSalary.innerText = formatCurrency(bachelorSalary);
  if (selectors.outputs.cardMSalary) selectors.outputs.cardMSalary.innerText = formatCurrency(masterSalary);
  if (selectors.outputs.cardBDebt) selectors.outputs.cardBDebt.innerText = formatCurrency(bachelorDebt);
  if (selectors.outputs.cardMDebt) selectors.outputs.cardMDebt.innerText = formatCurrency(masterDebt);
  if (selectors.outputs.cardBRoi) selectors.outputs.cardBRoi.innerText = formatCurrency(bachelorTotal30);
  if (selectors.outputs.cardMRoi) selectors.outputs.cardMRoi.innerText = formatCurrency(masterTotal30);
}
