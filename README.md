# 🔑 VaultKey Auto-Poster

Your Telegram bot posts to **@vaultkey_bets** by itself, 24/7, on a schedule.
Runs free on GitHub Actions — **no PC needed, nothing to keep running.**

You edit one text file (`posts.json`). The bot does the rest.

---

## ⚡ ONE-TIME SETUP (~5 minutes)

### 1. Make a fresh bot token
Your old token leaked in chat — replace it:
- Open **@BotFather** → `/revoke` → pick your bot → copy the **new token**.
- Make sure the bot is an **admin** of @vaultkey_bets with **"Post messages"** on.

### 2. Create a GitHub repo
- Go to github.com → **New repository** → name it `vaultkey-poster` → **Private** → Create.
- Upload **all files from this folder** (drag & drop into the repo → Commit).
  (Keep the folder structure — the `.github/workflows/` folder matters.)

### 3. Add the token as a secret
- In the repo: **Settings → Secrets and variables → Actions → New repository secret**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: paste your **new** bot token → Save.

### 4. Turn Actions on
- Open the **Actions** tab → if prompted, click **"I understand… enable workflows"**.
- You'll see **"VaultKey auto-poster"**. Click it → **Run workflow** to test it once.

That's it. From now on it checks every 15 minutes and posts anything that's due.

---

## 🗓️ HOW SCHEDULING WORKS

`config.json`:
```json
{
  "chat_id": "@vaultkey_bets",
  "timezone": "Europe/London",
  "start_date": "2026-09-08"
}
```
- **start_date** = the Monday your Week 1 begins. Change it to shift the whole week.
- **timezone** = the local time your posts fire. Default `Europe/London` (UK betting audience). Change to `Europe/Warsaw`, `Europe/Berlin`, etc. if you prefer.
- Posts in `posts.json` use `day` (1–7) + `time` (24h). Day 1 = start_date.

---

## ✍️ FILLING IN TIPS & RESULTS

Any post whose text still contains `[brackets]` is a **template** — the bot **skips it** so it never posts a placeholder. Before that day, open `posts.json` and replace the brackets with the real match / odds / result, then commit.

Example — change:
```
⚽ [Home] v [Away]
Pick: [selection]
Odds: [x.xx]
```
to:
```
⚽ Arsenal v Chelsea
Pick: Over 2.5 goals
Odds: 1.90
```
Save → commit. Done. (16 evergreen posts already auto-fire with no editing.)

**Results posts** (`...-result`, `...-recap`): fill them with what actually happened — won or lost, straight. That honesty is the channel's whole edge and keeps it ban-safe.

---

## ➕ ADDING / CHANGING POSTS

Each post is one block in `posts.json`:
```json
{
  "id": "d3-1400-tip",
  "day": 3, "time": "14:00",
  "text": "your text here\nuse \\n for new lines"
}
```
- **id** must be unique (any text). Once a post is sent, its id is remembered in `posted.json` and won't repeat.
- To post an **image** (e.g. a real winning slip), add `"image": "https://.../slip.jpg"` — a public image URL, or commit the image to the `images/` folder and use its raw GitHub URL.

---

## 🔁 WEEK 2 AND BEYOND

Two options:
1. **Reuse this file:** bump `start_date` to next Monday and refresh the texts — same schedule runs again.
2. **Send me your real results each week** → I'll write the next week's `posts.json` (with real win posts) and you just replace the file.

---

## 🧯 TROUBLESHOOTING

- **Nothing posts:** check the **Actions** tab → open the latest run → read the log. Most common: token secret name isn't exactly `TELEGRAM_BOT_TOKEN`, or the bot isn't an admin of the channel.
- **`chat not found`:** the bot isn't in the channel, or the @username is wrong.
- **A post fired late:** GitHub cron can drift a few minutes — normal. The bot never double-posts (it tracks `posted.json`).
- **Want to stop it:** Actions tab → "…" → **Disable workflow**.

---

## ⚠️ NOTES
- The bot posts to a **channel**. Selling/DMs still go through your personal **@thevaultholder** — a bot can only message people who message it first.
- Reaction mechanics ("250 reactions = 1 key") and real-time triggers aren't in this simple poster — we add those once you have an audience.
- 18+ · Bet responsibly. Picks are analysis, not guaranteed outcomes.
