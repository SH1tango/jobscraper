# report_from_db.py
import os, sqlite3, requests
DB = "jobs.db"
WEBHOOK = os.getenv("HA_WEBHOOK_URL") or "http://192.168.0.20:8123/api/webhook/-Su6Jkokz0muUT1CmwN9E5LB3"
con = sqlite3.connect(DB)
rows = con.execute("""
  SELECT title, url, posted_at
  FROM jobs
  WHERE posted_at LIKE '2025-%'
  ORDER BY posted_at DESC
""").fetchall()
if not rows:
    body = "No matching jobs."
else:
    lines = [f"- [{t}]({u})" + (f" (posted {p})" if p else "") for (t,u,p) in rows]
    body = "Jobs found (" + str(len(rows)) + "):\n\n" + "\n".join(lines)
    body = body[:3500] if len(body) > 3500 else body
requests.post(WEBHOOK, json={"title": "Job watcher", "message": body}, timeout=15).raise_for_status()
print(f"Sent {len(rows)} rows")
