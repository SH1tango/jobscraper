import os, sqlite3
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from scraper import scrape, DB_PATH

app = FastAPI(title="JobWatcher")

@app.get("/", response_class=PlainTextResponse)
def root():
    return "JobWatcher API. GET /jobs, POST /scrape"

@app.get("/jobs")
def get_jobs(
    year: int | None = None,
    limit: int = 100,
    title_any: str | None = Query(None, description="pipe sep terms, match any"),
    title_all: str | None = Query(None, description="pipe sep terms, match all"),
):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        sql = "SELECT site,title,url,posted_at FROM jobs"
        where = []
        params = []
        if year:
            where.append("posted_at LIKE ?")
            params.append(f"{year}-%")
        if title_any:
            terms = [t.strip().lower() for t in title_any.split("|") if t.strip()]
            if terms:
                ors = []
                for t in terms:
                    ors.append("lower(title) LIKE ?")
                    params.append(f"%{t}%")
                where.append("(" + " OR ".join(ors) + ")")
        if title_all:
            terms = [t.strip().lower() for t in title_all.split("|") if t.strip()]
            for t in terms:
                where.append("lower(title) LIKE ?")
                params.append(f"%{t}%")
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY posted_at DESC LIMIT ?"
        params.append(limit)
        rows = cur.execute(sql, params).fetchall()
    finally:
        con.close()
    items = [{"site":s,"title":t,"url":u,"posted_at":p} for (s,t,u,p) in rows]
    return JSONResponse({"count": len(items), "items": items})

@app.post("/scrape")
def trigger_scrape(backfill: bool = False, year: int = 2025):
    pages = int(os.environ.get("JW_PAGES_BACKFILL" if backfill else "JW_PAGES_DAILY", "1"))
    new_rows, all_rows = scrape(pages=pages, year_filter=year)
    return JSONResponse({"inserted": len(new_rows), "matched": len(all_rows), "pages": pages})
