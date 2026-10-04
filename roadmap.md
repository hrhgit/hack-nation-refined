# Roadmap

## Waiting on user
- Choose how to bring the two new features into the preview: A) merge UI only, features show "local only"; B) pre-generate summary answers as static files so they show online. Law-import page stays local-only either way.
- Decide whether to publish the app now (no official URL yet).

## Open
- Merge user's pushed frontend changes into the preview copy under `public/navigator/` (currently only the old snapshot is served).
- Re-dump data snapshot after merge (`scripts/dump_navigator_data.py`).
- Verify address-query results render in the preview.

## Done
- Pulled user's GitHub commit (add law imports and cited summaries); compared both trees.
- Font and hierarchy pass: Public Sans + Literata, figure marks de-emphasized.
