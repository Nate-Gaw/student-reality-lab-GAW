// main.js — Complete Financial ROI Model with Loan Amortization
// Implements the full specification with proper salary growth, loan calculations, and visualization

// Runtime holder for latest computed stats
let CURRENT_STATS = null;

// Default statistics (from payback_analysis.csv)
function getDefaultStats() {
  return {
    bachelor: {
      avgSalary: 85500,
      avgDebt: 27437,
      roi: 2565000,
      count: 0
    },
    master: {
      avgSalary: 95400,
      avgDebt: 61667,
      roi: 2903333,
      count: 0
    }
  };
}

const LOCATION_MULTIPLIERS = {
  low: 0.88,
  avg: 1.0,
  high: 1.12,
  veryhigh: 1.25
};

function getChartPointRadius() {
  const toggle = document.getElementById('chart-show-points');
  return toggle && toggle.checked ? 3 : 0;
}

function getAnnualChartType() {
  const selector = document.getElementById('annual-chart-type');
  return selector ? selector.value : 'bar';
}

/**
 * Calculate monthly loan payment using standard amortization formula
 * Payment = P * (r(1+r)^n) / ((1+r)^n - 1)
 * where P = principal, r = monthly rate, n = number of payments
 */
function calculateMonthlyPayment(principal, annualRate, yearsToRepay) {
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

/**
 * Generate full 30-year financial projection for one degree path
 * Accounts for:
 * - Salary growth at constant annual percentage
 * - Loan repayment during the first N years
 * - Cumulative net earnings (salary - monthly payments)
 */
function projectEarnings(startSalary, growthRate, yearsToProject = 30, totalDebt = 0, annualRate = 5, repaymentYears = 10, extra = {}) {
  const projection = [];
  let currentSalary = startSalary;
  let cumulativeEarnings = 0;
  const monthlyPayment = calculateMonthlyPayment(totalDebt, annualRate, repaymentYears);
  const annualPayment = monthlyPayment * 12;
  const taxRate = Number(extra.taxRate || 0);
  const costIndex = Number(extra.costIndex || 1);
  
  for (let year = 0; year <= yearsToProject; year++) {
    // Salary grows each year (after year 0)
    if (year > 0) {
      currentSalary = currentSalary * (1 + growthRate / 100);
    }
    
    // Determine annual payment (zero after repayment period)
    const isRepayingDebt = year > 0 && year <= repaymentYears;
    const paymentThisYear = isRepayingDebt ? annualPayment : 0;
    
    const grossCompensation = currentSalary;
    const taxAmount = grossCompensation * (taxRate / 100);
    const afterTaxIncome = grossCompensation - taxAmount;
    const costAdjustedIncome = costIndex > 0 ? afterTaxIncome / costIndex : afterTaxIncome;
    const netEarningsThisYear = costAdjustedIncome - paymentThisYear;
    cumulativeEarnings += netEarningsThisYear;
    
    projection.push({
      year: year,
      salary: Math.round(currentSalary),
      grossCompensation: Math.round(grossCompensation),
      monthlyPayment: Math.round(monthlyPayment),
      annualPayment: Math.round(annualPayment),
      taxAmount: Math.round(taxAmount),
      costAdjustedIncome: Math.round(costAdjustedIncome),
      netEarningsThisYear: Math.round(netEarningsThisYear),
      cumulativeNet: Math.round(cumulativeEarnings),
      isRepayingDebt: isRepayingDebt
    });
  }
  
  return projection;
}

// UI chart instances
let breakChart, salaryBar, debtArea, heroMini, roiVsTimeChart, annualAdvantageChart;

function createCharts(cleaned, datasets, stats) {
  console.log('🎨 Creating charts with stats:', stats);
  const years = Array.from({length:31}, (_,i)=>i);
  
  // Compute fallback values if needed
  const computeFallback = (level, field) => {
    try {
      const rows = cleaned.filter(r => r.degree_level && r.degree_level.includes(level) && r[field] !== null);
      if (!rows.length) return null;
      const vals = rows.map(r => Number(r[field])).filter(v => !Number.isNaN(v));
      if (!vals.length) return null;
      return Math.round(vals.reduce((a,b)=>a+b,0)/vals.length);
    } catch(e){ return null; }
  };

  // Get values (prefer stats, then fallback)
  const bSalary = stats.bachelor.avgSalary || computeFallback('bachelor','avg_salary') || 85500;
  const mSalary = stats.master.avgSalary || computeFallback('master','avg_salary') || 95400;
  const bDebt = stats.bachelor.avgDebt || computeFallback('bachelor','avg_grad_debt') || 27437;
  const mDebt = stats.master.avgDebt || computeFallback('master','avg_grad_debt') || 61667;

  console.log('📊 Chart defaults - Bachelor:', {bSalary, bDebt}, 'Master:', {mSalary, mDebt});

  // Generate initial projections with defaults (3% growth, 5% interest, 10-year repayment)
  const bProj = projectEarnings(bSalary, 3, 30, bDebt, 5, 10).map(p=>p.cumulativeNet);
  const mProj = projectEarnings(mSalary, 3, 30, mDebt, 5, 10).map(p=>p.cumulativeNet);

  // Hero mini chart (cumulative earnings over time)
  const heroEl = document.getElementById('heroMiniChart');
  if (heroEl && heroEl.getContext) {
    const heroCtx = heroEl.getContext('2d');
    try { if (heroMini) heroMini.destroy(); } catch(e){}
    heroMini = new Chart(heroCtx, {
      type:'line',
      data:{
        labels:years,
        datasets:[
          {label:'Bachelor',data:bProj,borderColor:'#2DE2E6',backgroundColor:'rgba(45,226,230,0.08)',tension:0.3,pointRadius:0,borderWidth:2},
          {label:'Master',data:mProj,borderColor:'#FF2A6D',backgroundColor:'rgba(255,42,109,0.06)',tension:0.3,pointRadius:0,borderWidth:2}
        ]
      },
      options:{
        responsive:true,
        maintainAspectRatio:false,
        plugins:{legend:{display:false}},
        elements:{line:{borderWidth:2}},
        scales:{y:{display:false},x:{display:false}}
      }
    });
  }

  // Break-even chart (cumulative earnings with intersection highlighting)
  const breakEl = document.getElementById('breakEvenChart');
  if (breakEl && breakEl.getContext) {
    const ctx = breakEl.getContext('2d');
    if (breakChart) try { breakChart.destroy(); } catch(e){}
    
    // Find break-even year
    let breakYear = '—';
    for (let i=0; i<years.length; i++){
      if (mProj[i] !== undefined && bProj[i] !== undefined && mProj[i] >= bProj[i]){ 
        breakYear = i; 
        break; 
      }
    }
    
    breakChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: years,
        datasets: [
          {
            label: 'Bachelor Path (Cumulative Net Earnings)',
            data: bProj,
            borderColor: '#2DE2E6',
            backgroundColor: 'rgba(45,226,230,0.06)',
            tension: 0.2,
            pointRadius: 0,
            borderWidth: 3,
            pointHoverRadius: 6
          },
          {
            label: 'Master Path (Cumulative Net Earnings)',
            data: mProj,
            borderColor: '#FF2A6D',
            backgroundColor: 'rgba(255,42,109,0.06)',
            tension: 0.2,
            pointRadius: 0,
            borderWidth: 3,
            pointHoverRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { 
          legend: { 
            position: 'top',
            labels: {color:'#e0e4e7', font: {size: 13, weight: '600'}, padding: 16}
          },
          tooltip: {
            backgroundColor: 'rgba(0,0,0,0.8)',
            titleColor: '#fff',
            titleFont: {size: 14, weight: '600'},
            bodyColor: '#e0e4e7',
            bodyFont: {size: 13},
            borderColor: 'rgba(45,226,230,0.3)',
            borderWidth: 1,
            padding: 10,
            callbacks:{
              label:function(ctx){return ctx.dataset.label+': $'+ctx.parsed.y.toLocaleString();}
            }
          }
        },
        scales: {
          y: { 
            title: { display: true, text: 'Cumulative Net Earnings (USD)', color:'#a5afb2', font: {size: 13, weight: '600'} },
            ticks: {callback:function(v){return '$'+(v/1000|0)+'k';}, color: '#a5afb2', font: {size: 12}},
            grid: {color:'rgba(255,255,255,0.05)'},
            beginAtZero: true
          },
          x: { 
            title: { display: true, text: 'Years After Graduation', color:'#a5afb2', font: {size: 13, weight: '600'} },
            grid: {color:'rgba(255,255,255,0.05)'},
            ticks: {color: '#a5afb2', font: {size: 12}}
          }
        }
      }
    });

    const breakYearEl = document.getElementById('break-year'); 
    if (breakYearEl) breakYearEl.innerText = breakYear;
  }

  // Salary bar chart
  const salaryEl = document.getElementById('salaryBar');
  if (salaryEl && salaryEl.getContext) {
    const sctx = salaryEl.getContext('2d');
    if (salaryBar) try{ salaryBar.destroy(); } catch(e){}
    salaryBar = new Chart(sctx, {
      type:'bar',
      data:{
        labels:['Bachelor','Master'],
        datasets:[{label:'Starting Salary (USD)',data:[bSalary,mSalary],backgroundColor:['rgba(45,226,230,0.9)','rgba(255,42,109,0.9)'],borderColor:['#2DE2E6','#FF2A6D'],borderWidth:1}]
      },
      options:{
        responsive:true,
        maintainAspectRatio:false,
        indexAxis: 'y',
        plugins:{
          legend:{position:'top', labels: {font: {size: 12}, color: '#e0e4e7', padding: 12}},
          tooltip:{backgroundColor: 'rgba(0,0,0,0.8)', titleFont: {size: 13}, bodyFont: {size: 12}, borderColor: 'rgba(45,226,230,0.3)', borderWidth: 1, callbacks:{label:function(ctx){return '$'+ctx.parsed.x.toLocaleString();}}}
        },
        scales:{y:{ticks:{color:'#a5afb2', font: {size: 13}}}, x:{beginAtZero:true,ticks:{callback:function(v){return '$'+(v/1000|0)+'k';}, color: '#a5afb2', font: {size: 12}}, grid: {color: 'rgba(255,255,255,0.05)'}}}
      }
    });
  }

  // Debt bar chart
  const debtEl = document.getElementById('debtArea');
  if (debtEl && debtEl.getContext) {
    const dctx = debtEl.getContext('2d');
    if (debtArea) try{ debtArea.destroy(); } catch(e){}
    debtArea = new Chart(dctx,{
      type: 'bar',
      data: {
        labels: ['Bachelor','Master'],
        datasets: [
          { label: 'Average Debt After Graduation (USD)', data: [bDebt, mDebt], backgroundColor: ['rgba(45,226,230,0.9)','rgba(255,42,109,0.9)'], borderColor: ['#2DE2E6','#FF2A6D'], borderWidth:1 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: { 
          legend: { position: 'top', labels: {font: {size: 12}, color: '#e0e4e7', padding: 12} },
          tooltip:{backgroundColor: 'rgba(0,0,0,0.8)', titleFont: {size: 13}, bodyFont: {size: 12}, borderColor: 'rgba(45,226,230,0.3)', borderWidth: 1, callbacks:{label:function(ctx){return '$'+ctx.parsed.x.toLocaleString();}}}
        },
        scales: {
          y: { beginAtZero: true, ticks: {color:'#a5afb2', font: {size: 13}} },
          x: { beginAtZero: true, ticks: {callback:function(v){return '$'+(v/1000|0)+'k';}, color: '#a5afb2', font: {size: 12}}, grid: {color: 'rgba(255,255,255,0.05)'} }
        }
      }
    });
  }

  // Update hero stat
  const lifetimeDiff = (mProj[30] - bProj[30]);
  document.getElementById('lifetime-diff').innerText = lifetimeDiff ? `$${(lifetimeDiff/1000).toFixed(1)}k` : '—';

  // Update summary cards
  const setIf = (id, val) => { const el = document.getElementById(id); if (!el) return; el.innerText = val; };
  setIf('b-salary', stats.bachelor.avgSalary ? `$${stats.bachelor.avgSalary.toLocaleString()}` : `$${bSalary.toLocaleString()}`);
  setIf('m-salary', stats.master.avgSalary ? `$${stats.master.avgSalary.toLocaleString()}` : `$${mSalary.toLocaleString()}`);
  setIf('b-debt', stats.bachelor.avgDebt ? `$${stats.bachelor.avgDebt.toLocaleString()}` : `$${bDebt.toLocaleString()}`);
  setIf('m-debt', stats.master.avgDebt ? `$${stats.master.avgDebt.toLocaleString()}` : `$${mDebt.toLocaleString()}`);
  setIf('b-roi', bProj[30] ? `$${bProj[30].toLocaleString()}` : '—');
  setIf('m-roi', mProj[30] ? `$${mProj[30].toLocaleString()}` : '—');
}

/**
 * Compute full ROI with all financial metrics and update all charts
 */
function computeROI() {
  try {
    // Get all input elements
    const bDebtEl = document.getElementById('bachelor-debt');
    const mDebtEl = document.getElementById('master-debt');
    const repaymentEl = document.getElementById('repayment-period');
    const interestEl = document.getElementById('interest');
    const bSalaryEl = document.getElementById('bachelor-salary');
    const mSalaryEl = document.getElementById('master-salary');
    const growthEl = document.getElementById('growth');
    const taxRateEl = document.getElementById('tax-rate');
    const locationEl = document.getElementById('location-tier');
    
    // Safety check
    if (!bDebtEl || !mDebtEl || !repaymentEl || !interestEl || !bSalaryEl || !mSalaryEl || !growthEl) {
      console.warn('❌ Some ROI input elements missing');
      return;
    }
    
    // Get values
    const bDebt = Number(bDebtEl.value);
    const mDebt = Number(mDebtEl.value);
    const repaymentYears = Number(repaymentEl.value);
    const interestRate = Number(interestEl.value);
    const bStartSalary = Number(bSalaryEl.value);
    const mStartSalary = Number(mSalaryEl.value);
    const growthRate = Number(growthEl.value);
    const taxRate = Number((taxRateEl && taxRateEl.value) || 0);
    const costIndex = Number((locationEl && locationEl.value) || 1);
    
    console.log('🧮 ROI Calculation:', {bDebt, mDebt, repaymentYears, interestRate, bStartSalary, mStartSalary, growthRate, taxRate, costIndex});
    
    // Calculate monthly payments
    const bMonthly = calculateMonthlyPayment(bDebt, interestRate, repaymentYears);
    const mMonthly = calculateMonthlyPayment(mDebt, interestRate, repaymentYears);
    
    console.log('💳 Monthly Payments - Bachelor: $' + bMonthly.toFixed(2) + ', Master: $' + mMonthly.toFixed(2));
    
    // Generate full 30-year projections for both paths
    const bProjection = projectEarnings(bStartSalary, growthRate, 30, bDebt, interestRate, repaymentYears, {
      taxRate,
      costIndex
    });
    const mProjection = projectEarnings(mStartSalary, growthRate, 30, mDebt, interestRate, repaymentYears, {
      taxRate,
      costIndex
    });
    
    // Find break-even year
    let breakEvenYear = 'Not Possible';
    for (let i = 0; i <= 30; i++) {
      if (mProjection[i] && bProjection[i] && mProjection[i].cumulativeNet >= bProjection[i].cumulativeNet) {
        breakEvenYear = i;
        console.log(`✓ Break-even at year ${i}`);
        break;
      }
    }
    
    // Extract cumulative values for charting
    const years = Array.from({length: 31}, (_, i) => i);
    const bCumulative = bProjection.map(p => p.cumulativeNet);
    const mCumulative = mProjection.map(p => p.cumulativeNet);
    
    // Calculate annual salary advantage (gross salary difference)
    const annualAdvantage = [];
    for (let i = 0; i <= 30; i++) {
      const bAnnual = bProjection[i].netEarningsThisYear;
      const mAnnual = mProjection[i].netEarningsThisYear;
      annualAdvantage.push(mAnnual - bAnnual);
    }
    
    // Calculate ROI (cumulative advantage over time)
    const roiOverTime = [];
    for (let i = 0; i <= 30; i++) {
      roiOverTime.push(mCumulative[i] - bCumulative[i]);
    }
    
    // 30-year totals
    const bTotal30 = bCumulative[30];
    const mTotal30 = mCumulative[30];
    const advantage30 = mTotal30 - bTotal30;
    
    console.log('📊 Results:', {breakEvenYear, bTotal30, mTotal30, advantage30});
    
    // Update output display
    document.getElementById('roi-break').innerText = breakEvenYear;
    document.getElementById('bachelor-monthly').innerText = '$' + bMonthly.toFixed(2) + '/mo';
    document.getElementById('master-monthly').innerText = '$' + mMonthly.toFixed(2) + '/mo';
    document.getElementById('roi-profit').innerText = advantage30 >= 0 
      ? `Gain $${Math.abs(advantage30).toLocaleString()}` 
      : `Loss $${Math.abs(advantage30).toLocaleString()}`;
    document.getElementById('roi-bachelor-total').innerText = '$' + bTotal30.toLocaleString();
    document.getElementById('roi-master-total').innerText = '$' + mTotal30.toLocaleString();

    const advantage15 = mCumulative[15] - bCumulative[15];
    const summary15 = document.getElementById('summary-15y');
    if (summary15) {
      summary15.innerText = `After 15 years: ${advantage15 >= 0 ? 'Master leads by' : 'Bachelor leads by'} $${Math.abs(advantage15).toLocaleString()}.`;
    }
    const summaryBreak = document.getElementById('summary-breakeven');
    if (summaryBreak) {
      summaryBreak.innerText = breakEvenYear === 'Not Possible'
        ? 'Break-even outlook: Master path does not break even within 30 years under current assumptions.'
        : `Break-even outlook: Master path overtakes Bachelor in year ${breakEvenYear}.`;
    }
    const retirementValue = Math.round(Math.max(0, advantage30) * 1.07);
    const summaryRetire = document.getElementById('summary-retirement');
    if (summaryRetire) {
      summaryRetire.innerText = `Projected additional retirement value: $${retirementValue.toLocaleString()} (illustrative 7% growth estimate).`;
    }
    
    // Update quick advantage (top right card)
    const quickAdvEl = document.getElementById('quick-advantage');
    if (quickAdvEl) {
      quickAdvEl.innerText = advantage30 >= 0 
        ? '$' + Math.abs(advantage30).toLocaleString() 
        : '-$' + Math.abs(advantage30).toLocaleString();
    }

    updateQualitativeInsight(advantage30);
    
    // Update Break-Even Chart
    if (breakChart) {
      breakChart.data.labels = years;
      breakChart.data.datasets[0].data = bCumulative;
      breakChart.data.datasets[1].data = mCumulative;
      const pointRadius = getChartPointRadius();
      breakChart.data.datasets[0].pointRadius = pointRadius;
      breakChart.data.datasets[1].pointRadius = pointRadius;
      breakChart.update();
    }
    
    // Update Hero Mini Chart
    if (heroMini) {
      heroMini.data.labels = years;
      heroMini.data.datasets[0].data = bCumulative;
      heroMini.data.datasets[1].data = mCumulative;
      const pointRadius = getChartPointRadius();
      heroMini.data.datasets[0].pointRadius = pointRadius;
      heroMini.data.datasets[1].pointRadius = pointRadius;
      heroMini.update();
    }
    
    // Update Salary Bar Chart
    if (salaryBar) {
      salaryBar.data.datasets[0].data = [bStartSalary, mStartSalary];
      salaryBar.update();
    }
    
    // Update Debt Bar Chart
    if (debtArea) {
      debtArea.data.datasets[0].data = [bDebt, mDebt];
      debtArea.update();
    }
    
    // Update ROI vs Time Chart
    updateOrCreateROIVsTimeChart(years, roiOverTime);
    
    // Update Annual Advantage Chart
    updateOrCreateAnnualAdvantageChart(years, annualAdvantage);
    
    // Update hero lifetime difference
    const lifetimeDiff = advantage30;
    const lifetimeDiffEl = document.getElementById('lifetime-diff');
    if (lifetimeDiffEl) {
      lifetimeDiffEl.innerText = lifetimeDiff ? `$${(lifetimeDiff / 1000).toFixed(1)}k` : '—';
    }
    
    console.log('✅ computeROI complete');
    
  } catch (err) {
    console.error('❌ computeROI failed:', err);
  }
}

/**
 * Create or update the ROI vs Time chart (cumulative advantage)
 */
function updateOrCreateROIVsTimeChart(years, roiData) {
  const roiEl = document.getElementById('roiVsTimeChart');
  if (!roiEl || !roiEl.getContext) return;
  
  const ctx = roiEl.getContext('2d');
  if (roiVsTimeChart) try { roiVsTimeChart.destroy(); } catch(e){}
  const pointRadius = getChartPointRadius();
  
  roiVsTimeChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: years,
      datasets: [
        {
          label: "Master's Financial Advantage (Cumulative)",
          data: roiData,
          borderColor: '#2DE2E6',
          backgroundColor: 'rgba(45,226,230,0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: pointRadius,
          borderWidth: 2,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: {font: {size: 12}, color:'#e0e4e7', padding: 12} },
        tooltip: {
          backgroundColor: 'rgba(0,0,0,0.8)',
          titleColor: '#fff',
          titleFont: {size: 13},
          bodyColor: '#e0e4e7',
          bodyFont: {size: 12},
          borderColor: 'rgba(45,226,230,0.3)',
          borderWidth: 1,
          callbacks: {
            label: function(ctx){
              return 'Advantage: $' + ctx.parsed.y.toLocaleString();
            }
          }
        }
      },
      scales: {
        y: {
          title: { display: true, text: 'Cumulative Advantage (USD)', color:'#a5afb2', font: {size: 13, weight: '600'} },
          ticks: {callback:function(v){return '$'+(v/1000|0)+'k';}, color: '#a5afb2', font: {size: 12}},
          grid: {color:'rgba(255,255,255,0.05)'}
        },
        x: {
          title: { display: true, text: 'Years After Graduation', color:'#a5afb2', font: {size: 13, weight: '600'} },
          grid: {color:'rgba(255,255,255,0.05)'},
          ticks: {color: '#a5afb2', font: {size: 12}}
        }
      }
    }
  });
}

