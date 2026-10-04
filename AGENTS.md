## Harness

- 与用户交流时尽量使用常见词汇，必要的专业名词需说明含义。
- 首次实现项目功能时，除非用户要求，不加入按时间或长度提前结束、截断或降级的兜底。
- 比赛引用评分只依据官方随包分发、可核验的语料原文。独立保存的链接原文可在遵守来源条款时用于研究；除非组织方正式将其加入并映射到分发语料，否则不计入引用评分。
- 参赛视频展示本队系统的实际输出和自行验证过程。本届不向参赛者提供 `score.py` 或开发集答案；不要展示 `score.py` 评分结果。
- 评估代码、输入配置和整理后的汇总报告可以提交；逐次运行结果、原始调用记录和追踪文件只保留在本地，不纳入 Git。

## Lovable preview app

- All `/api/*` calls are answered live by the original navigator TypeScript (`navigator/src`, imported unchanged via the `navigator-core/` alias) through `src/routes/api/$.ts`; a Vite plugin redirects its `node:fs`/`node:url`/`http.js` to in-memory/fetch shims in `src/lib/navcore/` because the Worker has no disk. Read-only data is bundled from `navigator/` and `starter-pack/` at build time; `public/navigator/data/` is no longer used.
- Files under `/nav/work/law_imports/` are mirrored to the `nav_files` table per request; law-import extraction runs in a separate `/api/imports/<id>/run` request opened by the page, with a heartbeat file marking it alive.
- `public/navigator/` is a three-way merge of `navigator/web/static/` (user's source of truth for features) with the preview's styling/copy edits; re-merge with `git merge-file` when the user pushes new frontend changes, never overwrite either side.
- The online "/api/summary" is a TanStack server route (`src/routes/api/summary.ts` + `src/lib/navigator-summary.server.ts`) ported from `navigator/src/web/summary.ts`; it uses the live lookup, calls DeepSeek with `DEEPSEEK_API_KEY`, and caches validated paragraphs in the `summary_cache` table because the Worker has no writable disk. Keep prompt/validation in sync with the Node original.
