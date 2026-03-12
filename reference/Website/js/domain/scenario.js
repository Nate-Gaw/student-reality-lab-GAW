const DEFAULTS = {
  bachelorDebt: 27437,
  masterDebt: 61667,
  repaymentYears: 10,
  interestRate: 5,
  bachelorSalary: 85500,
  masterSalary: 95400,
  growthRate: 3,
  taxRate: 24,
  costIndex: 1,
  showPoints: false,
  annualChartType: 'bar',
  worklifePriority: 3,
  careerPriority: 2,
  debtTolerance: 2
};

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function num(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function buildScenario(rawInput) {
  const scenario = {
    bachelorDebt: clamp(num(rawInput.bachelorDebt, DEFAULTS.bachelorDebt), 0, 100000),
    masterDebt: clamp(num(rawInput.masterDebt, DEFAULTS.masterDebt), 0, 150000),
    repaymentYears: clamp(num(rawInput.repaymentYears, DEFAULTS.repaymentYears), 1, 30),
    interestRate: clamp(num(rawInput.interestRate, DEFAULTS.interestRate), 0, 12),
    bachelorSalary: clamp(num(rawInput.bachelorSalary, DEFAULTS.bachelorSalary), 20000, 250000),
    masterSalary: clamp(num(rawInput.masterSalary, DEFAULTS.masterSalary), 20000, 250000),
    growthRate: clamp(num(rawInput.growthRate, DEFAULTS.growthRate), 0, 10),
    taxRate: clamp(num(rawInput.taxRate, DEFAULTS.taxRate), 0, 45),
    costIndex: clamp(num(rawInput.costIndex, DEFAULTS.costIndex), 0.5, 2),
    showPoints: Boolean(rawInput.showPoints),
    annualChartType: rawInput.annualChartType === 'line' ? 'line' : 'bar',
    worklifePriority: clamp(num(rawInput.worklifePriority, DEFAULTS.worklifePriority), 1, 3),
    careerPriority: clamp(num(rawInput.careerPriority, DEFAULTS.careerPriority), 1, 3),
    debtTolerance: clamp(num(rawInput.debtTolerance, DEFAULTS.debtTolerance), 1, 3)
  };

  return scenario;
}
