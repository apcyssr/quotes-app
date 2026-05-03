# crawler.py
import requests
from bs4 import BeautifulSoup
import sqlite3
import time

BASE_URL = "http://quotes.toscrape.com"

# 🔥 เลือก category ที่ต้องการ
TAGS = ["love", "inspirational", "life", "humor"]

# -----------------------
# DATABASE SETUP
# -----------------------
conn = sqlite3.connect("quotes.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    author TEXT,
    category TEXT
)
""")

# กัน insert ซ้ำ (optional แต่แนะนำ)
cursor.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_quote
ON quotes (text, author, category)
""")

# -----------------------
# CRAWLER FUNCTION
# -----------------------
def crawl_tag(tag):
    page = 1
    collected = 0

    print(f"\n🔍 Crawling category: {tag}")

    while collected < 20:
        url = f"{BASE_URL}/tag/{tag}/page/{page}/"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"❌ Page {page} not found for {tag}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.find_all("div", class_="quote")

        if not quotes:
            break

        for q in quotes:
            text = q.find("span", class_="text").get_text()
            author = q.find("small", class_="author").get_text()

            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO quotes (text, author, category) VALUES (?, ?, ?)",
                    (text, author, tag)
                )
                collected += 1
            except:
                continue

            if collected >= 20:
                break

        print(f"✔ Page {page} done (Total: {collected})")
        page += 1
        time.sleep(0.5)  # กันโดน block

# -----------------------
# RUN CRAWLER
# -----------------------
for tag in TAGS:
    crawl_tag(tag)

conn.commit()
conn.close()

print("\n✅ Crawling 완료 (category 당 20개 완료)")