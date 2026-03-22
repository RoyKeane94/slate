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
4. **Privacy & App Store**
   - **`PrivacyInfo.xcprivacy`** lives in `slate/` (folder-synced into the app bundle). It declares **no tracking**, **no collected data types**, and **UserDefaults** access with reason **CA92.1** (pending share code / local prefs).
   - **`NSUserNotificationsUsageDescription`** is set via build settings (`INFOPLIST_KEY_NSUserNotificationsUsageDescription`) on the **slate** target (Debug + Release).
   - **`ITSAppUsesNonExemptEncryption`** is set to **NO** for standard HTTPS-only traffic (adjust in Xcode if you add custom crypto).
5. Build & run (iOS **17+**).

## Backend

Deploy the Django project and run migrations so `Member.api_token` exists:

```bash
python manage.py migrate
```

The app calls:

- `POST /create/`, `POST /join/` — JSON; responses include `token`, `member_name`, `member_colour`.
- **Create:** send `name` and a **6-character** `code` (letters `a–z` except `i`, `l`, `o`, plus digits `2–9` — same alphabet in the app, web, and `slate/log/household_code.py`). Or omit `code` and the server will generate one.
- `POST /log/entry/` — `Authorization: Token …`
- `GET /log/entries/{year}/{month}/` — same header.

## Design

Colours and typography follow the web app: warm paper background, Georgia wordmark `slate.` (accent dot), SF Pro body (light/medium), serif amounts. The web app uses **Lora** in CSS; iOS uses **Georgia** as the bundled serif — spacing and weight may differ slightly.
