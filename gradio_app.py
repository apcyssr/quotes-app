import gradio as gr
import sqlite3
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -----------------------
# DATABASE FUNCTIONS
# -----------------------
def load_data():
    conn = sqlite3.connect("quotes.db")
    df = pd.read_sql_query("SELECT * FROM quotes", conn)
    conn.close()
    return df

def search_quotes(keyword):
    df = load_data()
    return df[df["text"].str.contains(keyword, case=False, na=False)]

def filter_author(author):
    df = load_data()
    return df[df["author"] == author]

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
    return list(df["author"].dropna().unique())


# -----------------------
# LANGUAGE DICTIONARY
# -----------------------
LANG = {
    "en": {
        "title": "🌟 Quotes Portfolio Dashboard",
        "desc": "Explore, search, and analyze quotes",
        "load": "Load Data",
        "search": "Search",
        "filter": "Filter",
        "wordcloud": "Generate WordCloud",
        "keyword": "Keyword",
        "author": "Select Author",
        "tab_all": "📄 All Quotes",
        "tab_search": "🔍 Search",
        "tab_filter": "👤 Filter by Author",
        "tab_wc": "☁️ WordCloud"
    },
    "th": {
        "title": "🌟 แดชบอร์ดคำคม",
        "desc": "ค้นหา วิเคราะห์ และดูข้อมูลคำคม",
        "load": "โหลดข้อมูล",
        "search": "ค้นหา",
        "filter": "กรอง",
        "wordcloud": "สร้าง WordCloud",
        "keyword": "คำค้นหา",
        "author": "เลือกผู้เขียน",
        "tab_all": "📄 คำคมทั้งหมด",
        "tab_search": "🔍 ค้นหา",
        "tab_filter": "👤 ผู้เขียน",
        "tab_wc": "☁️ เวิร์ดคลาวด์"
    },
    "kr": {
        "title": "🌟 명언 대시보드",
        "desc": "명언을 검색하고 분석하세요",
        "load": "데이터 불러오기",
        "search": "검색",
        "filter": "필터",
        "wordcloud": "워드클라우드 생성",
        "keyword": "검색어",
        "author": "작성자 선택",
        "tab_all": "📄 전체",
        "tab_search": "🔍 검색",
        "tab_filter": "👤 작성자",
        "tab_wc": "☁️ 워드클라우드"
    }
}


# -----------------------
# BUILD UI
# -----------------------
def build_ui(lang_code):
    t = LANG[lang_code]

    with gr.Blocks() as ui:
        gr.Markdown(f"# {t['title']}")
        gr.Markdown(t["desc"])

        with gr.Tab(t["tab_all"]):
            table = gr.Dataframe()
            btn_load = gr.Button(t["load"])
            btn_load.click(load_data, outputs=table)

        with gr.Tab(t["tab_search"]):
            keyword = gr.Textbox(label=t["keyword"])
            search_btn = gr.Button(t["search"])
            search_output = gr.Dataframe()
            search_btn.click(search_quotes, inputs=keyword, outputs=search_output)

        with gr.Tab(t["tab_filter"]):
            author_dropdown = gr.Dropdown(choices=get_authors(), label=t["author"])
            filter_btn = gr.Button(t["filter"])
            filter_output = gr.Dataframe()
            filter_btn.click(filter_author, inputs=author_dropdown, outputs=filter_output)

        with gr.Tab(t["tab_wc"]):
            wc_btn = gr.Button(t["wordcloud"])
            wc_plot = gr.Plot()
            wc_btn.click(wordcloud_plot, outputs=wc_plot)

    return ui


# -----------------------
# MAIN APP (LANG + THEME)
# -----------------------
def create_app():
    with gr.Blocks() as app:

        lang = gr.State("en")

        t = LANG["en"]

        title = gr.Markdown(f"# {t['title']}")
        desc = gr.Markdown(t["desc"])

        with gr.Row():
            lang_dropdown = gr.Dropdown(
                choices=[("English","en"),("ไทย","th"),("한국어","kr")],
                value="en",
                label="🌐 Language"
            )

        # UI Components
        with gr.Tab(t["tab_all"]):
            table = gr.Dataframe()
            btn_load = gr.Button(t["load"])
            btn_load.click(load_data, outputs=table)

        with gr.Tab(t["tab_search"]):
            keyword = gr.Textbox(label=t["keyword"])
            search_btn = gr.Button(t["search"])
            search_output = gr.Dataframe()
            search_btn.click(search_quotes, inputs=keyword, outputs=search_output)

        with gr.Tab(t["tab_filter"]):
            author_dropdown = gr.Dropdown(choices=get_authors(), label=t["author"])
            filter_btn = gr.Button(t["filter"])
            filter_output = gr.Dataframe()
            filter_btn.click(filter_author, inputs=author_dropdown, outputs=filter_output)

        with gr.Tab(t["tab_wc"]):
            wc_btn = gr.Button(t["wordcloud"])
            wc_plot = gr.Plot()
            wc_btn.click(wordcloud_plot, outputs=wc_plot)

        # 🔥 เปลี่ยนภาษา (update text แทน)
        def update_lang(lang_code):
            t = LANG[lang_code]
            return (
                f"# {t['title']}",
                t["desc"],
                t["load"],
                t["search"],
                t["filter"],
                t["wordcloud"]
            )

        lang_dropdown.change(
            update_lang,
            inputs=lang_dropdown,
            outputs=[title, desc, btn_load, search_btn, filter_btn, wc_btn]
        )

    return app



demo = create_app()