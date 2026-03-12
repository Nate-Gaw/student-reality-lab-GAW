export interface ProcessedMetrics {
  bachelorSalary: number;
  masterSalary: number;
  bachelorDebt: number;
  masterDebt: number;
  sampleCategory: string;
}

export interface ProcessedContract {
  contractVersion: string;
  generatedAt: string;
  units: {
    currency: 'USD';
    timeframe: 'annual';
  };
  definitions: {
    breakEven: string;
    roi30Year: string;
    debt: string;
  };
  metrics: ProcessedMetrics;
  sources: string[];
}

export function isProcessedContract(value: unknown): value is ProcessedContract {
  if (!value || typeof value !== 'object') return false;
  const contract = value as Record<string, unknown>;

  return (
    typeof contract.contractVersion === 'string' &&
    typeof contract.generatedAt === 'string' &&
    typeof contract.units === 'object' &&
    typeof contract.metrics === 'object' &&
    Array.isArray(contract.sources)
  );
}

export function assertProcessedContract(value: unknown): ProcessedContract {
  if (!isProcessedContract(value)) {
    throw new Error('Invalid processed data contract.');
  }

  const contract = value as ProcessedContract;
  const { metrics } = contract;

  const numericFields: Array<keyof ProcessedMetrics> = [
    'bachelorSalary',
    'masterSalary',
    'bachelorDebt',
    'masterDebt'
  ];

  for (const field of numericFields) {
    if (!Number.isFinite(metrics[field])) {
      throw new Error(`Invalid numeric field in processed contract: ${field}`);
    }
  }

  return contract;
}
