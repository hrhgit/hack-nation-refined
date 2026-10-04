CREATE TABLE public.summary_cache (
  key text PRIMARY KEY,
  paragraphs jsonb NOT NULL,
  timings jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT ALL ON public.summary_cache TO service_role;
ALTER TABLE public.summary_cache ENABLE ROW LEVEL SECURITY;