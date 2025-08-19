# scraper.py
import os, sys, time, smtplib, socket, sqlite3, re, unicodedata
from email.mime.text import MIMEText
from urllib.parse import urljoin
from datetime import datetime, timedelta

import requests, yaml
from bs4 import BeautifulSoup

DB_PATH = "jobs.db"
CFG_PATH = "config.yaml"

# ------------- utils -------------
CONTROL_CHARS_RE = re.compile(r"[\u0000-\u001F\u007F\u200B\u200E\u200F\u202A-\u202E]")

def clean_text(s: str | None) -> str | None:
    if not s:
        return s
    s = unicodedata.normalize("NFKC", s)
    s = CONTROL_CHARS_RE.sub("", s)
    s = " ".join(s.split())
    return s

def _parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.strip().replace("Z", "+00:00"))

def load_cfg(path=CFG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def validate_cfg(cfg):
    assert isinstance(cfg, dict), "config is not a mapping"
    assert isinstance(cfg.get("sites"), list) and cfg["sites"], "config.sites must be a non empty list"
    for i, s in enumerate(cfg["sites"]):
        for k in ("name","url","item_selector","title_selector","link_selector"):
            assert s.get(k), f"config.sites[{i}] missing '{k}'"

def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        create table if not exists jobs(
            id integer primary key,
            site text,
            title text,
            url text unique,
            posted_at text,
            first_seen_utc integer
        )
    """)
    return con

def fetch(url, timeout=20):
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (compatible; JobWatcher/1.0)"}, timeout=timeout)
    r.raise_for_status()
    return r.text, r.url

def normalise_link(base, href):
    return urljoin(base, href.strip()) if href else None

# ------------- scraping -------------
def page_urls(site: dict, pages: int):
    """Yield the first `pages` URLs for this site."""
    yield site["url"]
    pat = site.get("page_pattern")
    if not pat:
        return
    for p in range(2, pages+1):
        yield pat.format(page=p)

def parse_page(site: dict, url: str):
    html, final_url = fetch(url)
    soup = BeautifulSoup(html, "lxml")
    items = soup.select(site["item_selector"])
    results = []

    for it in items:
        tnode = it.select_one(site["title_selector"])
        lnode = it.select_one(site["link_selector"])
        if not tnode or not lnode:
            continue
        title = clean_text(tnode.get_text(strip=True)) or ""
        link = normalise_link(final_url, lnode.get("href"))
        if not link:
            continue

        posted_at = None
        if site.get("date_selector"):
            dnode = it.select_one(site["date_selector"])
            if dnode:
                posted_at = dnode.get(site.get("date_attr") or "") or dnode.get_text(strip=True)
                posted_at = clean_text(posted_at)

        # enforce year filter if set
        yf = site.get("year_filter")
        if yf:
            if not posted_at:
                continue
            try:
                if _parse_iso(posted_at).year != int(yf):
                    continue
            except Exception:
                continue

        # title must contain ALL required keywords (case-insensitive)
        must_all = [k.lower() for k in (site.get("title_keywords_all") or [])]
        ttl = title.lower()
        if must_all and not all(k in ttl for k in must_all):
            continue

        results.append({"site": site["name"], "title": title, "url": link, "posted_at": posted_at})
    return results

def scrape_site(site: dict, max_pages: int):
    all_rows = []
    for u in page_urls(site, max_pages):
        try:
            rows = parse_page(site, u)
            # stop early if a later page looks empty, but keep conservative:
            if not rows:
                # do not break on first empty, listings can have sparse pages
                pass
            all_rows.extend(rows)
        except Exception as e:
            print(f"[warn] {site['name']} page fetch failed {u}: {e}")
    return all_rows

# ------------- storage -------------
def store_new(con, jobs):
    cur = con.cursor()
    new_rows = []
    for j in jobs:
        try:
            cur.execute("insert into jobs(site,title,url,posted_at,first_seen_utc) values(?,?,?,?,?)",
                        (j["site"], j["title"], j["url"], j["posted_at"], int(time.time())))
            new_rows.append(j)
        except sqlite3.IntegrityError:
            pass
    con.commit()
    return new_rows

# ------------- reporting -------------
def _trim(s: str, max_len: int = 3500) -> str:
    return s if len(s) <= max_len else s[:max_len-12] + "\n\n…[truncated]"

def format_report(rows):
    if not rows:
        return "No matching jobs."
    lines = []
    for j in rows:
        when = f" ({j['posted_at'][:10]})" if j.get("posted_at") else ""
        lines.append(f"- [{j['title']}]({j['url']}){when}")
    return _trim(f"Jobs found ({len(rows)}):\n\n" + "\n".join(lines), 3500)

def send_webhook(cfg, body):
    url = os.getenv("HA_WEBHOOK_URL") or cfg["url"]
    try:
        r = requests.post(url, json={"title":"Job watcher","message": body}, timeout=15)
        r.raise_for_status()
        print(f"[webhook] sent len={len(body)}")
    except Exception as e:
        print(f"[webhook] failed: {e}\n{body}")

# ------------- main -------------
def main():
    cfg = load_cfg()
    validate_cfg(cfg)
    con = connect_db()

    backfill = "--backfill" in sys.argv       # crawl first N pages
    report_all = "--report-all" in sys.argv   # show all matches, not just new
    dry = "--dry-run" in sys.argv             # do not write DB

    all_for_report = []

    for site in cfg["sites"]:
        pages = site.get("backfill_pages", 5) if backfill else site.get("daily_pages", 1)
        rows = scrape_site(site, pages)
        print(f"[debug] {site['name']}: scraped {len(rows)} rows from {pages} page(s)")

        if dry:
            all_for_report.extend(rows if report_all else rows)
            continue

        new_rows = store_new(con, rows)
        all_for_report.extend(rows if report_all else new_rows)

    body = format_report(all_for_report)
    method = cfg["report"]["method"]
    if method == "webhook":
        send_webhook(cfg["report"]["webhook"], body)
    else:
        print(body)

if __name__ == "__main__":
    main()
