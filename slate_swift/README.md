# Slate (iOS)

Native SwiftUI client for the Slate daily spending log. The Django backend uses **session cookies** for the web app and **`Authorization: Token <uuid>`** for this app (tokens are stored on `Member.api_token`, not DRF’s `User`-bound authtoken).

## Link to Railway (API URL)

The app reads **`Config.baseURL`**, which should match your deployed Django root on Railway.

**Single source of truth:** put the public HTTPS URL in the **repo root `.env`**:

```env
SLATE_API_BASE_URL=https://your-service.up.railway.app
```

No trailing slash. Find the URL in **Railway → your service → Settings → Networking / Domains**.

Then from the **repository root** run:

```bash
python3 scripts/sync_ios_config.py
```

That updates `Slate/slate/slate/Config.swift`. Rebuild the Xcode project.

## Project layout (this repo)

The Xcode project lives under **`Slate/slate/`**. The app target uses a **folder-synced** group, so **all Swift sources must live inside** `Slate/slate/slate/` (next to `Assets.xcassets`). The entry point is **`slateApp.swift`** with `@main`.

## Open in Xcode

1. Open **`Slate/slate/slate.xcodeproj`**.
2. Set **`SLATE_API_BASE_URL`** in `.env` and run **`python3 scripts/sync_ios_config.py`** (see above).
3. **Signing & Capabilities** → select your team.
4. **Info** → add **Privacy – User Notifications Usage Description** (`NSUserNotificationsUsageDescription`):  
   `Slate can remind you once a day to log what you spent.`
5. Build & run (iOS **17+**).

## Backend

Deploy the Django project and run migrations so `Member.api_token` exists:

```bash
python manage.py migrate
```

The app calls:

- `POST /create/`, `POST /join/` — JSON; responses include `token`, `member_name`, `member_colour`.
- `POST /log/entry/` — `Authorization: Token …`
- `GET /log/entries/{year}/{month}/` — same header.

## Design

Colours and typography follow the web app: warm paper background, Georgia wordmark `slate.` (accent dot), SF Pro body (light/medium), serif amounts. The web app uses **Lora** in CSS; iOS uses **Georgia** as the bundled serif — spacing and weight may differ slightly.
