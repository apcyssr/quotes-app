# crawler.py
import requests
from bs4 import BeautifulSoup
import sqlite3

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

url = "http://quotes.toscrape.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

quotes = soup.find_all("div", class_="quote")

count = 0
for q in quotes:
    text = q.find("span", class_="text").get_text()
    author = q.find("small", class_="author").get_text()
    tags = [tag.get_text() for tag in q.find_all("a", class_="tag")]

    for tag in tags:
        cursor.execute(
            "INSERT INTO quotes (text, author, category) VALUES (?, ?, ?)",
            (text, author, tag)
        )

    count += 1
    if count >= 20:
        break

conn.commit()
conn.close()