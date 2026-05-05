import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# -------------------------------
# CONFIG
# -------------------------------

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=transformer+industry",
    "https://news.google.com/rss/search?q=power+transformer",
]

COMPETITORS = [
    "ABB", "Siemens", "GE", "Hitachi", "CG", "Schneider",
    "Toshiba", "Bharat Bijlee", "Voltamp"
]

# -------------------------------
# PRODUCT KEYWORDS
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
    text = text.lower()

    # Exclude irrelevant oil context
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return "Ignore"

    # Must contain transformer context
    if "transformer" not in text:
        return "Ignore"

    # Match product
    for product, keywords in PRODUCT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return product

    return "Other Transformer"


def detect_competitor(text):
    for comp in COMPETITORS:
        if comp.lower() in text.lower():
            return comp
    return "Other"


def relevance_score(text):
    text = text.lower()
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

            # Try to fetch article content
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
# STREAMLIT UI
# -------------------------------

st.title("🔌 Transformer Competitor Intelligence Dashboard")

if st.button("Fetch Latest News"):

    df = fetch_news()

    # Apply classification
    df["product"] = df["text"].apply(classify_product)
    df["competitor"] = df["text"].apply(detect_competitor)
    df["score"] = df["text"].apply(relevance_score)

    # Remove ignored
    df = df[df["product"] != "Ignore"]

    # Sidebar filters
    st.sidebar.header("Filters")

    product_filter = st.sidebar.multiselect(
        "Product",
        options=df["product"].unique()
    )

    competitor_filter = st.sidebar.multiselect(
        "Competitor",
        options=df["competitor"].unique()
    )

    if product_filter:
        df = df[df["product"].isin(product_filter)]

    if competitor_filter:
        df = df[df["competitor"].isin(competitor_filter)]

    # Show high relevance first
    df = df.sort_values(by="score", ascending=False)

    # Clickable titles
    df["title_link"] = df.apply(
        lambda x: f'<a href="{x["link"]}" target="_blank">{x["title"]}</a>',
        axis=1
    )

    st.subheader("📊 Results")

    st.write(
        df[["title_link", "product", "competitor", "score"]]
        .to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

