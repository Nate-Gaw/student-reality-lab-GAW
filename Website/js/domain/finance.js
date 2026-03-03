export function calculateMonthlyPayment(principal, annualRate, yearsToRepay) {
  if (principal <= 0 || yearsToRepay <= 0) return 0;

  const monthlyRate = annualRate / 100 / 12;
  const numPayments = yearsToRepay * 12;

  if (monthlyRate === 0) {
    return principal / numPayments;
  }

  const numerator = monthlyRate * Math.pow(1 + monthlyRate, numPayments);
  const denominator = Math.pow(1 + monthlyRate, numPayments) - 1;
  return principal * (numerator / denominator);
}

export function projectEarnings({
  startSalary,
  growthRate,
  yearsToProject = 30,
  totalDebt = 0,
  annualRate = 5,
  repaymentYears = 10,
  taxRate = 0,
  costIndex = 1
}) {
  const projection = [];
  let currentSalary = startSalary;
  let cumulativeEarnings = 0;

  const monthlyPayment = calculateMonthlyPayment(totalDebt, annualRate, repaymentYears);
  const annualPayment = monthlyPayment * 12;

  for (let year = 0; year <= yearsToProject; year += 1) {
    if (year > 0) {
      currentSalary *= (1 + growthRate / 100);
    }

    const isRepayingDebt = year > 0 && year <= repaymentYears;
    const paymentThisYear = isRepayingDebt ? annualPayment : 0;

    const grossCompensation = currentSalary;
    const taxAmount = grossCompensation * (taxRate / 100);
    const afterTaxIncome = grossCompensation - taxAmount;
    const costAdjustedIncome = costIndex > 0 ? afterTaxIncome / costIndex : afterTaxIncome;
    const netEarningsThisYear = costAdjustedIncome - paymentThisYear;

    cumulativeEarnings += netEarningsThisYear;

    projection.push({
      year,
      salary: Math.round(currentSalary),
      grossCompensation: Math.round(grossCompensation),
      taxAmount: Math.round(taxAmount),
      monthlyPayment: Math.round(monthlyPayment),
      annualPayment: Math.round(annualPayment),
      netEarningsThisYear: Math.round(netEarningsThisYear),
      cumulativeNet: Math.round(cumulativeEarnings),
      isRepayingDebt
    });
  }

  return projection;
}

export function computeBreakEvenYear(bachelorProjection, masterProjection) {
  const years = Math.min(bachelorProjection.length, masterProjection.length);
  for (let i = 0; i < years; i += 1) {
    if (masterProjection[i].cumulativeNet >= bachelorProjection[i].cumulativeNet) {
      return i;
    }
  }
  return null;
}

export function toCumulativeSeries(projection) {
  return projection.map((entry) => entry.cumulativeNet);
}

export function toAnnualAdvantageSeries(bachelorProjection, masterProjection) {
  const years = Math.min(bachelorProjection.length, masterProjection.length);
  const output = [];

  for (let i = 0; i < years; i += 1) {
    output.push(masterProjection[i].netEarningsThisYear - bachelorProjection[i].netEarningsThisYear);
  }

  return output;
}
