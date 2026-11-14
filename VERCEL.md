# Deploying APIx on Vercel

One Vercel project runs the whole app (dashboard, `/public`, keyed `/v1`,
`/docs`, `/console`) as a single Python function. No frontend split.

## What happens on deploy

1. Vercel installs `pyproject.toml` (the serving subset, locked in `uv.lock`).
2. Build runs `python -m scripts.vercel_build`: unpacks `data/seed` into
   Bronze, rebuilds Silver and Gold into `apix.db`, and creates the operator
   account from env vars. About 10 seconds.
3. At runtime the app copies `apix.db` to `/tmp` (the bundle is read-only)
   and serves from there, with the scheduler off and the clock in IST.

## Steps

1. vercel.com → **Add New → Project** → import this repo. Framework preset:
   **FastAPI** (auto-detected). Root directory: the repo root. Leave the
   build and install commands empty.
2. **Environment Variables** (Production and Preview):

   | Name | Value |
   |---|---|
   | `APIX_SECRET` | output of `python -c "import secrets;print(secrets.token_urlsafe(48))"` |
   | `APIX_ADMIN_EMAIL` | the email you'll sign in to `/console` with |
   | `APIX_ADMIN_PASSWORD` | at least 10 characters |

3. **Deploy**. Then check `/v1/health` (should show `published_days` > 0),
   `/`, `/docs`, and sign in at `/login`.

Changing an env var needs a **Redeploy** to take effect (the admin account
is created at build time).

## Limits

- **Console writes are temporary.** API keys minted in `/console`, failed
  login lockouts and the access log live in `/tmp` on one instance. They
  disappear when Vercel recycles it, and a key minted on one instance is not
  known to another. Persistent keys need a hosted database.
- **No collection here.** "Collect now" returns 409 on purpose. New data
  arrives by committing a new `data/seed/*.jsonl.gz` and redeploying.
- **The daily `collect` workflow's schedule is off by default.** Run it from
  the Actions tab, or uncomment the cron in `.github/workflows/collect.yml`.
