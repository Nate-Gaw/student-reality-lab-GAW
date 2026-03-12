import { assertProcessedContract, ProcessedContract } from './schema';

export async function loadProcessedData(url = '/data/processed.json'): Promise<ProcessedContract> {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to load processed data from ${url}: ${response.status}`);
  }

  const payload: unknown = await response.json();
  return assertProcessedContract(payload);
}
