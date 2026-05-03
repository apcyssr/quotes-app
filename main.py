from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

import gradio as gr
from gradio_app import demo

app = FastAPI(title="Quotes API", description="Manage and analyze quotes", version="1.0")

# -----------------------
# DATABASE
# -----------------------
def get_db():
    conn = sqlite3.connect("quotes.db")
    conn.row_factory = sqlite3.Row  # 🔥 ทำให้ dict ได้
    return conn


# -----------------------
# Pydantic Models
# -----------------------
class Quote(BaseModel):
    text: str
    author: str
    category: str


class QuoteResponse(Quote):
    id: int


# -----------------------
# ROOT
# -----------------------
@app.get("/")
def home():
    return {"message": "Quotes API is running 🚀"}


# -----------------------
# CREATE
# -----------------------
@app.post("/quotes", response_model=QuoteResponse)
def create_quote(quote: Quote):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO quotes (text, author, category) VALUES (?, ?, ?)",
        (quote.text, quote.author, quote.category)
    )
    conn.commit()

    new_id = cursor.lastrowid

    cursor.execute("SELECT * FROM quotes WHERE id=?", (new_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row)


# -----------------------
# READ (ALL + FILTER)
# -----------------------
@app.get("/quotes", response_model=List[QuoteResponse])
def get_quotes(
    author: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = Query(None, description="Search in text")
):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM quotes WHERE 1=1"
    params = []

    if author:
        query += " AND author = ?"
        params.append(author)

    if category:
        query += " AND category = ?"
        params.append(category)

    if keyword:
        query += " AND text LIKE ?"
        params.append(f"%{keyword}%")

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# -----------------------
# READ (DETAIL)
# -----------------------
@app.get("/quotes/{id}", response_model=QuoteResponse)
def get_quote(id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quotes WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Quote not found")

    return dict(row)


# -----------------------
# UPDATE
# -----------------------
@app.put("/quotes/{id}", response_model=QuoteResponse)
def update_quote(id: int, quote: Quote):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quotes WHERE id=?", (id,))
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Quote not found")

    cursor.execute(
        "UPDATE quotes SET text=?, author=?, category=? WHERE id=?",
        (quote.text, quote.author, quote.category, id)
    )
    conn.commit()

    cursor.execute("SELECT * FROM quotes WHERE id=?", (id,))
    updated = cursor.fetchone()

    conn.close()
    return dict(updated)


# -----------------------
# DELETE
# -----------------------
@app.delete("/quotes/{id}")
def delete_quote(id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quotes WHERE id=?", (id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Quote not found")

    cursor.execute("DELETE FROM quotes WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return {"message": f"Quote {id} deleted successfully"}


# -----------------------
# GRADIO MOUNT
# -----------------------
app = gr.mount_gradio_app(app, demo, path="/gradio")

# -----------------------
# Railway crash Protect
# -----------------------

import os

port = int(os.environ.get("PORT", 8000))

# -----------------------
# Database Reploy
# -----------------------

import os

if not os.path.exists("quotes.db"):
    import crawler