/**
 * Create or update the Annual Advantage chart (year-over-year benefit)
 */
function updateOrCreateAnnualAdvantageChart(years, advantageData) {
  const advEl = document.getElementById('annualAdvantageChart');
  if (!advEl || !advEl.getContext) return;
  
  const ctx = advEl.getContext('2d');
  if (annualAdvantageChart) try { annualAdvantageChart.destroy(); } catch(e){}
  const selectedType = getAnnualChartType();
  const pointRadius = getChartPointRadius();
  
  // Determine color based on positive/negative
  const colors = advantageData.map(v => v >= 0 ? 'rgba(45,226,230,0.8)' : 'rgba(255,42,109,0.8)');
  
  annualAdvantageChart = new Chart(ctx, {
    type: selectedType,
    data: {
      labels: years,
      datasets: [
        {
          label: "Annual Net Salary Advantage (Master - Bachelor)",
          data: advantageData,
          backgroundColor: colors,
          borderColor: '#2DE2E6',
          borderRadius: 4,
          borderSkipped: false,
          pointRadius: pointRadius,
          tension: 0.2,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: {font: {size: 12}, color:'#e0e4e7', padding: 12} },
        tooltip: {
          backgroundColor: 'rgba(0,0,0,0.8)',
          titleColor: '#fff',
          titleFont: {size: 13},
          bodyColor: '#e0e4e7',
          bodyFont: {size: 12},
          borderColor: 'rgba(45,226,230,0.3)',
          borderWidth: 1,
          callbacks: {
            label: function(ctx){
              return ctx.parsed.y >= 0 
                ? 'Master Advantage: $' + ctx.parsed.y.toLocaleString()
                : 'Bachelor Advantage: $' + Math.abs(ctx.parsed.y).toLocaleString();
            }
          }
        }
      },
      scales: {
        y: {
          title: { display: true, text: 'Annual Advantage (USD)', color:'#a5afb2', font: {size: 13, weight: '600'} },
          ticks: {callback:function(v){return '$'+(v/1000|0)+'k';}, color: '#a5afb2', font: {size: 12}},
          grid: {color:'rgba(255,255,255,0.05)'}
        },
        x: {
          title: { display: true, text: 'Years After Graduation', color:'#a5afb2', font: {size: 13, weight: '600'} },
          grid: {color:'rgba(255,255,255,0.05)'},
          ticks: {color: '#a5afb2', font: {size: 12}}
        }
      }
    }
  });
}

