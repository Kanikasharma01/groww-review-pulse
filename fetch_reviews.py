"""Fetch recent public Google Play reviews of the Groww app (India) into a CSV.

Run in Google Colab (or locally):
    pip install google-play-scraper
    python fetch_reviews.py

Output columns: reviewId, content, score, at
"""
import csv
import datetime as dt

from google_play_scraper import Sort, reviews

APP_ID = "com.nextbillion.groww"  # check against the id in the app's Play Store URL
WEEKS = 12

cutoff = dt.datetime.now() - dt.timedelta(weeks=WEEKS)
rows, token = [], None
while True:
    batch, token = reviews(
        APP_ID, lang="en", country="in",
        sort=Sort.NEWEST, count=200, continuation_token=token,
    )
    rows += [b for b in batch if b["at"] >= cutoff]
    if not batch or batch[-1]["at"] < cutoff or token is None:
        break

with open("groww_reviews.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["reviewId", "content", "score", "at"])
    for r in rows:
        w.writerow([r["reviewId"], r["content"], r["score"], r["at"].date().isoformat()])

print(len(rows), "reviews saved to groww_reviews.csv")
