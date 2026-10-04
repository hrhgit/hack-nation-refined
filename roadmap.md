# Roadmap

## Waiting on user
- Decide whether to port the law-import (parse law text) pipeline online — large port (extraction agent, packets, lookup engine re-run over all addresses, DB storage, polling).
- Decide whether to publish the app now (no official URL yet).

## Open
- Re-dump data snapshot after merge (`scripts/dump_navigator_data.py`) — needs the local Python server; current snapshot still renders.

## Done
- Merged user's pushed frontend (summary box, parse-law page, imports entry) into `public/navigator/` keeping preview styling/copy.
- Online summary: server route + DeepSeek + database cache; verified end-to-end with cited paragraphs.
- Address-query results verified in preview.
- Font and hierarchy pass: Public Sans + Literata, figure marks de-emphasized.
