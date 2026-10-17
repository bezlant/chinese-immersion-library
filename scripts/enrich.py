#!/usr/bin/env python3
"""Fill machine-resolvable fields in data/*.json from the network.

  youtube  -> ids.youtube_channel_id, image, feed (YouTube channel RSS)
  podcast  -> image, feed (the show's real RSS URL from the iTunes lookup API)
  bilibili -> image, feed (RSSHub route; self-host RSSHub for production use)
  website  -> feed (RSS/Atom advertised in the page head, verified to parse)

Only fills missing fields unless --force is given. Entries that cannot be
resolved are listed at the end so they can be fixed or removed by hand.

Usage:
    python3 scripts/enrich.py [--force] [--only youtube|podcast|bilibili|website]

Uses curl (preinstalled on macOS and GitHub runners) so it works without
Python certificate setup.
"""
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
RSSHUB = "https://rsshub.app"


def curl(url, *extra):
    r = subprocess.run(["curl", "-sL", "-m", "25", "-A", UA, "-H", "Accept-Language: en", *extra, url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def youtube(e):
    html = curl(e["url"])
    m = re.search(r'"externalId":"(UC[\w-]{22})"', html) or re.search(r'<meta itemprop="identifier" content="(UC[\w-]{22})"', html)
    if not m:
        return False
    cid = m.group(1)
    e.setdefault("ids", {})["youtube_channel_id"] = cid
    img = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if img:
        e["image"] = img.group(1)
    e["feed"] = {"format": "youtube", "url": f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"}
    return True


def podcasts(entries):
    """iTunes lookup accepts many comma-separated ids per request."""
    by_id = {e["ids"]["apple_podcast_id"]: e for e in entries}
    ids, done = list(by_id), set()
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        for attempt in range(3):
            try:
                data = json.loads(curl("https://itunes.apple.com/lookup?entity=podcast&id=" + ",".join(chunk)))
                break
            except json.JSONDecodeError:
                time.sleep(10)
        else:
            continue
        for r in data.get("results", []):
            e = by_id.get(str(r.get("collectionId")))
            if not e or not r.get("feedUrl"):
                continue
            e["feed"] = {"format": "podcast", "url": r["feedUrl"]}
            art = r.get("artworkUrl600") or r.get("artworkUrl100")
            if art:
                e["image"] = art
            done.add(str(r["collectionId"]))
        time.sleep(3)
    return {pid for pid in ids if pid not in done}


def bilibili(e):
    mid = e["ids"]["bilibili_mid"]
    try:
        d = json.loads(curl(f"https://api.bilibili.com/x/web-interface/card?mid={mid}", "-H", "Referer: https://www.bilibili.com"))
        card = d["data"]["card"]
    except Exception:
        return False
    if card.get("face"):
        e["image"] = card["face"].replace("http://", "https://")
    e["feed"] = {"format": "rsshub", "url": f"{RSSHUB}/bilibili/user/video/{mid}"}
    return True


FEED_LINK = re.compile(r'<link[^>]+type=["\']application/(rss|atom)\+xml["\'][^>]*>', re.I)


def website(e):
    """Discover an RSS/Atom feed advertised in the page <head>, and keep it only if it parses as a feed."""
    html = curl(e["url"])
    for m in FEED_LINK.finditer(html):
        href = re.search(r'href=["\']([^"\']+)["\']', m.group(0))
        if not href:
            continue
        url = href.group(1).replace("&amp;", "&")
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = re.match(r"https?://[^/]+", e["url"]).group(0) + url
        elif not url.startswith("http"):
            continue
        # Comment feeds and wiki change logs are not content feeds.
        if any(s in url for s in ("comments", "Special:RecentChanges", "featuredfeed")):
            continue
        body = curl(url)[:2000]
        if "<rss" in body or "<feed" in body or "<rdf:RDF" in body:
            e["feed"] = {"format": m.group(1).lower(), "url": url}
            return True
    return False


def main():
    force = "--force" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    files = {p: json.loads(p.read_text(encoding="utf-8")) for p in sorted(DATA.glob("*.json"))}
    entries = [e for items in files.values() for e in items]

    def todo(kind):
        return [e for e in entries if e["type"] == kind and (force or "feed" not in e) and only in (None, kind)]

    failed = []
    yt = todo("youtube")
    with cf.ThreadPoolExecutor(6) as ex:
        for e, ok in zip(yt, ex.map(youtube, yt)):
            if not ok:
                failed.append(("youtube", e["id"], e["url"]))
    pods = todo("podcast")
    for pid in podcasts(pods) if pods else []:
        e = next(x for x in pods if x["ids"]["apple_podcast_id"] == pid)
        failed.append(("podcast", e["id"], e["url"]))
    bl = todo("bilibili")
    with cf.ThreadPoolExecutor(4) as ex:
        for e, ok in zip(bl, ex.map(bilibili, bl)):
            if not ok:
                failed.append(("bilibili", e["id"], e["url"]))

    # Websites without a discoverable feed are normal, so they are not reported.
    sites = todo("website") + todo("newsletter")
    with cf.ThreadPoolExecutor(8) as ex:
        found = sum(ex.map(website, sites))

    for p, items in files.items():
        p.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"youtube {len(yt)}, podcast {len(pods)}, bilibili {len(bl)}, websites {len(sites)} ({found} feeds found) processed; {len(failed)} unresolved")
    for f in failed:
        print("  UNRESOLVED", *f)


if __name__ == "__main__":
    main()
