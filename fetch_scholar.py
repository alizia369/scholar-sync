import os, json, requests
from datetime import datetime, timezone
from scholarly import scholarly, ProxyGenerator

SCHOLAR_ID = os.environ["SCHOLAR_ID"]
GIST_ID    = os.environ["GIST_ID"]
TOKEN      = os.environ["GITHUB_TOKEN"]

# Use free proxies to avoid CAPTCHA
pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)

# Set a timeout so it doesn't hang forever
author = scholarly.search_author_id(SCHOLAR_ID)
scholarly.fill(author, sections=["indices", "counts"])

since_2019 = sum(
    v for y, v in author.get("cites_per_year", {}).items()
    if int(y) >= 2019
)

stats = {
    "citations":  author.get("citedby", 0),
    "h_index":    author.get("hindex", 0),
    "i10_index":  author.get("i10index", 0),
    "since_2019": since_2019,
    "updated":    datetime.now(timezone.utc).strftime("%Y-%m-%d")
}

requests.patch(
    f"https://api.github.com/gists/{GIST_ID}",
    headers={"Authorization": f"token {TOKEN}"},
    json={"files": {"scholar_stats.json": {"content": json.dumps(stats, indent=2)}}}
)
print("Done:", stats)
