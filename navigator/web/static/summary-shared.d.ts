export function summaryEvidence(data: Record<string, any>): Record<string, any>;
export function canonicalJson(value: unknown): string;
export function summaryFingerprint(data: Record<string, any>): Promise<string>;
export function lineReader(onLine: (line: string) => void): {push(text: string): void; end(): void};
