# AI News Social Media Agent

Pulls AI/tech/business news from RSS feeds, has Claude write original
summary or commentary posts about each story, and posts them to X
(Twitter), Facebook, LinkedIn, and Instagram — a few times a day via cron.

## Important reality check before you set this up

"Autopilot" is accurate for the posting mechanics, but **not** for getting
started — each platform requires you to register as a developer and get
approved before any automated posting works at all. Budget real time for
this part (Meta's review in particular can take days), and expect to test
in dry-run mode for a while before trusting it to post unsupervised.

Also worth knowing going in:
- **Instagram cannot post text-only content** — every post needs an image,
  which is why this includes a basic image generator + Imgur upload step.
- **X's free API tier is very limited** (often too limited for regular
  posting); you'll likely need a paid tier for reliable automated posting.
- **All four platforms' terms of service govern automated/bot content** —
  read them. Platforms can suspend accounts that violate spam or automation
  policies, so keep frequency reasonable and content genuinely valuable.
- Posts here are Claude's original commentary/summaries "inspired by" a
  headline — never verbatim copies of the source article — but you're
  still responsible for what goes out under your account. Skim generated
  posts periodically even once you trust the pipeline.

## Setting up API access (the part you asked for guidance on)

### 1. X (Twitter)
1. Apply at https://developer.twitter.com — create a developer account and an app.
2. In the app's settings, set permissions to **"Read and Write"**.
3. Generate: API Key, API Secret, Access Token, Access Token Secret.
4. Put all four in `.env`.
5. Note: as of recent pricing, posting via API typically requires at least
   the paid Basic tier — check current X API pricing before relying on this.

### 2. Facebook Page + Instagram (both go through Meta's Graph API)
1. Create a Meta developer account at https://developers.facebook.com.
2. Create an App (type: "Business").
3. Add the **Facebook Login** and **Instagram Graph API** products to the app.
4. You need: a Facebook **Page** you admin, and an **Instagram Business or
   Creator account** linked to that Page (convert in the Instagram app:
   Settings → Account type → switch to Professional, then link it to your
   Facebook Page under Settings → Linked Accounts).
5. Use the Graph API Explorer (in Meta's developer dashboard) to generate a
   **long-lived Page Access Token** with these permissions:
   `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`,
   `instagram_content_publish`.
6. Get your Page ID (Page Settings → About) and Instagram Business Account
   ID (Graph API Explorer: `GET /me/accounts` then
   `GET /{page-id}?fields=instagram_business_account`).
7. **App Review**: while your app is in "Development" mode, these
   permissions only work for accounts added as Admins/Testers on the app
   itself. To post from/to arbitrary accounts you'd submit for Meta's App
   Review — but for your own Page/IG account, Development mode is enough
   to get started.
8. Put `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`, and
   `INSTAGRAM_BUSINESS_ACCOUNT_ID` in `.env`.

### 3. LinkedIn
1. Create an app at https://www.linkedin.com/developers/apps.
2. Request access to the **"Share on LinkedIn"** product (self-serve for
   posting as yourself; company page posting needs additional review).
3. Complete the OAuth 2.0 flow to get an access token with `w_member_social`
   scope (LinkedIn's docs walk through the redirect/callback flow — there's
   no way around doing this once manually to mint the token).
4. Find your author URN: call `GET https://api.linkedin.com/v2/userinfo`
   with your token; the `sub` field is your member ID → URN is
   `urn:li:person:{sub}`.
5. Put `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_AUTHOR_URN` in `.env`.
   Note: LinkedIn access tokens expire (~60 days) — you'll need to refresh
   periodically unless you implement the refresh-token flow.

### 4. Image hosting (for Instagram)
1. Register a free app at https://api.imgur.com/oauth2/addclient — select
   "Anonymous usage without user authorization," you only need a Client ID.
2. Put `IMGUR_CLIENT_ID` in `.env`.

### 5. Content generation
Put your `ANTHROPIC_API_KEY` in `.env` (from https://console.anthropic.com).

## Running it

1. `pip install -r requirements.txt`
2. `cp .env.example .env` and fill in everything above.
3. Leave `LIVE_POSTING_ENABLED=false` for now and do a dry run:
   ```
   python run_cycle.py
   ```
   This prints exactly what it *would* post to each platform, with no
   actual API calls to the social platforms. Review the output — check
   tone, accuracy, and that nothing looks off — across several runs.
4. Once you're comfortable: set `LIVE_POSTING_ENABLED=true` in `.env`
   **and** `CONFIRM_LIVE_POSTING = True` in `config.py` (two separate
   switches on purpose — same pattern as the trading bot).
5. Schedule it to run a few times a day with cron:
   ```
   crontab -e
   ```
   Add (adjust path; this example runs at 9am, 1pm, 5pm, 8pm):
   ```
   0 9,13,17,20 * * * cd /path/to/social_ai_agent && /usr/bin/python3 run_cycle.py >> cron.log 2>&1
   ```

## Files

- `run_cycle.py` — one full cycle: fetch → generate → post → log (cron entry point)
- `news_fetcher.py` — pulls candidate articles from `config.RSS_FEEDS`
- `content_generator.py` — Claude turns each article into platform-specific copy
- `image_generator.py` — renders + hosts a headline image for Instagram
- `posted_log.py` — prevents re-posting the same article
- `platforms/` — one file per platform's posting API
- `config.py` — feeds, limits, posting frequency knobs, safety switches
- `agent.log` / `posted_log.json` — created automatically once you run it

## Tuning content

- `config.RSS_FEEDS` — swap in whatever sources you trust
- `config.CONTENT_MIX` — ratio of "summary" vs "commentary" style posts
- `config.POSTS_PER_CYCLE` — how many articles get posted per cron run
- `content_generator.PLATFORM_STYLE` — tone/format instructions per platform
