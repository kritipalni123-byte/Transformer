import streamlit as st
import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

st.title("🔌 Transformer Competitor Intelligence")

# -------------------------------
# CONFIG
# -------------------------------
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=power+transformer",
    "https://news.google.com/rss/search?q=transformer+industry"
]

COMPETITORS = [
    "ABB", "Siemens", "GE", "Hitachi", "CG", "Schneider",
    "Toshiba", "Bharat Bijlee", "Voltamp"
]

PRODUCT_KEYWORDS = {
    "Oil Filled Transformer": [
        "oil filled transformer",
        "oil immersed transformer",
        "transformer oil",
        "onan transformer",
        "onaf transformer"
    ],
    "Dry Type VPI Transformer": [
        "vpi transformer",
        "vacuum pressure impregnated"
    ],
    "Dry Type CRT Transformer": [
        "cast resin transformer",
        "crt transformer",
        "cast coil"
    ]
}

EXCLUDE_KEYWORDS = [
    "crude oil", "oil prices", "oil & gas",
    "petroleum", "diesel", "fuel"
]

# -------------------------------
# FUNCTIONS
# -------------------------------
def classify_product(text):
    text = str(text).lower()

    if any(word in text for word in EXCLUDE_KEYWORDS):
        return "Ignore"

    if "transformer" not in text:
        return "Ignore"

    for product, keywords in PRODUCT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return product

    return "Other Transformer"


def detect_competitor(text):
    text = str(text).lower()
    for comp in COMPETITORS:
        if comp.lower() in text:
            return comp
    return "Other"


def relevance_score(text):
    text = str(text).lower()
    score = 40

    if "transformer" in text:
        score += 20

    if any(x in text for x in ["mva", "kv", "capacity", "expansion"]):
        score += 20

    if any(x in text for x in ["order", "contract", "project", "deal"]):
        score += 20

    return min(score, 100)


def fetch_news():
    articles = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.title
            link = entry.link

            text = title

            try:
                res = requests.get(link, timeout=5)
                soup = BeautifulSoup(res.text, "html.parser")
                paragraphs = soup.find_all("p")
                content = " ".join([p.text for p in paragraphs])
                text = title + " " + content
            except:
                pass

            articles.append({
                "title": title,
                "link": link,
                "text": text
            })

    return pd.DataFrame(articles)

# -------------------------------
# MAIN
# -------------------------------
if st.button("Fetch News"):

    df = fetch_news()

    df["combined"] = df["title"] + " " + df["text"]

    df["Product"] = df["combined"].apply(classify_product)
    df["Competitor"] = df["combined"].apply(detect_competitor)
    df["Relevance Score"] = df["combined"].apply(relevance_score)

    df = df[df["Product"] != "Ignore"]

    # -------------------------------
    # FILTERS (OLD STYLE)
    # -------------------------------
    col1, col2 = st.columns(2)

    with col1:
        product_filter = st.multiselect(
            "Filter by Product",
            options=df["Product"].unique(),
            default=df["Product"].unique()
        )

    with col2:
        comp_filter = st.multiselect(
            "Filter by Competitor",
            options=df["Competitor"].unique(),
            default=df["Competitor"].unique()
        )

    df_filtered = df[
        (df["Product"].isin(product_filter)) &
        (df["Competitor"].isin(comp_filter))
    ]

    # -------------------------------
    # TABLE (OLD LOOK)
    # -------------------------------
    df_filtered = df_filtered.sort_values(by="Relevance Score", ascending=False)

    df_filtered["Title"] = df_filtered.apply(
        lambda x: f'<a href="{x["link"]}" target="_blank">{x["title"]}</a>',
        axis=1
    )

    st.write(
        df_filtered[["Title", "Competitor", "Product", "Relevance Score"]]
        .to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
