## Harness

- 与用户交流时尽量使用常见词汇，必要的专业名词需说明含义。
- 首次实现项目功能时，除非用户要求，不加入按时间或长度提前结束、截断或降级的兜底。
- 比赛引用评分只依据官方随包分发、可核验的语料原文。独立保存的链接原文可在遵守来源条款时用于研究；除非组织方正式将其加入并映射到分发语料，否则不计入引用评分。
- 参赛视频展示本队系统的实际输出和自行验证过程。本届不向参赛者提供 `score.py` 或开发集答案；不要展示 `score.py` 评分结果。
- 评估代码、输入配置和整理后的汇总报告可以提交；逐次运行结果、原始调用记录和追踪文件只保留在本地，不纳入 Git。

## Lovable preview app

- The Lovable preview (TanStack Start in `src/`) serves the original `navigator/web/static` frontend as a static snapshot from `public/navigator/`; answers are pre-dumped into `public/navigator/data/` from the Python web server (`python3 -m web`) because the preview has no Python runtime. Re-dump after `outputs/` or `work/` change.
- `public/navigator/` is a three-way merge of `navigator/web/static/` (user's source of truth for features) with the preview's styling/copy edits; re-merge with `git merge-file` when the user pushes new frontend changes, never overwrite either side.
- The online "/api/summary" is a TanStack server route (`src/routes/api/summary.ts` + `src/lib/navigator-summary.server.ts`) ported from `navigator/src/web/summary.ts`; it reads the lookup snapshot JSON, calls DeepSeek with `DEEPSEEK_API_KEY`, and caches validated paragraphs in the `summary_cache` table because the Worker has no writable disk. Keep prompt/validation in sync with the Node original.
- "/api/imports" is stubbed client-side in `public/navigator/index.html` (reports no model configured) until the extraction pipeline is ported.
