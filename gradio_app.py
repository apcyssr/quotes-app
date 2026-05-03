import gradio as gr
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re

# -----------------------
# DATABASE
# -----------------------
def load_data():
    conn = sqlite3.connect("quotes.db")
    df = pd.read_sql_query("SELECT * FROM quotes", conn)
    conn.close()
    return df


# -----------------------
# KPI
# -----------------------
def get_kpis():
    df = load_data()
    total_quotes = len(df)
    total_authors = df["author"].nunique()
    total_categories = df["category"].nunique()

    return total_quotes, total_authors, total_categories


# -----------------------
# SEARCH / FILTER
# -----------------------
def search_quotes(keyword):
    df = load_data()
    return df[df["text"].str.contains(keyword, case=False, na=False)]

def filter_author(author):
    df = load_data()
    return df[df["author"] == author]

def get_authors():
    df = load_data()
    return sorted(df["author"].dropna().unique())


# -----------------------
# VISUALIZATION
# -----------------------
def plot_top_authors():
    df = load_data()
    counts = df["author"].value_counts().head(10)

    plt.figure()
    counts.plot(kind="bar")
    plt.title("Top 10 Authors")
    plt.xlabel("Author")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    return plt


def plot_category_dist():
    df = load_data()
    counts = df["category"].value_counts()

    plt.figure()
    counts.plot(kind="bar")
    plt.title("Category Distribution")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    return plt


def plot_word_freq():
    df = load_data()
    text = " ".join(df["text"].tolist())

    words = re.findall(r'\b\w+\b', text.lower())
    common = Counter(words).most_common(10)

    labels = [w[0] for w in common]
    values = [w[1] for w in common]

    plt.figure()
    plt.bar(labels, values)
    plt.title("Top 10 Words")
    plt.xticks(rotation=45)
    return plt


def wordcloud_plot():
    df = load_data()
    text = " ".join(df["text"].tolist())

    wc = WordCloud(width=800, height=400, background_color="white").generate(text)

    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    return plt


# -----------------------
# UI
# -----------------------
def create_app():
    with gr.Blocks() as app:

        gr.Markdown("# 📊 Quotes Analytics Dashboard")
        gr.Markdown("Explore, search, and analyze quotes in real-time")

        # -----------------------
        # KPI Section
        # -----------------------
        with gr.Row():
            total_q = gr.Number(label="📌 Total Quotes")
            total_a = gr.Number(label="🧑 Authors")
            total_c = gr.Number(label="🏷 Categories")

        btn_kpi = gr.Button("🔄 Refresh KPIs")
        btn_kpi.click(get_kpis, outputs=[total_q, total_a, total_c])

        gr.Markdown("---")

        # -----------------------
        # Data Table
        # -----------------------
        gr.Markdown("## 📄 Dataset")

        table = gr.Dataframe(value=load_data())
        btn_load = gr.Button("Load Data")
        btn_load.click(load_data, outputs=table)

        gr.Markdown("---")

        # -----------------------
        # Search & Filter
        # -----------------------
        gr.Markdown("## 🔍 Search & Filter")

        with gr.Row():
            keyword = gr.Textbox(label="Keyword")
            search_btn = gr.Button("Search")

        search_output = gr.Dataframe()
        search_btn.click(search_quotes, inputs=keyword, outputs=search_output)

        with gr.Row():
            author_dropdown = gr.Dropdown(choices=get_authors(), label="Author")
            filter_btn = gr.Button("Filter")

        filter_output = gr.Dataframe()
        filter_btn.click(filter_author, inputs=author_dropdown, outputs=filter_output)

        gr.Markdown("---")

        # -----------------------
        # Charts
        # -----------------------
        gr.Markdown("## 📈 Analytics")

        with gr.Row():
            btn_author = gr.Button("Top Authors")
            btn_category = gr.Button("Category Distribution")

        with gr.Row():
            plot1 = gr.Plot()
            plot2 = gr.Plot()

        btn_author.click(plot_top_authors, outputs=plot1)
        btn_category.click(plot_category_dist, outputs=plot2)

        with gr.Row():
            btn_word = gr.Button("Top Words")
            btn_wc = gr.Button("WordCloud")

        with gr.Row():
            plot3 = gr.Plot()
            plot4 = gr.Plot()

        btn_word.click(plot_word_freq, outputs=plot3)
        btn_wc.click(wordcloud_plot, outputs=plot4)

    return app


demo = create_app()