function updateQualitativeInsight(advantage30) {
  const worklife = Number((document.getElementById('q-worklife') || {}).value || 2);
  const career = Number((document.getElementById('q-career') || {}).value || 2);
  const debt = Number((document.getElementById('q-debt') || {}).value || 2);
  const insightEl = document.getElementById('qualitative-insight');
  if (!insightEl) return;

  let recommendation = 'Balanced profile: review both financial and lifestyle factors before deciding.';
  if (advantage30 >= 0 && career >= 2 && debt >= 2) {
    recommendation = 'Your profile favors a Master path financially and professionally, as long as debt remains manageable.';
  } else if (worklife >= 3 && debt <= 2) {
    recommendation = 'Your priorities suggest caution: a Bachelor path may better protect lifestyle flexibility and debt comfort.';
  } else if (advantage30 < 0) {
    recommendation = 'Current assumptions favor the Bachelor path financially; pursue Master mainly for non-financial goals.';
  }
  insightEl.innerText = recommendation;
}


/**
 * Setup ROI calculator with live updates from all inputs
 */
function setupROI() {
  console.log('🎚️ Setting up ROI calculator');
  
  // Get all input elements
  const inputs = {
    'bachelor-debt': document.getElementById('bachelor-debt'),
    'master-debt': document.getElementById('master-debt'),
    'repayment-period': document.getElementById('repayment-period'),
    'interest': document.getElementById('interest'),
    'bachelor-salary': document.getElementById('bachelor-salary'),
    'master-salary': document.getElementById('master-salary'),
    'growth': document.getElementById('growth'),
    'tax-rate': document.getElementById('tax-rate')
  };
  
  // Get all numeric number input elements (for dual control)
  const numInputs = {
    'bachelor-debt-num': document.getElementById('bachelor-debt-num'),
    'master-debt-num': document.getElementById('master-debt-num'),
    'repayment-period-num': document.getElementById('repayment-period-num'),
    'interest-num': document.getElementById('interest-num'),
    'bachelor-salary-num': document.getElementById('bachelor-salary-num'),
    'master-salary-num': document.getElementById('master-salary-num'),
    'growth-num': document.getElementById('growth-num'),
    'tax-rate-num': document.getElementById('tax-rate-num')
  };
  
  // Get all display value elements
  const displays = {
    'bachelor-debt': document.getElementById('bachelor-debt-val'),
    'master-debt': document.getElementById('master-debt-val'),
    'repayment-period': document.getElementById('repayment-period-val'),
    'interest': document.getElementById('interest-val'),
    'bachelor-salary': document.getElementById('bachelor-salary-val'),
    'master-salary': document.getElementById('master-salary-val'),
    'growth': document.getElementById('growth-val'),
    'tax-rate': document.getElementById('tax-rate-val')
  };
  
  // Safety check
  if (!inputs['bachelor-debt'] || !inputs['growth']) {
    console.error('❌ Missing slider elements');
    return;
  }
  
  // Update display values
  function updateDisplay(fieldKey, value) {
    const display = displays[fieldKey];
    if (!display) return;
    
    // Also update the number input field with nice formatting for currency fields
    const numInput = numInputs[fieldKey + '-num'];
    if (numInput && (fieldKey.includes('debt') || fieldKey.includes('salary'))) {
      const numVal = Number(value);
      numInput.value = numVal.toLocaleString('en-US', {maximumFractionDigits: 0});
    }
    
    if (fieldKey === 'repayment-period') {
      display.innerText = value + ' years';
    } else if (fieldKey === 'interest' || fieldKey === 'growth' || fieldKey === 'tax-rate') {
      display.innerText = Number(value).toFixed(1) + '%';
    } else {
      display.innerText = '$' + Number(value).toLocaleString('en-US', {maximumFractionDigits: 0});
    }
  }
  
  // Sync slider and number inputs, update display, and recalculate
  function syncAndCalculate(fieldKey) {
    const slider = inputs[fieldKey];
    const numInput = numInputs[fieldKey + '-num'];
    
    if (!slider) return;
    if (!numInput) {
      updateDisplay(fieldKey, Number(slider.value));
      return;
    }
    
    if (numInput === document.activeElement) {
      const rawNumVal = numInput.value.replace(/[^0-9.-]/g, '');
      const numVal = Number(rawNumVal) || 0;
      const min = Number(slider.min);
      const max = Number(slider.max);
      slider.value = Math.max(min, Math.min(max, numVal));
    } else {
      numInput.value = slider.value;
    }
    
    const finalValue = Number(slider.value);
    updateDisplay(fieldKey, finalValue);
  }
  
  // Add blur handler for proper number formatting
  Object.keys(numInputs).forEach(key => {
    const numInput = numInputs[key];
    if (!numInput) return;
    
    // Add input validation and formatting
    numInput.addEventListener('input', function() {
      const fieldKey = key.replace('-num', '');
      // Allow only digits
      this.value = this.value.replace(/[^0-9.-]/g, '');
    });
    
    numInput.addEventListener('blur', function() {
      const fieldKey = key.replace('-num', '');
      const rawVal = this.value.replace(/[^0-9.-]/g, '');
      let numVal = Number(rawVal) || 0;
      const slider = inputs[fieldKey];
      
      if (slider) {
        const min = Number(slider.min);
        const max = Number(slider.max);
        // Clamp and validate
        numVal = Math.max(min, Math.min(max, numVal));
        slider.value = numVal;
        updateDisplay(fieldKey, numVal);
        computeROI();
      }
    });
  });
  
  // Create unified event handler
  const handleChange = function() {
    const id = this.id.replace('-num', '');
    syncAndCalculate(id);
    computeROI();
  };

  const locationSelector = document.getElementById('location-tier');
  const locationVal = document.getElementById('location-tier-val');
  if (locationSelector) {
    locationSelector.addEventListener('change', () => {
      if (locationVal) {
        const multiplier = Number(locationSelector.value || 1).toFixed(2);
        locationVal.innerText = `x${multiplier}`;
      }
      computeROI();
    });
  }

  const chartToggle = document.getElementById('chart-show-points');
  if (chartToggle) chartToggle.addEventListener('change', () => computeROI());
  const chartTypeSelector = document.getElementById('annual-chart-type');
  if (chartTypeSelector) chartTypeSelector.addEventListener('change', () => computeROI());

  ['q-worklife', 'q-career', 'q-debt'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', () => computeROI());
  });
  
  // Attach listeners to all inputs
  Object.keys(inputs).forEach(key => {
    if (inputs[key]) {
      inputs[key].addEventListener('input', handleChange);
    }
    const numInput = numInputs[key + '-num'];
    if (numInput) {
      numInput.addEventListener('input', handleChange);
    }
  });
  
  console.log('✓ Event listeners attached');
  
  // Initialize display values
  Object.keys(inputs).forEach(key => {
    if (inputs[key]) {
      updateDisplay(key, inputs[key].value);
    }
  });

  if (locationSelector && locationVal) {
    locationVal.innerText = `x${Number(locationSelector.value || 1).toFixed(2)}`;
  }
  
  console.log('✓ Initial display values set');
  
  // Initial computation
  computeROI();
  
  console.log('✅ setupROI complete');
}

