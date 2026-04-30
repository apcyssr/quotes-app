# main.py
from fastapi import FastAPI
import sqlite3

app = FastAPI()

def get_db():
    return sqlite3.connect("quotes.db")

@app.get("/")
def home():
    return {"message": "Quotes API"}

# READ
@app.get("/quotes")
def get_quotes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes")
    data = cursor.fetchall()
    conn.close()
    return data

# CREATE
@app.post("/quotes")
def create_quote(text: str, author: str, category: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO quotes (text, author, category) VALUES (?, ?, ?)",
        (text, author, category)
    )
    conn.commit()
    conn.close()
    return {"status": "created"}

# UPDATE
@app.put("/quotes/{id}")
def update_quote(id: int, text: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE quotes SET text=? WHERE id=?",
        (text, id)
    )
    conn.commit()
    conn.close()
    return {"status": "updated"}

# DELETE
@app.delete("/quotes/{id}")
def delete_quote(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quotes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

from gradio_app import demo
import gradio as gr

app = gr.mount_gradio_app(app, demo, path="/gradio")