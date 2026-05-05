import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Transformer Intelligence", layout="wide")

st.title("🔌 Transformer Intelligence Dashboard")
st.caption("Live competitor & product tracking")

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

# -------------------------------
# PRODUCT LOGIC (FIXED)
# -------------------------------
PRODUCT_KEYWORDS = {
    "Oil Filled Transformer": [
        "oil filled transformer",
        "oil immersed transformer",
        "transformer oil",
        "mineral oil transformer",
        "onan transformer",
        "onaf transformer",
        "ofaf cooling",
        "oil cooled transformer"
    ],
    "Dry Type VPI Transformer": [
        "vpi transformer",
        "vacuum pressure impregnated transformer"
    ],
    "Dry Type CRT Transformer": [
        "cast resin transformer",
        "crt transformer",
        "cast coil transformer",
        "epoxy resin transformer"
    ]
}

EXCLUDE_KEYWORDS = [
    "crude oil", "oil prices", "oil & gas",
    "petroleum", "refinery", "diesel", "fuel"
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
            published = entry.get("published", "")

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
                "published": published,
                "text": text
            })

    return pd.DataFrame(articles)

# -------------------------------
# RUN PIPELINE
# -------------------------------
if st.button("🔄 Fetch Latest News"):

    df = fetch_news()

    df["combined"] = df["title"] + " " + df["text"]

    df["product"] = df["combined"].apply(classify_product)
    df["competitor"] = df["combined"].apply(detect_competitor)
    df["score"] = df["combined"].apply(relevance_score)

    df = df[df["product"] != "Ignore"]

    # -------------------------------
    # DASHBOARD TABS
    # -------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🏢 Competitors",
        "⚙️ Products",
        "📰 Articles"
    ])

    # -------------------------------
    # OVERVIEW
    # -------------------------------
    with tab1:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Articles", len(df))
        col2.metric("High Relevance", len(df[df["score"] > 70]))

        if len(df) > 0:
            col3.metric("Top Competitor", df["competitor"].value_counts().idxmax())
            col4.metric("Top Product", df["product"].value_counts().idxmax())

        st.markdown("---")

        st.subheader("Competitor Activity")
        comp_df = df["competitor"].value_counts().reset_index()
        comp_df.columns = ["Competitor", "Count"]
        st.bar_chart(comp_df.set_index("Competitor"))

        st.subheader("Product Split")
        prod_df = df["product"].value_counts().reset_index()
        prod_df.columns = ["Product", "Count"]
        st.bar_chart(prod_df.set_index("Product"))

    # -------------------------------
    # COMPETITOR TAB
    # -------------------------------
    with tab2:
        selected_comp = st.selectbox("Select Competitor", df["competitor"].unique())
        comp_df = df[df["competitor"] == selected_comp]
        st.dataframe(comp_df[["title", "product", "score"]])

    # -------------------------------
    # PRODUCT TAB
    # -------------------------------
    with tab3:
        selected_prod = st.selectbox("Select Product", df["product"].unique())
        prod_df = df[df["product"] == selected_prod]
        st.dataframe(prod_df[["title", "competitor", "score"]])

    # -------------------------------
    # ARTICLES TAB
    # -------------------------------
    with tab4:
        df = df.sort_values(by="score", ascending=False)

        df["title_link"] = df.apply(
            lambda x: f'<a href="{x["link"]}" target="_blank">{x["title"]}</a>',
            axis=1
        )

        st.write(
            df[["title_link", "competitor", "product", "score"]]
            .to_html(escape=False, index=False),
            unsafe_allow_html=True
        )

    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
