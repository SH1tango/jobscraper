# api.py
import sqlite3
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, PlainTextResponse

DB_PATH = "/data/jobs.db"

app = FastAPI(title="JobWatcher API")

@app.get("/", response_class=PlainTextResponse)
def root():
    return "JobWatcher API. Try /jobs or /jobs?year=2025&title_any=copilot|co pilot"

def _like_frag(x: str) -> str:
    # case-insensitive LIKE by using lower() in SQL and lower() terms in params
    return f"%{x.lower()}%"

@app.get("/jobs")
def get_jobs(
    year: int | None = None,
    limit: int = 100,
    title_any: str | None = Query(None, description="pipe-separated substrings; match if ANY found"),
    title_all: str | None = Query(None, description="pipe-separated substrings; match only if ALL found"),
):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        where = []
        params = []

        # base query: rows you have in DB (already Australia-only because of scraper)
        base = "SELECT site, title, url, posted_at FROM jobs"

        # year filter (uses posted_at ISO)
        if year:
            where.append("posted_at LIKE ?")
            params.append(f"{year}-%")

        # text filters (case-insensitive)
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
    finally:
        con.close()

    items = [{"site": s, "title": t, "url": u, "posted_at": p} for (s, t, u, p) in rows]
    return JSONResponse({"count": len(items), "items": items})
