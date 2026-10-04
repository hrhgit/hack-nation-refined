CREATE TABLE public.nav_files (
  path text PRIMARY KEY,
  content text NOT NULL,
  mtime_ms double precision NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);
GRANT ALL ON public.nav_files TO service_role;
ALTER TABLE public.nav_files ENABLE ROW LEVEL SECURITY;