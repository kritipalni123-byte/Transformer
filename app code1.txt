import streamlit as st
import pandas as pd
import feedparser
from datetime import datetime
import time

st.title("⚡ Transformer Competitor Intelligence Dashboard")

# ----------------------------
# LOAD KEYWORDS FROM REPO
# ----------------------------
@st.cache_data
def load_keywords():
    df = pd.read_excel("data/transformer_keywords.xlsx")
    df = df.drop_duplicates()
    df = df[df["Priority"].isin(["High", "Medium"])]
    return df

keyword_df = load_keywords()
keywords = keyword_df["Keyword"].dropna().unique().tolist()

st.write(f"Loaded {len(keywords)} keywords")

# ----------------------------
# SCRAPER FUNCTION
# ----------------------------
def fetch_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}"
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", ""),
            "keyword": keyword,
            "scraped_at": datetime.now()
        })

    return articles

# ----------------------------
# RUN SCRAPER
# ----------------------------
if st.button("🔄 Fetch Latest News"):

    all_articles = []
    progress = st.progress(0)

    for i, keyword in enumerate(keywords[:200]):  # limit for speed
        try:
            articles = fetch_news(keyword)
            all_articles.extend(articles)
            time.sleep(0.3)
        except:
            continue

        progress.progress((i + 1) / len(keywords[:200]))

    df = pd.DataFrame(all_articles)

    # Deduplicate
    df["id"] = df["link"].apply(lambda x: hash(x))
    df = df.drop_duplicates(subset="id")

    # Basic scoring (no LLM needed)
    df["relevance_score"] = df["keyword"].apply(lambda x: 80 if "kv" in x.lower() or "mva" in x.lower() else 50)
    df["category"] = "general"

    df.to_csv("processed_articles.csv", index=False)

    st.success(f"✅ {len(df)} articles fetched")

# ----------------------------
# DISPLAY RESULTS
# ----------------------------
try:
    df = pd.read_csv("processed_articles.csv")
except:
    df = pd.DataFrame()

if not df.empty:
    st.dataframe(df[["title", "keyword", "relevance_score", "category"]])
else:
    st.info("Click 'Fetch Latest News' to begin")
