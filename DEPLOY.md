# Deployment

## Railway (recommended for this repo)

1. **New project → Deploy from GitHub** (or CLI) using this repository.
2. **Root directory**: leave as **repo root** (folder that contains `requirements.txt` and `slate/`).  
   `railway.toml` already runs `cd slate` for Django commands.
3. **Add Postgres**: **New** → **Database** → **PostgreSQL**. Railway injects **`DATABASE_URL`** into the web service — no manual `DB_*` vars needed.
4. **Variables** on the **web** service (minimum for production):

| Variable | Example | Notes |
|----------|---------|--------|
| `DJANGO_DEBUG` | `False` | Required for production behaviour |
| `DJANGO_SECRET_KEY` | *(long random string)* | Not `django-insecure-…` |
| `ALLOWED_HOSTS` | `yourapp.up.railway.app` | Comma-separated if several |
| `CSRF_TRUSTED_ORIGINS` | `https://yourapp.up.railway.app` | Optional if unset: **`RAILWAY_PUBLIC_DOMAIN`** is appended automatically |

Railway also sets **`RAILWAY_PUBLIC_DOMAIN`**; the app adds it to **`ALLOWED_HOSTS`** and **`CSRF_TRUSTED_ORIGINS`** (`https://…`) so you can often omit those two if you only use the default Railway URL.

5. **Build / deploy** (from `railway.toml`):
   - **Build**: `pip install` + `collectstatic`
   - **Release**: `migrate`
   - **Start**: Gunicorn on **`$PORT`**
6. **Health check**: `GET /health/` → `200` + body `ok`.

**If health checks fail with “service unavailable”**: Probes use **HTTP** on the container without `X-Forwarded-Proto`. **`SECURE_SSL_REDIRECT`** defaults to **`False`** whenever **`DJANGO_DEBUG=False`** so probes are not redirected (TLS is still at Railway’s edge). Opt in with **`SECURE_SSL_REDIRECT=true`** only if your probes follow redirects.

**Database tables missing (`relation "log_household" does not exist`)**: Run migrations against the same database your app uses — locally: `cd slate && python manage.py migrate`. On Railway, **`startCommand`** runs **`migrate`** before Gunicorn so a fresh Postgres gets tables even if the release phase did not run.

### Custom domain

Add the domain in Railway, then set:

- `ALLOWED_HOSTS` to include your hostname(s)
- `CSRF_TRUSTED_ORIGINS` to include `https://yourdomain.com`

### Procfile

If you prefer Railway’s **Procfile** detection instead of `railway.toml` `[deploy]`, the repo root **Procfile** is still valid; remove or adjust `startCommand` / `releaseCommand` in `railway.toml` to avoid duplication.

---

## Environment variables (general)

| Variable | Required | Notes |
|----------|----------|--------|
| `DATABASE_URL` | On Railway Postgres | Set automatically when DB is linked |
| `DJANGO_DEBUG` | Yes in prod | `False` |
| `DJANGO_SECRET_KEY` | Yes in prod | Strong random secret |
| `ALLOWED_HOSTS` | Yes* | *Auto-filled from `RAILWAY_PUBLIC_DOMAIN` on Railway |
| `CSRF_TRUSTED_ORIGINS` | Yes* | *HTTPS origin auto-added for Railway public domain |
| `DB_*` | Local / non-Railway | If no `DATABASE_URL` |
| `PORT` | PaaS | Set by Railway |
| `WEB_CONCURRENCY` | Optional | Gunicorn workers (default `2`) |

## Static files

WhiteNoise serves **`slate/staticfiles/`** after `collectstatic` (included in the Railway **build** step).
