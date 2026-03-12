export function formatCurrency(value) {
  return `$${Math.round(value).toLocaleString()}`;
}

export function formatCompactCurrency(value) {
  return `$${(value / 1000).toFixed(1)}k`;
}

export function formatPercent(value, digits = 1) {
  return `${Number(value).toFixed(digits)}%`;
}

export function formatYears(value) {
  return `${Math.round(value)} years`;
}

export function formatMonthly(value) {
  return `$${Number(value).toFixed(2)}/mo`;
}
