import gradio as gr
import sqlite3
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def load_data():
    conn = sqlite3.connect("quotes.db")
    df = pd.read_sql_query("SELECT * FROM quotes", conn)
    conn.close()
    return df

def search_quotes(keyword):
    df = load_data()
    result = df[df["text"].str.contains(keyword, case=False)]
    return result

def filter_author(author):
    df = load_data()
    result = df[df["author"] == author]
    return result

def wordcloud_plot():
    df = load_data()
    text = " ".join(df["text"].tolist())

    wc = WordCloud(width=800, height=400, background_color="white").generate(text)

    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    return plt

def get_authors():
    df = load_data()
    return list(df["author"].unique())

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🌟 Quotes Portfolio Dashboard")
    gr.Markdown("ค้นหา วิเคราะห์ และดูข้อมูลคำคมแบบมือโปร")

    with gr.Tab("📄 All Quotes"):
        table = gr.Dataframe()
        btn_load = gr.Button("โหลดข้อมูล")
        btn_load.click(load_data, outputs=table)

    with gr.Tab("🔍 Search"):
        keyword = gr.Textbox(label="ค้นหาคำ")
        search_btn = gr.Button("Search")
        search_output = gr.Dataframe()
        search_btn.click(search_quotes, inputs=keyword, outputs=search_output)

    with gr.Tab("👤 Filter by Author"):
        author_dropdown = gr.Dropdown(choices=get_authors(), label="เลือกผู้เขียน")
        filter_btn = gr.Button("Filter")
        filter_output = gr.Dataframe()
        filter_btn.click(filter_author, inputs=author_dropdown, outputs=filter_output)

    with gr.Tab("☁️ WordCloud"):
        wc_btn = gr.Button("Generate WordCloud")
        wc_plot = gr.Plot()
        wc_btn.click(wordcloud_plot, outputs=wc_plot)