/**
 * Populate data sources in footer
 */
function populateSources() {
  const sourcesList = document.getElementById('sources-list');
  if (!sourcesList) return;
  
  const sources = [
    { text: 'Education Data: Student Loan Debt by Major', url: 'https://educationdata.org/student-loan-debt-by-major' },
    { text: 'GitHub: Degrees That Pay Back (ANLY 500)', url: 'https://github.com/YujiShen/anly-500-project/blob/master/degrees-that-pay-back.csv' },
    { text: 'College Scorecard: Official U.S. Education Department Data', url: 'https://collegescorecard.ed.gov/data/' }
  ];
  
  sourcesList.innerHTML = sources.map((src, idx) => 
    `<li><a href="${src.url}" target="_blank" rel="noopener noreferrer">${src.text}</a></li>`
  ).join('');
}

/**
 * Initialize everything when DOM is ready
 */
function init() {
  console.log('🚀 INIT STARTING');
  try {
    const stats = getDefaultStats();
    console.log('📊 Got default stats:', stats);
    CURRENT_STATS = stats;

    console.log('📈 Creating initial charts...');
    createCharts([], [], stats);

    console.log('🎚️ Setting up ROI calculator...');
    setupROI();
    
    console.log('📚 Populating data sources...');
    populateSources();
    console.log('✅ Initialization complete');
  } catch (err) {
    console.error('❌ Initialization error:', err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('📄 DOM Loaded');
  const startBtn = document.getElementById('start-explore');
  if (startBtn) {
    startBtn.addEventListener('click', ()=>{ 
      window.scrollTo({top:600,behavior:'smooth'}); 
    });
  }
  init();
});
