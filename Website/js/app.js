import {
  calculateMonthlyPayment,
  computeBreakEvenYear,
  projectEarnings,
  toAnnualAdvantageSeries,
  toCumulativeSeries
} from './domain/finance.js';
import { buildScenario } from './domain/scenario.js';
import { getSelectors } from './ui/selectors.js';
import { wireBindings } from './ui/bindings.js';
import { readRawState, writeComputedOutputs, writeInputDisplays } from './ui/state.js';
import { createChartRegistry } from './charts/registry.js';
import { updateCharts } from './charts/update.js';
import { populateSourcesList } from './services/sources.js';

function yearsArray(maxYears = 30) {
  return Array.from({ length: maxYears + 1 }, (_, index) => index);
}

function buildQualitativeInsight({ advantage30, worklifePriority, careerPriority, debtTolerance }) {
  if (advantage30 >= 0 && careerPriority >= 2 && debtTolerance >= 2) {
    return 'Your profile favors a Master path financially and professionally, as long as debt remains manageable.';
  }
  if (worklifePriority >= 3 && debtTolerance <= 2) {
    return 'Your priorities suggest caution: a Bachelor path may better protect lifestyle flexibility and debt comfort.';
  }
  if (advantage30 < 0) {
    return 'Current assumptions favor the Bachelor path financially; pursue Master mainly for non-financial goals.';
  }
  return 'Balanced profile: review both financial and lifestyle factors before deciding.';
}

function computeFinancialModel(scenario) {
  const bachelorProjection = projectEarnings({
    startSalary: scenario.bachelorSalary,
    growthRate: scenario.growthRate,
    yearsToProject: 30,
    totalDebt: scenario.bachelorDebt,
    annualRate: scenario.interestRate,
    repaymentYears: scenario.repaymentYears,
    taxRate: scenario.taxRate,
    costIndex: scenario.costIndex
  });

  const masterProjection = projectEarnings({
    startSalary: scenario.masterSalary,
    growthRate: scenario.growthRate,
    yearsToProject: 30,
    totalDebt: scenario.masterDebt,
    annualRate: scenario.interestRate,
    repaymentYears: scenario.repaymentYears,
    taxRate: scenario.taxRate,
    costIndex: scenario.costIndex
  });

  const bachelorCumulative = toCumulativeSeries(bachelorProjection);
  const masterCumulative = toCumulativeSeries(masterProjection);
  const annualAdvantage = toAnnualAdvantageSeries(bachelorProjection, masterProjection);
  const roiOverTime = masterCumulative.map((value, index) => value - bachelorCumulative[index]);
  const breakEvenYear = computeBreakEvenYear(bachelorProjection, masterProjection);

  const bachelorTotal30 = bachelorCumulative[30];
  const masterTotal30 = masterCumulative[30];
  const advantage30 = masterTotal30 - bachelorTotal30;
  const advantage15 = masterCumulative[15] - bachelorCumulative[15];

  const bachelorMonthly = calculateMonthlyPayment(scenario.bachelorDebt, scenario.interestRate, scenario.repaymentYears);
  const masterMonthly = calculateMonthlyPayment(scenario.masterDebt, scenario.interestRate, scenario.repaymentYears);

  return {
    years: yearsArray(30),
    bachelorProjection,
    masterProjection,
    bachelorCumulative,
    masterCumulative,
    annualAdvantage,
    roiOverTime,
    breakEvenYear,
    bachelorMonthly,
    masterMonthly,
    bachelorTotal30,
    masterTotal30,
    advantage30,
    advantage15,
    retirementEstimate: Math.round(Math.max(0, advantage30) * 1.07),
    qualitativeInsight: buildQualitativeInsight({
      advantage30,
      worklifePriority: scenario.worklifePriority,
      careerPriority: scenario.careerPriority,
      debtTolerance: scenario.debtTolerance
    }),
    bachelorSalary: scenario.bachelorSalary,
    masterSalary: scenario.masterSalary,
    bachelorDebt: scenario.bachelorDebt,
    masterDebt: scenario.masterDebt
  };
}

function createRecomputePipeline(selectors, registry) {
  return function recompute() {
    const rawState = readRawState(selectors);
    const scenario = buildScenario(rawState);

    writeInputDisplays(selectors, scenario);

    const model = computeFinancialModel(scenario);

    writeComputedOutputs(selectors, model);
    updateCharts(registry, {
      years: model.years,
      bachelorCumulative: model.bachelorCumulative,
      masterCumulative: model.masterCumulative,
      roiOverTime: model.roiOverTime,
      annualAdvantage: model.annualAdvantage,
      bachelorSalary: model.bachelorSalary,
      masterSalary: model.masterSalary,
      bachelorDebt: model.bachelorDebt,
      masterDebt: model.masterDebt
    }, {
      showPoints: scenario.showPoints,
      annualChartType: scenario.annualChartType
    });
  };
}

export function initialize() {
  const selectors = getSelectors();
  populateSourcesList(selectors.sourcesList);

  const initialScenario = buildScenario(readRawState(selectors));
  const registry = createChartRegistry(selectors, yearsArray(30), {
    showPoints: initialScenario.showPoints,
    annualChartType: initialScenario.annualChartType
  });

  const recompute = createRecomputePipeline(selectors, registry);

  wireBindings(selectors, {
    onRecompute: recompute,
    onStartExplore: () => window.scrollTo({ top: 600, behavior: 'smooth' }),
    onCompareScenario: () => {
      const panel = document.getElementById('roi-panel');
      if (panel) panel.scrollIntoView({ behavior: 'smooth' });
    }
  });

  recompute();
}

document.addEventListener('DOMContentLoaded', initialize);
