import streamlit as st
import pandas as pd
import feedparser
from datetime import datetime
import time

st.set_page_config(page_title="Transformer Intelligence", layout="wide")

st.title("⚡ Transformer Competitor Intelligence Dashboard")

# ----------------------------
# LOAD KEYWORDS FROM EXCEL
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data/transformer_keywords.xlsx")

    # Clean
    df = df.drop_duplicates()
    df = df[df["Priority"].isin(["High", "Medium"])]

    return df

try:
    keyword_df = load_data()
except Exception as e:
    st.error("❌ Error loading Excel file. Check path: data/transformer_keywords.xlsx")
    st.stop()

keywords = keyword_df["Keyword"].dropna().unique().tolist()
competitors = keyword_df["Competitor"].dropna().unique().tolist()

st.success(f"Loaded {len(keywords)} keywords | {len(competitors)} competitors")

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
# DETECT COMPETITOR
# ----------------------------
def detect_competitor(text):
    text = str(text).lower()

    for comp in competitors:
        if comp.lower() in text:
            return comp

    return "Other"

# ----------------------------
# RUN SCRAPER
# ----------------------------
if st.button("🔄 Fetch Latest News"):

    all_articles = []
    progress = st.progress(0)

    # Limit keywords to avoid timeout
    run_keywords = keywords[:200]

    for i, keyword in enumerate(run_keywords):
        try:
            articles = fetch_news(keyword)
            all_articles.extend(articles)
            time.sleep(0.3)
        except:
            continue

        progress.progress((i + 1) / len(run_keywords))

    df = pd.DataFrame(all_articles)

    if df.empty:
        st.warning("No articles found")
        st.stop()

    # Deduplicate
    df["id"] = df["link"].apply(lambda x: hash(x))
    df = df.drop_duplicates(subset="id")

    # Detect competitor
    df["competitor"] = df["title"].apply(detect_competitor)

    # Simple relevance logic
    def score(row):
        score = 50

        if "kv" in row["keyword"].lower() or "mva" in row["keyword"].lower():
            score += 20

        if row["competitor"] != "Other":
            score += 20

        return min(score, 100)

    df["relevance_score"] = df.apply(score, axis=1)

    # Save
    df.to_csv("processed_articles.csv", index=False)

    st.success(f"✅ {len(df)} articles fetched & processed")

# ----------------------------
# DISPLAY DATA
# ----------------------------
try:
    df = pd.read_csv("processed_articles.csv")
except:
    df = pd.DataFrame()

if not df.empty:

    st.sidebar.header("Filters")

    selected_comp = st.sidebar.multiselect(
        "Competitor",
        options=sorted(df["competitor"].unique())
    )

    if selected_comp:
        df = df[df["competitor"].isin(selected_comp)]

    min_score = st.sidebar.slider("Min Relevance Score", 0, 100, 50)
    df = df[df["relevance_score"] >= min_score]

    st.subheader("📊 Results")

    st.dataframe(
        df[["title", "competitor", "keyword", "relevance_score"]],
        use_container_width=True
    )

else:
    st.info("Click 'Fetch Latest News' to begin")
