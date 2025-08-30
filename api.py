# api.py
from __future__ import annotations
import os
import shutil
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, PlainTextResponse

DATA_DIR = Path("/data")
DB_PATH = DATA_DIR / "jobs.db"
SEED_DB = Path("/app/jobs.db")  # optional seed baked into the image

app = FastAPI(title="JobWatcher API")

def ensure_db() -> None:
    # Make /data even if the Supervisor mount is missing
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Seed once if no DB but a seed exists
    if not DB_PATH.exists() and SEED_DB.exists():
        try:
            shutil.copyfile(SEED_DB, DB_PATH)
            print(f">>> Seeded DB from {SEED_DB} -> {DB_PATH}")
        except Exception as e:
            print(f">>> Warning: could not seed DB: {e}")

    # Create schema if table absent
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                site TEXT,
                title TEXT,
                url TEXT,
                posted_at TEXT
            )
            """
        )
        con.commit()

@app.on_event("startup")
def _startup() -> None:
    try:
        ensure_db()
        size = DB_PATH.stat().st_size if DB_PATH.exists() else -1
        is_mount = any(line.split()[1] == "/data" for line in open("/proc/mounts"))
        print(f">>> Using DB {DB_PATH} size={size}B mount={is_mount}")
    except Exception as e:
        # Do not crash app on startup
        print(f">>> Startup DB init warning: {e}")

@app.get("/", response_class=PlainTextResponse)
def root():
    return "JobWatcher API. Try /jobs or /jobs?year=2025&title_any=copilot|co pilot"

@app.get("/debug/dbinfo")
def dbinfo():
    return {
        "db_path": str(DB_PATH),
        "exists": DB_PATH.exists(),
        "size": DB_PATH.stat().st_size if DB_PATH.exists() else 0,
        "data_is_mount": any(line.split()[1] == "/data" for line in open("/proc/mounts")),
    }

def _like_frag(x: str) -> str:
    return f"%{x.lower()}%"

@app.get("/jobs")
def get_jobs(
    year: int | None = None,
    limit: int = 100,
    title_any: str | None = Query(None, description="pipe separated substrings; match if ANY found"),
    title_all: str | None = Query(None, description="pipe separated substrings; match only if ALL found"),
):
    # Ensure DB in case startup path failed
    try:
        ensure_db()
    except Exception as e:
        # Continue and return empty result if DB still not usable
        print(f">>> ensure_db at request warning: {e}")
        return JSONResponse({"count": 0, "items": []})

    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        where, params = [], []

        base = "SELECT site, title, url, posted_at FROM jobs"

        if year:
            where.append("posted_at LIKE ?")
            params.append(f"{year}-%")

        if title_any:
            any_terms = [t.strip().lower() for t in title_any.split("|") if t.strip()]
            if any_terms:
                ors = []
                for t in any_terms:
                    ors.append("lower(title) LIKE ?")
                    params.append(_like_frag(t))
                where.append("(" + " OR ".join(ors) + ")")

        if title_all:
            all_terms = [t.strip().lower() for t in title_all.split("|") if t.strip()]
            for t in all_terms:
                where.append("lower(title) LIKE ?")
                params.append(_like_frag(t))

        sql = base
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY posted_at DESC LIMIT ?"
        params.append(limit)

        rows = cur.execute(sql, params).fetchall()
    except sqlite3.OperationalError as e:
        # Table missing or DB not openable — return empty set rather than 500
        print(f">>> SQLite error: {e}")
        rows = []
    finally:
        try:
            con.close()
        except Exception:
            pass

    items = [{"site": s, "title": t, "url": u, "posted_at": p} for (s, t, u, p) in rows]
    return JSONResponse({"count": len(items), "items": items})
