# Rental Housing Law Navigator

The Rental Housing Law Navigator helps people review rental housing rules for a property address and a selected date. It shows the rule, its status, and the source text used for the result. This project was built for the Hack-Nation RealPage challenge.

## What you can do

- Look up rental rules by address and review the rules that apply on a chosen date.
- Open the cited law text and see why a rule applies, needs review, has not taken effect, or has been replaced.
- Compare rule coverage before and after a law change, including the affected addresses.
- Paste law text or upload a `.txt` file for rule extraction. Review the extracted rules and their address impact before applying them.
- Read query summaries in English, Spanish, or Chinese, with citations linked to the supporting result.

The Navigator provides information for research and is not legal advice. Coverage depends on the laws and address data available to the project; check the cited source before relying on a result.

## Run locally

You need Node.js and npm.

```sh
git clone https://github.com/hrhgit/hack-nation-refined.git
cd hack-nation-refined
npm install
npm run dev
```

The local development server prints its address when it starts. The app's data-backed API features use Supabase, and law extraction and query summaries use DeepSeek. Configure `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_PUBLISHABLE_KEY`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, and `DEEPSEEK_API_KEY` in the appropriate local or deployment environment. Keep `SUPABASE_SERVICE_ROLE_KEY` and `DEEPSEEK_API_KEY` server-side; never expose them in browser code. Database tables are defined in [`drizzle/migrations/`](drizzle/migrations/).

## How it works

The web app uses React, TypeScript, and TanStack Start. API requests run the original Navigator TypeScript from `navigator/src`; the Vite build redirects its file and HTTP access to in-memory and `fetch` adapters for the Worker runtime. Read-only laws, address facts, and challenge data are bundled from `navigator/` and `starter-pack/` at build time. Supabase stores submitted law text and validated summary results.

For the original Navigator's extraction, address lookup, change tracking, and evaluation workflows, see [`navigator/README.md`](navigator/README.md).

## Main folders

- `src/` — web app, API routes, and runtime adapters.
- `navigator/` — Navigator source, law and address data, and project documentation.
- `starter-pack/` — challenge materials and distributed source texts.
- `drizzle/migrations/` — database table definitions.
- `submission/` — team introduction and technical walkthrough materials.
