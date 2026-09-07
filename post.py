#!/usr/bin/env python3
"""
VaultKey auto-poster.
Runs on a schedule (GitHub Actions), posts any DUE messages to the Telegram channel,
and remembers what it already sent so nothing double-posts.

You normally only edit config.json and posts.json — not this file.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
POSTS_PATH = os.path.join(HERE, "posts.json")
POSTED_PATH = os.path.join(HERE, "posted.json")

API = "https://api.telegram.org/bot{token}/{method}"


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def scheduled_dt(cfg, post, tz):
    """Compute the absolute send time for a post from START_DATE + day + time."""
    start = datetime.strptime(cfg["start_date"], "%Y-%m-%d").date()
    d = start + timedelta(days=int(post["day"]) - 1)
    hh, mm = map(int, post["time"].split(":"))
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz)


def send_text(token, chat_id, text):
    r = requests.post(
        API.format(token=token, method="sendMessage"),
        data={
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        },
        timeout=30,
    )
    return r


def send_photo(token, chat_id, photo, caption):
    r = requests.post(
        API.format(token=token, method="sendPhoto"),
        data={"chat_id": chat_id, "photo": photo, "caption": caption},
        timeout=60,
    )
    return r


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN env var is missing.", file=sys.stderr)
        sys.exit(1)

    cfg = load_json(CONFIG_PATH, {})
    chat_id = cfg.get("chat_id")
    tz = ZoneInfo(cfg.get("timezone", "Europe/London"))
    if not chat_id or not cfg.get("start_date"):
        print("ERROR: config.json needs chat_id and start_date.", file=sys.stderr)
        sys.exit(1)

    posts = load_json(POSTS_PATH, [])
    posted = set(load_json(POSTED_PATH, []))

    now = datetime.now(tz)
    print(f"Now ({tz}): {now:%Y-%m-%d %H:%M} | {len(posts)} posts, {len(posted)} already sent")

    newly_posted = []
    for p in posts:
        pid = p["id"]
        if pid in posted:
            continue

        # skip un-filled template tips so the bot never posts a [placeholder]
        if "[" in p["text"] and "]" in p["text"]:
            when = scheduled_dt(cfg, p, tz)
            if when <= now:
                print(f"SKIP {pid}: still has [placeholders], not sending. Fill it in posts.json.")
            continue

        when = scheduled_dt(cfg, p, tz)
        if when > now:
            continue  # not due yet

        # too old? (more than 12h late) — skip to avoid dumping stale posts after downtime
        if now - when > timedelta(hours=12):
            print(f"SKIP {pid}: due {when:%m-%d %H:%M}, too old, marking as done.")
            newly_posted.append(pid)
            continue

        try:
            img = p.get("image")
            if img:
                r = send_photo(token, chat_id, img, p["text"])
            else:
                r = send_text(token, chat_id, p["text"])
            ok = r.json().get("ok", False)
            if ok:
                print(f"SENT {pid} (scheduled {when:%m-%d %H:%M})")
                newly_posted.append(pid)
            else:
                print(f"FAIL {pid}: {r.text}", file=sys.stderr)
        except Exception as e:
            print(f"ERROR {pid}: {e}", file=sys.stderr)

    if newly_posted:
        posted.update(newly_posted)
        save_json(POSTED_PATH, sorted(posted))
        print(f"Updated posted.json (+{len(newly_posted)})")
    else:
        print("Nothing due.")


if __name__ == "__main__":
    main()
