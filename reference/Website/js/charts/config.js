export const CHART_COLORS = {
  bachelor: '#2DE2E6',
  master: '#FF2A6D',
  grid: 'rgba(255,255,255,0.05)',
  tick: '#a5afb2'
};

export function commonLineOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { position: 'top', labels: { color: '#e0e4e7', font: { size: 12 }, padding: 12 } },
      tooltip: {
        backgroundColor: 'rgba(0,0,0,0.8)',
        titleColor: '#fff',
        bodyColor: '#e0e4e7',
        borderColor: 'rgba(45,226,230,0.3)',
        borderWidth: 1
      }
    }
  };
}

export function yCurrencyAxis(label) {
  return {
    title: { display: true, text: label, color: CHART_COLORS.tick, font: { size: 13, weight: '600' } },
    ticks: { color: CHART_COLORS.tick, font: { size: 12 }, callback: (value) => `$${(value / 1000 | 0)}k` },
    grid: { color: CHART_COLORS.grid }
  };
}

export function xYearsAxis() {
  return {
    title: { display: true, text: 'Years After Graduation', color: CHART_COLORS.tick, font: { size: 13, weight: '600' } },
    ticks: { color: CHART_COLORS.tick, font: { size: 12 } },
    grid: { color: CHART_COLORS.grid }
  };
}
