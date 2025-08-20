import os, sys, time, sqlite3, re, unicodedata
from urllib.parse import urljoin
from datetime import datetime, timedelta
import requests, yaml
from bs4 import BeautifulSoup

BASE_DIR = os.environ.get("JOBWATCHER_DIR", "/config/jobwatcher")
DB_PATH = os.path.join(BASE_DIR, "jobs.db")

CONTROL_CHARS_RE = re.compile(r"[\u0000-\u001F\u007F\u200B\u200E\u200F\u202A-\u202E]")

import json

OPTIONS_PATH = "/data/options.json"

def load_options():
    try:
        with open(OPTIONS_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def clean_text(s):
    if not s: return s
    import unicodedata
    s = unicodedata.normalize("NFKC", s)
    s = CONTROL_CHARS_RE.sub("", s)
    return " ".join(s.split())

def connect_db():
    os.makedirs(BASE_DIR, exist_ok=True)
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

def _parse_iso(s):  # ISO8601 with Z handling
    return datetime.fromisoformat(s.strip().replace("Z","+00:00"))

def parse_page(url, item_sel, title_sel, link_sel, date_sel, date_attr, year_filter=None, must_all=None):
    html, final_url = fetch(url)
    soup = BeautifulSoup(html, "lxml")
    items = soup.select(item_sel)
    rows = []
    for it in items:
        tnode = it.select_one(title_sel)
        lnode = it.select_one(link_sel)
        if not tnode or not lnode:
            continue
        title = clean_text(tnode.get_text(strip=True)) or ""
        link = normalise_link(final_url, lnode.get("href"))
        if not link:
            continue
        posted_at = None
        if date_sel:
            dnode = it.select_one(date_sel)
            if dnode:
                posted_at = dnode.get(date_attr or "") or dnode.get_text(strip=True)
                posted_at = clean_text(posted_at)
        if year_filter:
            if not posted_at:
                continue
            try:
                if _parse_iso(posted_at).year != int(year_filter):
                    continue
            except Exception:
                continue
        if must_all:
            ttl = title.lower()
            if not all(k in ttl for k in must_all):
                continue
        rows.append({"site":"Helijobs Oceania pilots","title":title,"url":link,"posted_at":posted_at})
    return rows

def scrape(pages, year_filter):
    opts = load_options()
    # always record only Australia titles in DB
    must_all = ["australia"]
    item_sel = "article"
    title_sel = "h2.entry-title a"
    link_sel = "h2.entry-title a"
    date_sel = "time.entry-date"
    date_attr = "datetime"


    source_url = opts.get("source_url", "https://helijobs.net/category/pilot/?tag=oceania")
    page_pattern = opts.get("page_pattern", "https://helijobs.net/category/pilot/page/{page}/?tag=oceania")
    year_filter = opts.get("year_filter", 2025)
    pages = int(opts.get("pages_daily", 1))
    
    urls = [source_url] + [page_pattern.format(page=i) for i in range(2, pages+1)]
    all_rows = []
    for u in urls:
        try:
            all_rows.extend(parse_page(u, item_sel, title_sel, link_sel, date_sel, date_attr, year_filter, must_all))
        except Exception as e:
            print(f"[warn] page failed {u}: {e}")

    con = connect_db()
    cur = con.cursor()
    new_rows = []
    for j in all_rows:
        try:
            cur.execute("insert into jobs(site,title,url,posted_at,first_seen_utc) values(?,?,?,?,?)",
                        (j["site"], j["title"], j["url"], j["posted_at"], int(time.time())))
            new_rows.append(j)
        except sqlite3.IntegrityError:
            pass
    con.commit()
    con.close()
    return new_rows, all_rows
