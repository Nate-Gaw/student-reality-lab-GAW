import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const dataDir = path.join(root, 'data');

function parseMoney(value) {
  if (!value) return 0;
  const num = Number(String(value).replace(/[^\d.-]/g, ''));
  return Number.isFinite(num) ? num : 0;
}

async function readText(fileName) {
  return readFile(path.join(dataDir, fileName), 'utf8');
}

function extractDebtMetricsFromNerdWallet(csvText) {
  const lines = csvText.split(/\r?\n/).filter(Boolean);
  let bachelorDebt = 29300;
  let masterDebt = 77300;

  for (const line of lines.slice(1)) {
    const [type, value] = line.split(',');
    if (!type || !value) continue;
    if (/Bachelor/i.test(type)) bachelorDebt = parseMoney(value);
    if (/Graduate/i.test(type)) masterDebt = parseMoney(value);
  }

  return { bachelorDebt, masterDebt };
}

function extractSalaryMetricsFromComparison(csvText) {
  const lines = csvText.split(/\r?\n/).filter(Boolean);
  let bachelorSalary = 85500;
  let masterSalary = 95400;
  let sampleCategory = 'General';

  for (const line of lines.slice(1)) {
    const parts = line.split(',');
    if (parts.length < 5) continue;
    const category = parts[0]?.trim();
    const bIncome = Number(parts[1]);
    const mIncome = Number(parts[3]);

    if (!Number.isFinite(bIncome) || !Number.isFinite(mIncome)) continue;

    if (/General/i.test(category) || /CS - All/i.test(category)) {
      bachelorSalary = bIncome;
      masterSalary = mIncome;
      sampleCategory = category;
      break;
    }
  }

  return { bachelorSalary, masterSalary, sampleCategory };
}

async function main() {
  const nerdWalletCsv = await readText('NerdWalletAvgLoanDebt.csv');
  const comparisonCsv = await readText('cs_degree_comparison.csv');
  const sourcesText = await readText('sources.txt');

  const debt = extractDebtMetricsFromNerdWallet(nerdWalletCsv);
  const salary = extractSalaryMetricsFromComparison(comparisonCsv);

  const processed = {
    contractVersion: '1.0.0',
    generatedAt: new Date().toISOString(),
    units: {
      currency: 'USD',
      timeframe: 'annual'
    },
    definitions: {
      breakEven: 'First year where Master cumulative net earnings are greater than or equal to Bachelor cumulative net earnings.',
      roi30Year: 'Difference between Master and Bachelor cumulative net earnings at year 30.',
      debt: 'Total education debt at graduation used as principal for amortized repayment.'
    },
    metrics: {
      bachelorSalary: salary.bachelorSalary,
      masterSalary: salary.masterSalary,
      bachelorDebt: debt.bachelorDebt,
      masterDebt: debt.masterDebt,
      sampleCategory: salary.sampleCategory
    },
    sources: sourcesText.split(/\r?\n/).filter(Boolean)
  };

  const target = path.join(dataDir, 'processed.json');
  await writeFile(target, `${JSON.stringify(processed, null, 2)}\n`, 'utf8');
  console.log(`Generated ${target}`);
}

main().catch((error) => {
  console.error('Failed to build processed data:', error);
  process.exit(1);
});
