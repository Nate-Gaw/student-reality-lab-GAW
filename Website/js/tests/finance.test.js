import {
  calculateMonthlyPayment,
  computeBreakEvenYear,
  projectEarnings,
  toAnnualAdvantageSeries,
  toCumulativeSeries
} from '../domain/finance.js';

function assert(condition, message) {
  if (!condition) {
    throw new Error(`Test failed: ${message}`);
  }
}

function runFinanceTests() {
  const monthly = calculateMonthlyPayment(50000, 5, 10);
  assert(monthly > 0, 'monthly payment should be positive for valid loan');

  const noInterestMonthly = calculateMonthlyPayment(12000, 0, 1);
  assert(Math.round(noInterestMonthly) === 1000, '0% interest payment should be principal/12');

  const bachelor = projectEarnings({
    startSalary: 80000,
    growthRate: 3,
    yearsToProject: 30,
    totalDebt: 20000,
    annualRate: 5,
    repaymentYears: 10,
    taxRate: 20,
    costIndex: 1
  });

  const master = projectEarnings({
    startSalary: 92000,
    growthRate: 3,
    yearsToProject: 30,
    totalDebt: 50000,
    annualRate: 5,
    repaymentYears: 10,
    taxRate: 20,
    costIndex: 1
  });

  assert(bachelor.length === 31, 'projection should include year 0 through year 30');
  assert(master[30].cumulativeNet > bachelor[30].cumulativeNet, 'higher salary path should end with higher cumulative net under these assumptions');

  const breakEven = computeBreakEvenYear(bachelor, master);
  assert(breakEven !== null, 'break-even should exist in this scenario');

  const bachelorCum = toCumulativeSeries(bachelor);
  const masterCum = toCumulativeSeries(master);
  assert(bachelorCum.length === 31 && masterCum.length === 31, 'cumulative series length should match projection length');

  const annualAdvantage = toAnnualAdvantageSeries(bachelor, master);
  assert(annualAdvantage.length === 31, 'annual advantage series should match year count');

  console.log('All finance tests passed.');
}

runFinanceTests();
