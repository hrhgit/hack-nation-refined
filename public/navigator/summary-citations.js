// Keep the law's identifying number rather than a generic source symbol.
// These are display abbreviations; the full citation remains in the preview.
export function citationLabel(citation, rule = {}) {
  const cite = String(citation || '');
  const city = String(rule.jurisdiction || '').split(',')[0];
  const place = rule.level === 'state' ? rule.jurisdiction : ({
    'Los Angeles': 'LA', 'San Francisco': 'SF', 'San Diego': 'SD', 'Santa Ana': 'SA',
    Berkeley: 'BK', Boston: 'BOS', Cambridge: 'CAM', Hoboken: 'HOB', 'Jersey City': 'JC', Newark: 'NWK',
  }[city] || city.split(/\s+/).map(word => word[0]).join('').toUpperCase());
  const bill = cite.match(/\b(AB|SB)\s*(\d+)/i) || cite.match(/\b(H|S)\.(\d+)/);
  if (bill) return `${bill[1].toUpperCase()} ${bill[2]}`;
  const nj = cite.match(/N\.J\.(?:S\.A\.|A\.C\.)\s*([\dA-Z]+:[\dA-Z]+(?:[-.][\dA-Z]+)*)/);
  if (nj) return `NJ ${nj[1]}`;
  const sessionLaw = cite.match(/P\.L\.\s*(\d{4}),?\s*c\.\s*(\d+)/);
  if (sessionLaw) return `${place} ${sessionLaw[1]}:${sessionLaw[2]}`;
  const chapter = cite.match(/(?:\bc\.|\bch\.)\s*(\d[\dA-Z]*(?:[.:][\dA-Z]+)*)/i);
  const section = cite.match(/§+\s*([\dA-Z][\w.:\/–-]*(?:\s+1\/2)?)/i);
  if (section) return `${place || '§'} ${chapter ? chapter[1] + ':' : '§'}${section[1]}`;
  if (chapter) return `${place || 'Ch.'} ${chapter[1]}`;
  const cmr = cite.match(/(\d+)\s+CMR\s+([\d.]+)/);
  if (cmr) return `MA ${cmr[1]}:${cmr[2]}`;
  const motion = cite.match(/C\.F\.\s*([\d-]+)/);
  if (motion) return `${place} ${motion[1]}`;
  const petition = cite.match(/Petition\s*([\d-]+)/i);
  if (petition) return `${place} ${petition[1]}`;
  const ordinance = cite.match(/#(\d+)/);
  if (ordinance) return `${place} ${ordinance[1]}`;
  const acronym = cite.match(/\(([A-Z]{2,})\)/);
  if (acronym) return `${place} ${acronym[1]}`;
  // Named ordinances have no section number. Their title initials still let a
  // reader tell sources apart; no source text is shortened or discarded.
  const initials = cite.replace(city, '').split(/[^\p{L}\p{N}]+/u)
    .filter(word => word && !/^(and|of|the|in|et|seq)$/i.test(word))
    .map(word => word[0].toUpperCase()).join('');
  return `${place || ''} ${initials || cite}`.trim();
}

export function citationKind(ref) {
  return ref.result === 'unknown' || ref.result === 'applies' && ref.conflict_flag ? 'review'
    : ref.result === 'applies' ? 'applies' : ['pending', 'not_yet_effective'].includes(ref.result) ? 'inactive' : 'excluded';
}
