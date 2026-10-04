const NOT_A_CODE = /\bOrd(?:inance)?\b\.?\s*(?:No\.?)?\s*[\dA-Z]|C\.F\.|Council File|\bMotion\b|\bBill\b|\b[HS]\.\s?\d|\bP\.L\.|\bAB\s?\d|\bSB\s?\d/i;
const SECTION = /(§§?\s*|\bch(?:apter)?\.?\s*|\barticle\s+|\bart\.\s*)?(\d+(?:[:.]\d+)*(?:-\d+[0-9A-Za-z.]*)?)/i;
export function chapterOf(citation: string): string | null {
  if (!citation || NOT_A_CODE.test(citation)) return null;
  const m = citation.replace(/\([^)]*\)/g, ' ').match(SECTION);
  if (!m) return null;
  const marker = (m[1] ?? '').toLowerCase(), token = m[2];
  if (marker.startsWith('ch') || marker.startsWith('art') || token.includes(':')) return token.split('-')[0];
  if (token.includes('-')) {const head = token.split('-')[0]; return /^\d+$/.test(head) ? head : null;}
  const parts = token.split('.'); return parts.length >= 3 ? parts.slice(0, 2).join('.') : null;
}
export function chapterCitation(citation: string, chapter: string): string {
  const m = SECTION.exec(citation);
  return m ? (citation.slice(0, m.index) + 'ch. ' + chapter + citation.slice(m.index + m[0].length)).replaceAll('  ', ' ').trim() : citation;
}
