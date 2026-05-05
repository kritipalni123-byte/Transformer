import streamlit as st
import feedparser
import pandas as pd
import plotly.express as px
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time
import json
import logging
import random
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="TransformerIntel · India",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #05060f !important; color: #f0f0ff; }
.hero {
    background: linear-gradient(135deg,#0a1628 0%,#1a2d50 55%,#0d1f3a 100%);
    padding: 26px 28px 20px; position: relative; overflow: hidden;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.hero::before {
    content:''; position:absolute; top:-50px; right:-30px;
    width:240px; height:240px;
    background:radial-gradient(circle,rgba(56,189,248,0.12),transparent 70%);
    border-radius:50%;
}
.hero-title {
    font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800;
    background:linear-gradient(90deg,#fff 25%,#38bdf8 60%,#818cf8 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:4px;
}
.hero-sub { font-size:0.74rem; color:#666; }
.hero-pills { display:flex; gap:8px; margin-top:12px; flex-wrap:wrap; }
.hero-pill {
    background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3);
    border-radius:20px; padding:3px 12px; font-size:0.65rem; color:#38bdf8;
}
.mcard {
    border-radius:12px; padding:16px 14px; position:relative;
    overflow:hidden; margin-bottom:4px;
}
.mcard::after {
    content:''; position:absolute; top:0; left:0; right:0;
    height:3px; border-radius:12px 12px 0 0;
}
.mc1{background:linear-gradient(135deg,#0a1628,#1e3a5f);} .mc1::after{background:linear-gradient(90deg,#38bdf8,#7dd3fc);}
.mc2{background:linear-gradient(135deg,#1a0a2e,#2d1b69);} .mc2::after{background:linear-gradient(90deg,#818cf8,#a5b4fc);}
.mc3{background:linear-gradient(135deg,#051a10,#064e3b);} .mc3::after{background:linear-gradient(90deg,#10b981,#34d399);}
.mc4{background:linear-gradient(135deg,#1a1000,#78350f);} .mc4::after{background:linear-gradient(90deg,#f59e0b,#fcd34d);}
.mc5{background:linear-gradient(135deg,#1a0510,#6b0f1a);} .mc5::after{background:linear-gradient(90deg,#ff5e62,#ff9966);}
.mnum{font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;line-height:1.1;}
.mc1 .mnum{color:#7dd3fc;} .mc2 .mnum{color:#a5b4fc;} .mc3 .mnum{color:#34d399;} .mc4 .mnum{color:#fcd34d;} .mc5 .mnum{color:#ff8585;}
.mlbl{font-size:0.6rem;text-transform:uppercase;letter-spacing:1.5px;color:#555;margin-top:4px;}
.mdelta{font-size:0.67rem;color:#34d399;margin-top:3px;}
.ncard {
    background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:14px 16px; margin-bottom:10px;
    display:flex; gap:14px; align-items:flex-start;
    transition:border-color 0.2s,background 0.2s;
}
.ncard:hover{border-color:rgba(56,189,248,0.25);background:rgba(56,189,248,0.03);}
.score-ring{
    flex-shrink:0; width:46px; height:46px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-family:'Syne',sans-serif; font-weight:800; font-size:0.78rem;
}
.ring-high{background:linear-gradient(135deg,#ff5e62,#ff9966);color:#fff;}
.ring-med{background:linear-gradient(135deg,#f59e0b,#fcd34d);color:#000;}
.ring-low{background:rgba(255,255,255,0.07);color:#888;border:1px solid #2a2a3a;}
.ring-ig{background:#111;color:#333;border:1px solid #222;}
.ntitle{font-size:0.87rem;font-weight:600;color:#e8e8ff;margin-bottom:5px;line-height:1.4;}
.nbadges{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:4px;}
.nbadge{font-size:0.6rem;font-weight:700;padding:2px 8px;border-radius:20px;letter-spacing:0.5px;text-transform:uppercase;}
.nb-ma  {background:rgba(124,58,237,0.18);color:#a78bfa;border:1px solid rgba(124,58,237,0.3);}
.nb-cap {background:rgba(56,189,248,0.15);color:#7dd3fc;border:1px solid rgba(56,189,248,0.3);}
.nb-tech{background:rgba(16,185,129,0.15);color:#34d399;border:1px solid rgba(16,185,129,0.3);}
.nb-prod{background:rgba(245,158,11,0.15);color:#fcd34d;border:1px solid rgba(245,158,11,0.3);}
.nb-reg {background:rgba(255,94,98,0.15);color:#ff8585;border:1px solid rgba(255,94,98,0.3);}
.nb-mkt {background:rgba(6,182,212,0.15);color:#67e8f9;border:1px solid rgba(6,182,212,0.3);}
.nb-fin {background:rgba(52,211,153,0.12);color:#6ee7b7;border:1px solid rgba(52,211,153,0.3);}
.nb-oth {background:rgba(255,255,255,0.05);color:#666;border:1px solid #2a2a3a;}
.nb-hi  {background:rgba(255,94,98,0.18);color:#ff8585;border:1px solid rgba(255,94,98,0.35);}
.nb-med {background:rgba(245,158,11,0.15);color:#fcd34d;border:1px solid rgba(245,158,11,0.3);}
.nb-low {background:rgba(255,255,255,0.05);color:#888;border:1px solid #333;}
.nb-comp{background:rgba(56,189,248,0.15);color:#7dd3fc;border:1px solid rgba(56,189,248,0.3);}
.nmeta{font-size:0.65rem;color:#444;line-height:1.7;margin-top:4px;}
.sbar-wrap{background:rgba(255,255,255,0.05);border-radius:4px;height:4px;margin:5px 0 2px 0;}
.sbar{height:4px;border-radius:4px;}
.score-bd{background:#0a0a1a;border:1px solid #1a1a2e;border-radius:6px;
          padding:7px 12px;font-size:0.63rem;color:#555;margin-top:6px;line-height:1.6;}
.sec-title{font-family:'Syne',sans-serif;font-size:0.88rem;font-weight:700;
           color:#e0e0ff;margin:16px 0 12px 0;}
.comp-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);
           border-radius:12px;padding:14px 16px;margin-bottom:10px;}
.sh{font-family:'Syne',sans-serif;font-size:0.63rem;text-transform:uppercase;
    letter-spacing:1.8px;color:#38bdf8;margin:16px 0 6px 0;
    border-bottom:1px solid rgba(56,189,248,0.2);padding-bottom:4px;}
div[data-testid="stSidebarContent"]{background:#07071a !important;border-right:1px solid rgba(255,255,255,0.05);}
.stButton>button{
    background:linear-gradient(135deg,#38bdf8,#818cf8) !important;
    color:#000 !important;border:none !important;font-weight:700 !important;
    border-radius:8px !important;width:100% !important;
}
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,0.02);border-radius:10px;padding:4px;gap:4px;border:1px solid rgba(255,255,255,0.06);}
.stTabs [data-baseweb="tab"]{border-radius:8px;color:#666;font-size:0.8rem;font-weight:500;padding:8px 16px;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(56,189,248,0.15),rgba(129,140,248,0.12)) !important;color:#fff !important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MASTER DATA — from transformer_keyword_master_exhaustive.xlsx
# ══════════════════════════════════════════════════════════════════

COMPETITORS = [
    "Siemens","GE","Hitachi","CG","Schneider","TARIL","ABB","Toshiba",
    "Bharat Bijilee","Shirdi Sai","Telawne","Voltamp","Silchar",
    "Kotsons","DICAB","Uttam","Danish","Kirloskar","Viviana Power Tech",
]
COMP_NAMES = [c.lower() for c in COMPETITORS]

# ── Product Line 1: CRT (Cast Resin Transformer / Dry Type) ──────
KW_CRT_GENERIC = [
    # Core
    "cast resin transformer","dry type transformer","epoxy transformer",
    # Voltage spec
    "11kV cast resin transformer","33kV cast resin transformer",
    "66kV cast resin transformer","132kV cast resin transformer",
    "220kV cast resin transformer","11kV dry type transformer",
    "33kV dry type transformer","66kV dry type transformer",
    "132kV dry type transformer","220kV dry type transformer",
    "11kV epoxy transformer","33kV epoxy transformer",
    # Capacity spec
    "500 kVA cast resin transformer","1000 kVA cast resin transformer",
    "10 MVA cast resin transformer","50 MVA cast resin transformer",
    "500 kVA dry type transformer","1000 kVA dry type transformer",
    "10 MVA dry type transformer","50 MVA dry type transformer",
    # Standards
    "IEC 60076 cast resin transformer","IEC 60076-11 cast resin transformer",
    "IS 2026 cast resin transformer","IEC 60076 dry type transformer",
    "IEC 60076-11 dry type transformer","IS 2026 dry type transformer",
    "IEC 60076 epoxy transformer","IS 2026 epoxy transformer",
    # Cooling
    "ONAN cast resin transformer","ONAF cast resin transformer",
    "AN dry type transformer","AF dry type transformer",
]

KW_CRT_INDIA = [
    "cast resin transformer India","dry type transformer India",
    "cast resin transformer manufacturer India",
    "dry type transformer manufacturer India",
    "epoxy resin transformer India",
    "cast resin transformer market India",
    "cast resin transformer price India",
    "IS 2026 transformer India","IEC 60076-11 transformer India",
    "indoor transformer India","fire safe transformer India",
    "cast resin transformer order India","dry type transformer order India",
    "cast resin transformer plant India","dry type transformer capacity India",
    "cast resin transformer 2025 India","dry type transformer 2026 India",
]

# ── Product Line 2: VPI (Vacuum Pressure Impregnated) ────────────
KW_VPI_GENERIC = [
    # Core
    "VPI transformer","vacuum pressure impregnated transformer",
    "vacuum impregnated transformer",
    # Voltage spec
    "11kV VPI transformer","33kV VPI transformer",
    "66kV VPI transformer","132kV VPI transformer","220kV VPI transformer",
    "11kV vacuum pressure impregnated transformer",
    "33kV vacuum pressure impregnated transformer",
    "66kV vacuum pressure impregnated transformer",
    # Capacity spec
    "500 kVA VPI transformer","1000 kVA VPI transformer",
    "10 MVA VPI transformer","50 MVA VPI transformer",
    "500 kVA vacuum pressure impregnated transformer",
    "1000 kVA vacuum pressure impregnated transformer",
    # Standards
    "IEC 60076 VPI transformer","IEC 60076-11 VPI transformer",
    "IS 2026 VPI transformer",
    "IEC 60076 vacuum pressure impregnated transformer",
    "IS 2026 vacuum pressure impregnated transformer",
]

KW_VPI_INDIA = [
    "VPI transformer India","vacuum pressure impregnated transformer India",
    "VPI transformer manufacturer India",
    "VPI transformer market India","VPI transformer order India",
    "vacuum impregnated transformer India",
    "VPI transformer plant India","VPI transformer 2025 India",
    "IEC 60076 VPI transformer India","IS 2026 VPI transformer India",
]

# ── Product Line 3: Oil (Oil Filled / Oil Immersed / Power) ──────
KW_OIL_GENERIC = [
    # Core
    "oil filled transformer","oil immersed transformer","power transformer",
    # Voltage spec
    "11kV oil filled transformer","33kV oil filled transformer",
    "66kV oil filled transformer","132kV oil filled transformer",
    "220kV oil filled transformer","11kV oil immersed transformer",
    "33kV oil immersed transformer","66kV oil immersed transformer",
    "132kV oil immersed transformer","11kV power transformer",
    "33kV power transformer","66kV power transformer",
    "132kV power transformer","220kV power transformer",
    # Capacity spec
    "500 kVA oil filled transformer","1000 kVA oil filled transformer",
    "10 MVA oil filled transformer","50 MVA oil filled transformer",
    "10 MVA power transformer","50 MVA power transformer",
    "100 MVA power transformer","500 MVA power transformer",
    # Standards
    "IEC 60076 oil filled transformer","IS 2026 oil filled transformer",
    "IEC 60076 oil immersed transformer","IS 2026 oil immersed transformer",
    "IEC 60076 power transformer","IS 2026 power transformer",
    # Cooling
    "ONAN transformer","ONAF transformer","OFAF transformer","ODAF transformer",
]

KW_OIL_INDIA = [
    "oil filled transformer India","oil immersed transformer India",
    "power transformer India","power transformer manufacturer India",
    "oil filled transformer manufacturer India",
    "oil immersed transformer manufacturer India",
    "power transformer market India","power transformer order India",
    "power transformer India 2025","oil filled transformer India 2025",
    "IS 2026 power transformer India","IEC 60076 transformer India",
    "power transformer capacity India","oil immersed transformer plant India",
    "distribution transformer India","step down transformer India",
    "step up transformer India","substation transformer India",
    "grid transformer India","PGCIL transformer India",
    "NTPC transformer India","power grid transformer India",
]

# ── Competitor-specific search keywords (High priority, curated) ──
COMP_KEYWORDS_CRT = [
    "Siemens cast resin transformer India","Siemens dry type transformer India",
    "ABB cast resin transformer India","ABB dry type transformer India",
    "Siemens 11kV cast resin transformer","Siemens 33kV dry type transformer",
    "ABB 11kV cast resin transformer","ABB IEC 60076-11 cast resin transformer",
    "GE cast resin transformer India","Hitachi cast resin transformer India",
    "Schneider dry type transformer India","CG cast resin transformer India",
    "Kirloskar cast resin transformer","Voltamp dry type transformer",
    "TARIL cast resin transformer","Bharat Bijilee dry type transformer",
    "Kotsons cast resin transformer India","Uttam dry type transformer India",
]

COMP_KEYWORDS_VPI = [
    "Siemens VPI transformer India","ABB VPI transformer India",
    "Siemens vacuum pressure impregnated transformer",
    "ABB vacuum pressure impregnated transformer",
    "GE VPI transformer India","Hitachi VPI transformer India",
    "CG VPI transformer India","Schneider VPI transformer India",
    "Kirloskar VPI transformer","Voltamp VPI transformer",
    "TARIL VPI transformer India","Kotsons VPI transformer India",
]

COMP_KEYWORDS_OIL = [
    "Siemens oil filled transformer India","ABB oil filled transformer India",
    "Siemens power transformer India","ABB power transformer India",
    "GE power transformer India","Hitachi power transformer India",
    "Siemens 132kV power transformer","ABB 220kV power transformer",
    "GE 132kV oil filled transformer","Hitachi oil immersed transformer India",
    "CG power transformer India","Schneider oil filled transformer India",
    "Kirloskar power transformer India","Voltamp oil filled transformer",
    "TARIL oil filled transformer India","Bharat Bijilee power transformer",
    "Kotsons oil filled transformer India","Uttam power transformer India",
    "DICAB oil filled transformer India","Danish power transformer",
]

ALL_KEYWORD_GROUPS = {
    "🔵 CRT — Generic":        KW_CRT_GENERIC,
    "🔵 CRT — India Market":   KW_CRT_INDIA,
    "🟣 VPI — Generic":        KW_VPI_GENERIC,
    "🟣 VPI — India Market":   KW_VPI_INDIA,
    "🟤 Oil — Generic":        KW_OIL_GENERIC,
    "🟤 Oil — India Market":   KW_OIL_INDIA,
    "🏭 Competitor CRT":       COMP_KEYWORDS_CRT,
    "🏭 Competitor VPI":       COMP_KEYWORDS_VPI,
    "🏭 Competitor Oil":       COMP_KEYWORDS_OIL,
}

ALL_CRT_KW = KW_CRT_GENERIC + KW_CRT_INDIA + COMP_KEYWORDS_CRT
ALL_VPI_KW = KW_VPI_GENERIC + KW_VPI_INDIA + COMP_KEYWORDS_VPI
ALL_OIL_KW = KW_OIL_GENERIC + KW_OIL_INDIA + COMP_KEYWORDS_OIL

# ── Product tokens for relevance matching ────────────────────────
PRODUCT_TOKENS = [
    # CRT / Dry type — must have "transformer" anchor
    "cast resin transformer","dry type transformer","epoxy transformer",
    "epoxy resin transformer","cast resin transformer india",
    "dry type transformer india","resin transformer",
    # VPI
    "vpi transformer","vacuum pressure impregnated transformer",
    "vacuum impregnated transformer","vpi transformer india",
    # Oil / Power
    "oil filled transformer","oil immersed transformer","power transformer",
    "distribution transformer","oil filled transformer india",
    "power transformer india","oil immersed transformer india",
    # Spec-anchored (safe — always paired with transformer)
    "11kv transformer","33kv transformer","66kv transformer",
    "132kv transformer","220kv transformer",
    "kva transformer","mva transformer","mva power transformer",
    "onan transformer","onaf transformer","ofaf transformer","odaf transformer",
]

STANDARDS_TOKENS = [
    "iec 60076","iec 60076-11","is 2026","is 1180",
    "bis transformer","bis certification transformer",
    "qco transformer","quality control order transformer",
]

# ── Broad domain signals for disqualify gate ────────────────────
BROAD_TRANSFORMER_SIGNALS = [
    "cast resin transformer","dry type transformer","epoxy transformer",
    "vpi transformer","vacuum pressure impregnated transformer",
    "oil filled transformer","oil immersed transformer","power transformer",
    "distribution transformer","resin transformer",
    "11kv transformer","33kv transformer","66kv transformer",
    "132kv transformer","220kv transformer",
    "iec 60076","is 2026","is 1180","transformer manufacturer india",
    "transformer market india","transformer order india",
    "transformer capacity india","transformer plant india",
    "siemens","abb","hitachi","schneider","kirloskar","voltamp",
    "taril","kotsons","uttam","dicab","danish","bharat bijilee",
    "shirdi sai","telawne","silchar","viviana power","cg transformer",
    "ge transformer",
]

# ── Always block (unrelated transformer context) ─────────────────
ALWAYS_BLOCK = [
    # Wrong-context "transformer"
    "netflix transformer","transformers movie","transformers film",
    "transformers cartoon","transformers toy","optimus prime",
    "megatron transformer","autobot","decepticon",
    "power transformer workout","fitness transformer",
    "transformer costume","transformer toy review",
    # Wrong electrical equipment (not transformers)
    "circuit breaker","switchgear panel","cable gland","mcb manufacturer",
    "electrical wire manufacturer","motor manufacturer",
    # Academic/journal
    "journal of","doi:10.","pubmed","ieee xplore","sciencedirect",
    "research paper abstract","springer nature","elsevier",
    # Consumer
    "home appliance","consumer electronic","smartphone","laptop",
    "television","washing machine","refrigerator",
    # Instrument transformer (different product)
    "current transformer ct","potential transformer pt",
    "instrument transformer","measurement transformer",
]

# ── Category mapping ─────────────────────────────────────────────
INTENT_SCORES = {
    "Investment / Capacity Expansion": 100,
    "M&A / Partnership":               100,
    "New Product Launch":               90,
    "Technology / Innovation":          85,
    "Regulatory / Compliance":          80,
    "Large Order / Contract":           75,
    "General News / Mention":           40,
    "Irrelevant":                        0,
}
INTENT_TO_CAT = {
    "Investment / Capacity Expansion": "Capacity Development",
    "M&A / Partnership":               "M&A / Partnerships",
    "New Product Launch":              "New Product Launch",
    "Technology / Innovation":         "Technology Update",
    "Regulatory / Compliance":         "Regulatory Change",
    "Large Order / Contract":          "Market Expansion",
    "General News / Mention":          "Other",
    "Irrelevant":                      "Other",
}
CATEGORIES = [
    "M&A / Partnerships","Capacity Development","Technology Update",
    "New Product Launch","Regulatory Change","Market Expansion",
    "Financial Results","Other",
]
CAT_BADGE = {
    "M&A / Partnerships":"nb-ma","Capacity Development":"nb-cap",
    "Technology Update":"nb-tech","New Product Launch":"nb-prod",
    "Regulatory Change":"nb-reg","Market Expansion":"nb-mkt",
    "Financial Results":"nb-fin","Other":"nb-oth",
}
CAT_COLORS = {
    "M&A / Partnerships":"#a78bfa","Capacity Development":"#7dd3fc",
    "Technology Update":"#34d399","New Product Launch":"#fcd34d",
    "Regulatory Change":"#ff8585","Market Expansion":"#67e8f9",
    "Financial Results":"#6ee7b7","Other":"#444",
}

# ── Keyword scoring map ───────────────────────────────────────────
KEYWORD_SCORE_MAP = [
    # Brand + product → 100
    ("siemens cast resin transformer",100,"Brand+Product"),
    ("siemens dry type transformer",100,"Brand+Product"),
    ("siemens vpi transformer",100,"Brand+Product"),
    ("siemens oil filled transformer",100,"Brand+Product"),
    ("siemens power transformer",100,"Brand+Product"),
    ("abb cast resin transformer",100,"Brand+Product"),
    ("abb dry type transformer",100,"Brand+Product"),
    ("abb vpi transformer",100,"Brand+Product"),
    ("abb oil filled transformer",100,"Brand+Product"),
    ("abb power transformer",100,"Brand+Product"),
    ("ge cast resin transformer",100,"Brand+Product"),
    ("ge power transformer",100,"Brand+Product"),
    ("hitachi cast resin transformer",100,"Brand+Product"),
    ("hitachi power transformer",100,"Brand+Product"),
    ("cg cast resin transformer",100,"Brand+Product"),
    ("cg power transformer",100,"Brand+Product"),
    ("schneider dry type transformer",100,"Brand+Product"),
    ("kirloskar transformer",100,"Brand+Product"),
    ("voltamp transformer",100,"Brand+Product"),
    ("taril transformer",100,"Brand+Product"),
    ("kotsons transformer",100,"Brand+Product"),
    ("bharat bijilee transformer",100,"Brand+Product"),
    ("uttam transformer",100,"Brand+Product"),
    ("dicab transformer",100,"Brand+Product"),
    ("danish transformer",100,"Brand+Product"),
    ("shirdi sai transformer",100,"Brand+Product"),
    ("telawne transformer",100,"Brand+Product"),
    ("silchar transformer",100,"Brand+Product"),
    ("viviana power transformer",100,"Brand+Product"),
    # Standards → 90
    ("iec 60076",90,"Standard"),("iec 60076-11",90,"Standard"),
    ("is 2026",90,"Standard"),("is 1180",90,"Standard"),
    ("bis transformer",90,"Standard"),("qco transformer",90,"Standard"),
    # Specs → 80
    ("11kv cast resin",80,"Spec"),("33kv cast resin",80,"Spec"),
    ("66kv cast resin",80,"Spec"),("132kv cast resin",80,"Spec"),
    ("11kv dry type",80,"Spec"),("33kv dry type",80,"Spec"),
    ("66kv dry type",80,"Spec"),("132kv dry type",80,"Spec"),
    ("11kv vpi",80,"Spec"),("33kv vpi",80,"Spec"),
    ("11kv oil filled",80,"Spec"),("33kv oil filled",80,"Spec"),
    ("66kv oil filled",80,"Spec"),("132kv oil filled",80,"Spec"),
    ("132kv power transformer",80,"Spec"),("220kv power transformer",80,"Spec"),
    ("mva transformer",80,"Spec"),("mva power transformer",80,"Spec"),
    ("kva transformer",80,"Spec"),
    # Core products → 70
    ("cast resin transformer",70,"Core"),("dry type transformer",70,"Core"),
    ("epoxy transformer",70,"Core"),("vpi transformer",70,"Core"),
    ("vacuum pressure impregnated transformer",70,"Core"),
    ("oil filled transformer",70,"Core"),("oil immersed transformer",70,"Core"),
    ("power transformer",70,"Core"),("distribution transformer",70,"Core"),
    ("resin transformer",70,"Core"),
    # Cooling → 50
    ("onan transformer",50,"Cooling"),("onaf transformer",50,"Cooling"),
    ("ofaf transformer",50,"Cooling"),("odaf transformer",50,"Cooling"),
    # Generic → 20
    ("transformer india",20,"Generic"),("transformer manufacturer",20,"Generic"),
    ("transformer market",20,"Generic"),("transformer order",20,"Generic"),
]

# ══════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════════
SYSTEM_INTENT_PROMPT = """
You are a senior market intelligence analyst for a transformer manufacturer in India.
Products: Cast Resin Transformers (CRT), VPI Transformers, Oil Filled/Power Transformers.
Competitors: Siemens, ABB, GE, Hitachi, CG, Schneider, TARIL, Toshiba, Kirloskar, Voltamp,
  Bharat Bijilee, Kotsons, DICAB, Uttam, Danish, Shirdi Sai, Telawne, Silchar, Viviana Power Tech.
Geography: INDIA market focus.

STEP 1 — DOMAIN VALIDATION
First verify this is genuinely about transformer manufacturing/supply.
Return intent="Irrelevant" if:
- "transformer" refers to a movie/cartoon (Transformers, Optimus Prime)
- Article is about instrument/current/potential transformers (CT/PT) — different product
- Article is about electrical equipment that is NOT transformers

STEP 2 — CLASSIFY INTENT (exactly one):
- Investment / Capacity Expansion
- M&A / Partnership
- New Product Launch
- Technology / Innovation
- Regulatory / Compliance
- Large Order / Contract
- General News / Mention
- Irrelevant

Return ONE key insight max 12 words, India-market focused.

Reply ONLY in valid JSON: {"intent":"...","confidence":75,"key_insight":"..."}
"""

SYSTEM_DEDUP_PROMPT = """
Determine if two transformer industry news headlines describe the EXACT SAME business event.
YES if: same company + same action + same product/project/deal value.
NO if: different companies, different projects, different stages (announced vs completed).
Output ONLY: YES or NO
"""

# ══════════════════════════════════════════════════════════════════
# FILTER & SCORING ENGINE
# ══════════════════════════════════════════════════════════════════

def has_product_token(text):
    for t in PRODUCT_TOKENS + STANDARDS_TOKENS:
        if t in text: return True, t
    return False, None

def get_comp_hits(text):
    return [c for c in COMP_NAMES if c in text]

def is_disqualified(title, summary, source):
    text = (title + " " + summary + " " + source).lower()
    for s in ALWAYS_BLOCK:
        if s in text:
            hpt, _ = has_product_token(text)
            if not hpt:
                return True, f"Blocked: '{s}'"
    if not any(sig in text for sig in BROAD_TRANSFORMER_SIGNALS):
        return True, "No transformer domain signal"
    return False, ""

def is_relevant(title, summary):
    text = (title + " " + summary).lower()
    t_low = title.lower()
    comp_hits = get_comp_hits(text)
    has_comp  = len(comp_hits) > 0
    hpt, tok  = has_product_token(text)

    if has_comp and hpt: return True, comp_hits
    if len(comp_hits) >= 2: return True, comp_hits
    std = [s for s in STANDARDS_TOKENS if s in text]
    if std: return True, comp_hits
    if hpt:
        pm = [t for t in PRODUCT_TOKENS if t in text]
        strong = [t for t in pm if len(t.split()) >= 3]
        if strong: return True, comp_hits
        if len(pm) >= 2: return True, comp_hits
    if has_comp and any(t in t_low for t in PRODUCT_TOKENS):
        return True, comp_hits
    # Rule5: India + business event + transformer product
    ind = any(i in text for i in ["india","indian","maharashtra","delhi","mumbai",
              "gujarat","chennai","pune","bis","pgcil","ntpc","powergrid"])
    biz = any(b in text for b in ["launch","launches","unveiled","opens","inaugurated",
              "mandatory","production line","factory","order","contract","expands","capacity"])
    prd = any(p in text for p in ["transformer","cast resin","dry type","vpi","oil filled",
              "oil immersed","power transformer","distribution transformer"])
    if ind and biz and prd: return True, comp_hits
    return False, comp_hits

def compute_kw_score(title, summary):
    text_full  = (title + " " + summary).lower()
    text_title = title.lower()
    best, best_type, high_ct = 0, "Generic", 0
    for pat, base, ktype in KEYWORD_SCORE_MAP:
        if pat in text_full:
            if base > best: best, best_type = base, ktype
            if base >= 70: high_ct += 1
    if best == 0: return 10, "None"
    score = best
    if any(pat in text_title for pat, base, _ in KEYWORD_SCORE_MAP if base == best): score += 10
    if high_ct >= 2: score += 10
    return min(score, 100), best_type

def compute_comp_score(text):
    hits = get_comp_hits(text)
    if not hits: return 20, []
    bonus = len(hits) >= 2
    return min(100 + (10 if bonus else 0), 100), hits

def compute_intent_kw(title, summary):
    t = (title + " " + summary).lower()
    if any(k in t for k in ["new plant","expansion","invest","greenfield","new facility","capacity increase","new manufacturing"]):
        return 100,"Investment / Capacity Expansion"
    if any(k in t for k in ["acqui","merger","joint venture","partnership","stake","buyout","takeover","collaboration"]):
        return 100,"M&A / Partnership"
    if any(k in t for k in ["launch","new product","new model","introduces","unveil","new range","new transformer"]):
        return 90,"New Product Launch"
    if any(k in t for k in ["innovation","patent","r&d","technology","new design","smart transformer","digital transformer"]):
        return 85,"Technology / Innovation"
    if any(k in t for k in ["regulat","standard","compliance","bis","qco","mandatory","is 2026","iec 60076","certification"]):
        return 80,"Regulatory / Compliance"
    if any(k in t for k in ["contract","order","supply","tender","award","procurement","large order","supply agreement"]):
        return 75,"Large Order / Contract"
    return 40,"General News / Mention"

def final_score(kw, comp, intent, w_kw=0.4, w_comp=0.3, w_intent=0.3):
    return round((kw * w_kw) + (comp * w_comp) + (intent * w_intent))

def score_label(score):
    if score >= 80: return "🔥 High",   "nb-hi"
    if score >= 60: return "⚡ Medium",  "nb-med"
    if score >= 40: return "🟡 Low",    "nb-low"
    return "❌ Ignore","nb-oth"

def ring_cls(score):
    if score >= 80: return "ring-high"
    if score >= 60: return "ring-med"
    if score >= 40: return "ring-low"
    return "ring-ig"

def sbar_html(score):
    c = ("#ff5e62" if score>=80 else "#f59e0b" if score>=60 else "#f7b731" if score>=40 else "#333")
    return f'<div class="sbar-wrap"><div class="sbar" style="width:{min(score,100)}%;background:{c};"></div></div>'

# ══════════════════════════════════════════════════════════════════
# DEDUPLICATION
# ══════════════════════════════════════════════════════════════════
def deduplicate(articles, threshold=0.82):
    unique = []
    for art in articles:
        dup = False
        words_a = set(w for w in art["title"].lower().split() if len(w) > 3)
        for kept in unique:
            words_b = set(w for w in kept["title"].lower().split() if len(w) > 3)
            if len(words_a & words_b) < 2: continue
            if SequenceMatcher(None, art["title"].lower(), kept["title"].lower()).ratio() >= threshold:
                if art.get("relevance",0) > kept.get("relevance",0):
                    unique.remove(kept); unique.append(art)
                dup = True; break
        if not dup: unique.append(art)
    return unique

# ══════════════════════════════════════════════════════════════════
# LLM INTENT
# ══════════════════════════════════════════════════════════════════
def _call_groq(client, prompt, max_retries=3, initial_delay=2.0):
    delay = initial_delay
    for attempt in range(1, max_retries+1):
        try:
            resp = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role":"user","content":prompt}],
                max_tokens=120, temperature=0.1,
            )
            raw = resp.choices[0].message.content.strip()
            raw = raw.replace("```json","").replace("```","").strip()
            return json.loads(raw)
        except json.JSONDecodeError:
            logging.warning(f"Attempt {attempt}: JSON parse error")
            return None
        except Exception as e:
            err = str(e).lower()
            if "rate" in err or "429" in err:
                if attempt < max_retries:
                    logging.warning(f"Rate limit. Retrying in {delay:.1f}s...")
                    time.sleep(delay); delay *= 2
                else: return None
            else:
                logging.error(f"Groq error: {e}"); return None
    return None

def classify_llm(articles, api_key):
    if not api_key:
        for a in articles:
            is_, intent = compute_intent_kw(a["title"], a["summary"])
            a["intent"]=intent; a["intent_score"]=is_; a["confidence"]=40
            a["category"]=INTENT_TO_CAT.get(intent,"Other")
            a["key_insight"]="Add Groq API key for AI insights"
        return articles
    client = Groq(api_key=api_key)
    for a in articles:
        t, s = a["title"], a["summary"][:300]
        prompt = SYSTEM_INTENT_PROMPT + f"\n\nTitle: {t}\nSummary: {s}"
        result = _call_groq(client, prompt)
        if result:
            intent = result.get("intent","General News / Mention")
            if intent not in INTENT_SCORES: intent = "General News / Mention"
            a["intent"]      = intent
            a["intent_score"]= INTENT_SCORES[intent]
            a["confidence"]  = max(0,min(100,int(result.get("confidence",50))))
            a["category"]    = INTENT_TO_CAT.get(intent,"Other")
            a["key_insight"] = result.get("key_insight","—")
        else:
            is_, intent = compute_intent_kw(a["title"],a["summary"])
            a["intent"]=intent; a["intent_score"]=is_; a["confidence"]=30
            a["category"]=INTENT_TO_CAT.get(intent,"Other"); a["key_insight"]="—"
        time.sleep(0.5)
    return articles

# ══════════════════════════════════════════════════════════════════
# FETCH PIPELINE
# ══════════════════════════════════════════════════════════════════
def fetch_google_news(query, days_back=30, max_retries=3):
    COMP_NAMES_FULL = [c.lower() for c in COMPETITORS]
    is_comp_query = (any(c in query.lower() for c in COMP_NAMES_FULL)
                     and len(query.split()) <= 4)
    iq = query if (is_comp_query or "india" in query.lower()) else f"{query} India"
    encoded = urllib.parse.quote(iq)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=15,
                headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"})
            if response.status_code == 429:
                logging.error(f"Rate limit 429 for: {query[:40]}")
                time.sleep(60); return []
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            if not feed.version and not feed.entries: return []
            if not feed.entries: return []

            cutoff = None if days_back is None else datetime.now() - timedelta(days=days_back)
            q_lower = query.lower()
            q_words = [w for w in q_lower.split()
                       if len(w)>=4 and w not in ("india","with","from","that","this","have","been","transformer")]
            out = []
            for e in feed.entries:
                title = e.get("title","")
                link  = e.get("link","")
                t_lower = title.lower()
                source = ""
                desc = e.get("description","") or e.get("summary","")
                if desc:
                    try:
                        soup = BeautifulSoup(desc,"html.parser")
                        ft = soup.find("font")
                        if ft: source = ft.text.strip()
                    except: pass
                if not source: source = e.get("source",{}).get("title","Unknown")
                summary_text = e.get("summary","").lower()
                full_text = t_lower + " " + source.lower() + " " + summary_text

                # Per-query gate: any meaningful word matches
                matched = any(w in full_text for w in q_words) if q_words else True
                if not matched: continue

                try:    pub = datetime(*e.published_parsed[:6])
                except: pub = datetime.now()
                if cutoff and pub < cutoff: continue

                out.append({
                    "title":t_lower.title(), "link":link,"published":pub,
                    "source":source,"summary":e.get("summary","")[:500],"query":query,
                })
            logging.info(f"Fetched {len(out)} for: {query[:50]}")
            return out
        except requests.exceptions.Timeout:
            wait = random.uniform(5,10)+attempt*8
            logging.warning(f"Timeout attempt {attempt+1}. Wait {wait:.1f}s")
            time.sleep(wait)
        except requests.exceptions.RequestException as e:
            wait = random.uniform(3,8)+attempt*5
            logging.error(f"Network error: {e}. Wait {wait:.1f}s")
            time.sleep(wait)
        except Exception as e:
            logging.critical(f"Unexpected error: {e}"); return []
    return []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_news(queries_tuple, days_back, api_key, w_kw, w_comp, w_intent):
    raw = []
    for q in queries_tuple:
        raw.extend(fetch_google_news(q, days_back))
        time.sleep(random.uniform(0.5, 1.5))

    # Exact dedup
    seen, deduped = set(), []
    for a in raw:
        if a["title"] not in seen: seen.add(a["title"]); deduped.append(a)

    # Disqualify
    kept, removed = [], []
    for a in deduped:
        disq, reason = is_disqualified(a["title"], a["summary"], a["source"])
        if disq: a["discard_reason"]=reason; removed.append(a)
        else: kept.append(a)

    # Relevance filter
    relevant, irrelevant = [], []
    for a in kept:
        rel, comp_hits = is_relevant(a["title"], a["summary"])
        if rel: a["comp_hits_rel"]=comp_hits; relevant.append(a)
        else:
            a["discard_reason"]="Failed relevance filter"
            irrelevant.append(a)
    removed += irrelevant

    # Score
    for a in relevant:
        text = (a["title"]+" "+a["summary"]).lower()
        kw_s, kw_type      = compute_kw_score(a["title"], a["summary"])
        cs,   comp_hits    = compute_comp_score(text)
        is_,  intent       = compute_intent_kw(a["title"], a["summary"])
        fs = final_score(kw_s, cs, is_, w_kw, w_comp, w_intent)
        a.update({
            "kw_score":kw_s,"kw_type":kw_type,"comp_score":cs,"comp_hits":comp_hits,
            "intent":intent,"intent_score":is_,"relevance":fs,
            "category":INTENT_TO_CAT.get(intent,"Other"),"key_insight":"","confidence":40,
            "score_breakdown":(f"KW:{kw_s}({kw_type})×{w_kw} + "
                               f"Comp:{cs}({'|'.join(comp_hits) if comp_hits else 'none'})×{w_comp} + "
                               f"Intent:{is_}({intent})×{w_intent} = {fs}"),
        })

    # Fuzzy dedup
    relevant = deduplicate(relevant, threshold=0.82)

    # LLM
    relevant = classify_llm(relevant, api_key)

    # Re-score with LLM intent
    for a in relevant:
        fs = final_score(a["kw_score"], a["comp_score"], a["intent_score"], w_kw, w_comp, w_intent)
        a["relevance"] = fs
        a["score_breakdown"] = (f"KW:{a['kw_score']}({a['kw_type']})×{w_kw} + "
                                 f"Comp:{a['comp_score']}({'|'.join(a['comp_hits']) if a['comp_hits'] else 'none'})×{w_comp} + "
                                 f"Intent:{a['intent_score']}({a['intent']})×{w_intent} = {fs}")
    relevant.sort(key=lambda x: x["relevance"], reverse=True)
    return relevant, removed

def build_queries(sel_comp, sel_groups, inc_comp_kw):
    q = list(sel_comp)
    for g in sel_groups: q.extend(ALL_KEYWORD_GROUPS.get(g,[]))
    if inc_comp_kw:
        q.extend(COMP_KEYWORDS_CRT + COMP_KEYWORDS_VPI + COMP_KEYWORDS_OIL)
    seen, u = set(), []
    for x in q:
        if x not in seen: seen.add(x); u.append(x)
    return u

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🔌 TransformerIntel")
    st.markdown("**Transformer Business · 🇮🇳 India**")
    st.markdown('<div style="background:linear-gradient(90deg,#38bdf8,#818cf8);height:2px;border-radius:2px;margin-bottom:16px;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh">🔑 API Key</div>', unsafe_allow_html=True)
    try:    api_key = st.secrets.get("GROQ_API_KEY","")
    except: api_key = ""
    if not api_key:
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")

    st.markdown('<div class="sh">🏭 Competitors</div>', unsafe_allow_html=True)
    sel_comp = st.multiselect("Select competitors", COMPETITORS, default=COMPETITORS[:8])
    new_co   = st.text_input("➕ Add competitor", placeholder="e.g. Kirloskar Electric")
    if new_co: sel_comp.append(new_co)

    st.markdown('<div class="sh">📦 Product Lines & Keywords</div>', unsafe_allow_html=True)
    sel_groups = st.multiselect(
        "Keyword groups",
        list(ALL_KEYWORD_GROUPS.keys()),
        default=list(ALL_KEYWORD_GROUPS.keys()),
    )
    inc_comp_kw = st.checkbox("Competitor-specific keywords", value=True)

    st.markdown('<div class="sh">📅 Time & Filters</div>', unsafe_allow_html=True)
    time_option = st.selectbox(
        "Time range",
        ["Last 7 days","Last 14 days","Last 30 days","Last 60 days","Last 90 days","No limit"],
        index=2,
    )
    TIME_MAP = {"Last 7 days":7,"Last 14 days":14,"Last 30 days":30,
                "Last 60 days":60,"Last 90 days":90,"No limit":None}
    days_back = TIME_MAP[time_option]

    selected_cats = st.multiselect("Categories", CATEGORIES, default=CATEGORIES)
    min_score     = st.slider("Min score (0–100)", 0, 100, 20,
                               help="20+ catches general market news. 60+ = high confidence.")
    show_discard   = st.checkbox("Show discarded articles", value=False)
    show_breakdown = st.checkbox("Show score breakdown",    value=False)

    st.markdown('<div class="sh">⚖️ Score Weights</div>', unsafe_allow_html=True)
    w_kw     = st.slider("Keyword weight",    0.0,1.0,0.4,0.05)
    w_comp   = st.slider("Competitor weight", 0.0,1.0,0.3,0.05)
    w_intent = st.slider("Intent weight",     0.0,1.0,0.3,0.05)
    wt = round(w_kw+w_comp+w_intent,2)
    if abs(wt-1.0)>0.05: st.warning(f"⚠️ Weights sum to {wt}")

    fetch_btn = st.button("🔌 Fetch & Analyse News")

# ══════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-title">Transformer Market Intelligence · India</div>
  <div class="hero-sub">CRT · VPI · Oil Filled · 19 Competitors · 2500+ Keywords · AI-Powered</div>
  <div class="hero-pills">
    <span class="hero-pill">🔵 Cast Resin (CRT)</span>
    <span class="hero-pill">🟣 VPI</span>
    <span class="hero-pill">🟤 Oil Filled</span>
    <span class="hero-pill">🇮🇳 India Focus</span>
    <span class="hero-pill">⚡ Weighted Scoring</span>
    <span class="hero-pill">🔁 Deduplication ON</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════
if fetch_btn or "t_intel_data" in st.session_state:
    if fetch_btn:
        queries = build_queries(sel_comp, sel_groups, inc_comp_kw)
        st.info(f"🔍 Running **{len(queries)} queries** · ⏱️ {time_option} · India-focused · dedup ON")
        with st.spinner("Fetching, filtering, scoring…"):
            st.session_state["_groq_key"] = api_key or ""
            kept, removed = fetch_all_news(
                tuple(queries), days_back, api_key or "",
                w_kw, w_comp, w_intent
            )
            st.session_state["t_intel_data"]   = kept
            st.session_state["t_removed_data"] = removed

    kept    = st.session_state.get("t_intel_data",   [])
    removed = st.session_state.get("t_removed_data", [])
    df      = pd.DataFrame(kept)    if kept    else pd.DataFrame()
    df_rem  = pd.DataFrame(removed) if removed else pd.DataFrame()

    if df.empty:
        st.warning("⚠️ No articles found. Try: (1) 'No limit' time range, (2) lower Min Score to 10, (3) check keyword group selections.")
    else:
        df_f = df[df["category"].isin(selected_cats) & (df["relevance"]>=min_score)].copy()

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📰 Intelligence Feed","🏭 Competitors","📦 Products","📋 Regulatory","📈 Trends"
        ])

        # ── TAB 1: FEED ───────────────────────────────────────────
        with tab1:
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            c1,c2,c3,c4,c5 = st.columns(5)
            for col, val, lbl, cls, delta in [
                (c1, len(df_f),                                         "Relevant Articles","mc1",f"of {len(df)} total"),
                (c2, len(df_f[df_f["relevance"]>=80]),                  "🔥 High Priority", "mc2","score ≥ 80"),
                (c3, len(removed),                                       "Auto-Filtered",    "mc3","noise removed"),
                (c4, len(df_f[df_f["intent"]=="M&A / Partnership"]),    "M&A Signals",      "mc4","partnerships · deals"),
                (c5, round(df_f["relevance"].mean(),1) if len(df_f) else 0,"Avg Score",     "mc5","out of 100"),
            ]:
                col.markdown(
                    f'<div class="mcard {cls}"><div class="mnum">{val}</div>'
                    f'<div class="mlbl">{lbl}</div><div class="mdelta">{delta}</div></div>',
                    unsafe_allow_html=True)

            st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

            ch1, ch2 = st.columns(2)
            with ch1:
                cat_df = df_f["category"].value_counts().reset_index()
                cat_df.columns = ["Category","Count"]
                fig = px.bar(cat_df, x="Count", y="Category", orientation="h",
                             color="Category", color_discrete_map=CAT_COLORS,
                             title="Articles by Category")
                fig.update_layout(plot_bgcolor="#0a0a1a",paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#888",showlegend=False,
                    title_font=dict(family="Syne",size=13,color="#e0e0ff"),
                    margin=dict(l=10,r=10,t=36,b=10),
                    xaxis=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e"))
                st.plotly_chart(fig, use_container_width=True)
            with ch2:
                bands = pd.cut(df_f["relevance"],bins=[0,39,59,79,100],
                               labels=["❌ <40","🟡 40–59","⚡ 60–79","🔥 80–100"])
                bd = bands.value_counts().reset_index(); bd.columns=["Band","Count"]
                fig2 = px.bar(bd, x="Band", y="Count", color="Band",
                              color_discrete_map={"🔥 80–100":"#ff5e62","⚡ 60–79":"#f59e0b",
                                                  "🟡 40–59":"#f7b731","❌ <40":"#2a2a3a"},
                              title="Score Distribution")
                fig2.update_layout(plot_bgcolor="#0a0a1a",paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#888",showlegend=False,
                    title_font=dict(family="Syne",size=13,color="#e0e0ff"),
                    margin=dict(l=10,r=10,t=36,b=10),
                    xaxis=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e"))
                st.plotly_chart(fig2, use_container_width=True)

            fc1,fc2,fc3 = st.columns([2,1,1])
            with fc1: srch = st.text_input("🔎 Search","",placeholder="e.g. Siemens, IEC 60076, cast resin…")
            with fc2:
                fp = st.selectbox("Product Line",["All","CRT","VPI","Oil Filled"])
            with fc3: sb = st.selectbox("Sort",["Highest score","Latest first"])

            df_show = df_f.copy()
            if srch: df_show = df_show[df_show["title"].str.contains(srch,case=False,na=False)]
            if fp != "All":
                pm = {"CRT":ALL_CRT_KW,"VPI":ALL_VPI_KW,"Oil Filled":ALL_OIL_KW}
                df_show = df_show[df_show["query"].isin(pm[fp])]
            if sb=="Latest first": df_show = df_show.sort_values("published",ascending=False)

            st.markdown(
                f'<div style="font-size:0.76rem;color:#444;margin-bottom:10px;">'
                f'Showing <b style="color:#e0e0ff">{len(df_show)}</b> articles · '
                f'<b style="color:#444">{len(removed)}</b> removed</div>',
                unsafe_allow_html=True)

            for _, row in df_show.iterrows():
                sc   = row.get("relevance",0)
                slbl, sbdg = score_label(sc)
                cbc  = CAT_BADGE.get(row.get("category","Other"),"nb-oth")
                comp_str = ", ".join(row.get("comp_hits",[]) or []) or "—"
                ki   = row.get("key_insight","—") or "—"
                bd   = row.get("score_breakdown","—")
                conf = row.get("confidence","—")
                st.markdown(f"""
                <div class="ncard">
                  <div class="score-ring {ring_cls(sc)}">{sc}</div>
                  <div style="flex:1;min-width:0;">
                    <div class="ntitle">
                      <a href="{row['link']}" target="_blank" style="color:#e8e8ff;text-decoration:none;">{row['title']}</a>
                    </div>
                    <div class="nbadges">
                      <span class="nbadge {cbc}">{row.get('category','—')}</span>
                      <span class="nbadge {sbdg}">{slbl} {sc}/100</span>
                      <span class="nbadge nb-comp">🏭 {comp_str}</span>
                    </div>
                    {sbar_html(sc)}
                    <div class="nmeta">
                      🗞️ {row['source']} &nbsp;|&nbsp;
                      📅 {row['published'].strftime('%d %b %Y')} &nbsp;|&nbsp;
                      🎯 {row.get('intent','—')} &nbsp;|&nbsp;
                      🔵 Confidence: {conf}% &nbsp;|&nbsp;
                      💡 {ki}
                    </div>
                    {"<div class='score-bd'>📐 "+bd+"</div>" if show_breakdown else ""}
                  </div>
                </div>""", unsafe_allow_html=True)

            if show_discard and not df_rem.empty:
                st.markdown("---")
                st.markdown(f"**❌ Discarded ({len(df_rem)})**")
                for _, row in df_rem.iterrows():
                    st.markdown(f"""
                    <div class="ncard" style="opacity:0.35;border-color:#1a1a2e;">
                      <div class="score-ring ring-ig">✗</div>
                      <div style="flex:1;"><div class="ntitle" style="color:#444;">{row['title']}</div>
                      <div class="nmeta">❌ {row.get('discard_reason','—')} · 🗞️ {row['source']}</div></div>
                    </div>""", unsafe_allow_html=True)

            # Export
            st.markdown("---")
            e1,e2,e3 = st.columns(3)
            ec = ["title","category","relevance","intent","intent_score","confidence",
                  "kw_score","comp_score","comp_hits","key_insight","score_breakdown","source","published","link"]
            out      = df_show[[c for c in ec if c in df_show.columns]].copy()
            full     = df[[c for c in ec if c in df.columns]].copy()
            comp_only= df[df["comp_hits"].apply(lambda x: isinstance(x,list) and len(x)>0)][[c for c in ec if c in df.columns]].copy()
            for d in [out,full,comp_only]:
                if "published" in d.columns: d["published"]=d["published"].dt.strftime("%Y-%m-%d")
            with e1: st.download_button("⬇️ Filtered CSV",out.to_csv(index=False),
                        f"transformer_intel_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
            with e2: st.download_button("⬇️ Full CSV",full.to_csv(index=False),
                        f"transformer_full_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
            with e3: st.download_button(f"⬇️ Competitor CSV ({len(comp_only)})",comp_only.to_csv(index=False),
                        f"transformer_comp_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")

        # ── TAB 2: COMPETITORS ────────────────────────────────────
        with tab2:
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">🏭 Competitor Activity</div>', unsafe_allow_html=True)
            colors = ["#38bdf8","#a78bfa","#34d399","#fcd34d","#ff8585","#67e8f9",
                      "#fb923c","#f472b6","#a3e635","#e879f9","#7dd3fc","#86efac",
                      "#fdba74","#c4b5fd","#6ee7b7","#fca5a5","#93c5fd","#d9f99d","#f9a8d4"]
            rows = []
            for i,cn in enumerate(COMP_NAMES):
                mask = df["comp_hits"].apply(lambda x: cn in x if isinstance(x,list) else False)
                sub  = df[mask]
                if len(sub)==0: continue
                col = colors[i%len(colors)]
                pct = int(sub["relevance"].mean())
                rows.append({"Competitor":cn.title(),"Articles":len(sub),"Avg Score":pct,
                              "High":len(sub[sub["relevance"]>=80]),"Top Intent":sub["intent"].mode()[0],"Color":col})
                st.markdown(f"""
                <div class="comp-card">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.95rem;color:{col};">{cn.title()}</div>
                    <div style="display:flex;gap:6px;">
                      <span class="nbadge nb-med">{len(sub)} articles</span>
                      <span class="nbadge nb-hi">{len(sub[sub['relevance']>=80])} 🔥</span>
                    </div>
                  </div>
                  <div class="sbar-wrap" style="height:5px;"><div class="sbar" style="width:{pct}%;background:{col};height:5px;"></div></div>
                  <div class="nmeta" style="margin-top:5px;">Avg Score: <b style="color:{col};">{pct}/100</b> &nbsp;|&nbsp; Top Intent: {sub['intent'].mode()[0]}</div>
                </div>""", unsafe_allow_html=True)
            if rows:
                cdf = pd.DataFrame(rows)
                fig = px.bar(cdf,x="Competitor",y="Avg Score",color="Competitor",
                             color_discrete_sequence=colors,title="Competitor Avg Relevance Score")
                fig.update_layout(plot_bgcolor="#0a0a1a",paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#888",showlegend=False,
                    title_font=dict(family="Syne",size=13,color="#e0e0ff"),
                    margin=dict(l=10,r=10,t=36,b=10),
                    yaxis=dict(gridcolor="#1a1a2e",range=[0,100]),xaxis=dict(gridcolor="#1a1a2e"))
                st.plotly_chart(fig,use_container_width=True)

        # ── TAB 3: PRODUCTS ───────────────────────────────────────
        with tab3:
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">📦 Product Line Intelligence</div>', unsafe_allow_html=True)
            p1,p2,p3 = st.columns(3)
            for col,em,lbl,kws,cls in [
                (p1,"🔵","Cast Resin (CRT)",ALL_CRT_KW,"mc1"),
                (p2,"🟣","VPI Transformer", ALL_VPI_KW,"mc2"),
                (p3,"🟤","Oil Filled / Power",ALL_OIL_KW,"mc3"),
            ]:
                sub = df[df["query"].isin(kws)] if "query" in df.columns else pd.DataFrame()
                col.markdown(
                    f'<div class="mcard {cls}" style="text-align:left;">'
                    f'<div style="font-size:1.6rem;margin-bottom:4px;">{em}</div>'
                    f'<div class="mnum">{len(sub)}</div>'
                    f'<div class="mlbl">{lbl}</div>'
                    f'<div class="mdelta">Avg: {round(sub["relevance"].mean(),1) if len(sub) else 0}/100</div>'
                    f'</div>', unsafe_allow_html=True)

            for plbl,kws in [("🔵 CRT",ALL_CRT_KW),("🟣 VPI",ALL_VPI_KW),("🟤 Oil Filled",ALL_OIL_KW)]:
                sub = df_f[df_f["query"].isin(kws)].head(5) if "query" in df_f.columns else pd.DataFrame()
                if not sub.empty:
                    st.markdown(f'<div class="sec-title" style="margin-top:18px;">{plbl} — Top Articles</div>',unsafe_allow_html=True)
                    for _,row in sub.iterrows():
                        sc=row.get("relevance",0); sl,_=score_label(sc)
                        st.markdown(f"""
                        <div class="ncard">
                          <div class="score-ring {ring_cls(sc)}">{sc}</div>
                          <div style="flex:1;"><div class="ntitle">
                            <a href="{row['link']}" target="_blank" style="color:#e8e8ff;text-decoration:none;">{row['title']}</a>
                          </div>
                          <div class="nmeta">🗞️ {row['source']} · 📅 {row['published'].strftime('%d %b %Y')} · {sl}</div>
                          </div>
                        </div>""", unsafe_allow_html=True)

        # ── TAB 4: REGULATORY ─────────────────────────────────────
        with tab4:
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">📋 Regulatory & Standards · India</div>', unsafe_allow_html=True)
            reg = df_f[df_f["category"]=="Regulatory Change"]
            if reg.empty:
                st.info("No regulatory articles found. Try increasing the time range.")
            else:
                st.markdown(f'<div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.2);border-radius:10px;padding:12px 16px;font-size:0.78rem;color:#aaa;margin-bottom:14px;">⚠️ <b>{len(reg)} regulatory alerts</b> · Standards: IEC 60076 · IEC 60076-11 · IS 2026 · IS 1180 · BIS QCO · PGCIL specs</div>',unsafe_allow_html=True)
                for _,row in reg.iterrows():
                    sc=row.get("relevance",0); sl,_=score_label(sc)
                    st.markdown(f"""
                    <div class="ncard" style="border-color:rgba(56,189,248,0.25);">
                      <div class="score-ring {ring_cls(sc)}">{sc}</div>
                      <div style="flex:1;"><div class="ntitle">
                        <a href="{row['link']}" target="_blank" style="color:#e8e8ff;text-decoration:none;">{row['title']}</a>
                      </div>
                      <div class="nbadges"><span class="nbadge nb-reg">📋 Regulatory</span><span class="nbadge nb-hi">{sl} {sc}/100</span></div>
                      <div class="nmeta">🗞️ {row['source']} · 📅 {row['published'].strftime('%d %b %Y')} · 💡 {row.get('key_insight','—')}</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

        # ── TAB 5: TRENDS ─────────────────────────────────────────
        with tab5:
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">📈 Intelligence Trends</div>', unsafe_allow_html=True)
            if len(df_f)>0:
                df_f2 = df_f.copy()
                df_f2["week"] = df_f2["published"].dt.to_period("W").astype(str)
                trend = df_f2.groupby(["week","category"]).size().reset_index(name="count")
                fig_t = px.line(trend,x="week",y="count",color="category",
                                color_discrete_map=CAT_COLORS,
                                title="Weekly Intelligence Volume",markers=True)
                fig_t.update_layout(plot_bgcolor="#0a0a1a",paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#888",legend=dict(bgcolor="rgba(0,0,0,0)",font_size=10),
                    title_font=dict(family="Syne",size=13,color="#e0e0ff"),
                    margin=dict(l=10,r=10,t=36,b=10),
                    xaxis=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e"))
                st.plotly_chart(fig_t,use_container_width=True)
                sc_trend = df_f2.groupby("week")["relevance"].mean().reset_index()
                sc_trend.columns = ["week","avg_score"]
                fig_s = px.area(sc_trend,x="week",y="avg_score",title="Avg Relevance Score Over Time",
                                color_discrete_sequence=["#38bdf8"])
                fig_s.update_traces(fill="tozeroy",fillcolor="rgba(56,189,248,0.07)",line_color="#38bdf8")
                fig_s.update_layout(plot_bgcolor="#0a0a1a",paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#888",title_font=dict(family="Syne",size=13,color="#e0e0ff"),
                    margin=dict(l=10,r=10,t=36,b=10),
                    xaxis=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e"))
                st.plotly_chart(fig_s,use_container_width=True)

else:
    # Landing
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(56,189,248,0.05);border:1px solid rgba(56,189,248,0.2);border-radius:10px;padding:12px 16px;font-size:0.78rem;color:#aaa;margin-bottom:16px;">
    <b>📐 Formula:</b> Score = (Keyword × 0.4) + (Competitor × 0.3) + (Intent × 0.3) &nbsp;|&nbsp;
    🔥 80–100 Immediate &nbsp; ⚡ 60–79 Track &nbsp; 🟡 40–59 Optional &nbsp; ❌ &lt;40 Filtered
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">📦 Product Lines Tracked</div>', unsafe_allow_html=True)
    p1,p2,p3 = st.columns(3)
    for col,em,title,desc,cls in [
        (p1,"🔵","Cast Resin Transformer (CRT)",
         "IEC 60076-11 · IS 2026 · Dry Type · Epoxy\n11kV–220kV · 500kVA–50MVA · ONAN/ONAF/AN/AF",
         "mc1"),
        (p2,"🟣","VPI Transformer",
         "IEC 60076-11 · IS 2026 · Vacuum Pressure Impregnated\n11kV–220kV · 500kVA–50MVA",
         "mc2"),
        (p3,"🟤","Oil Filled / Power Transformer",
         "IEC 60076 · IS 2026 · Oil Immersed · Power\n11kV–220kV · 500kVA–500MVA · ONAN/ONAF/OFAF",
         "mc3"),
    ]:
        col.markdown(f"""
        <div class="mcard {cls}" style="text-align:left;padding:20px;min-height:130px;">
          <div style="font-size:2rem;margin-bottom:10px;">{em}</div>
          <div style="font-weight:700;color:#e0e0ff;font-size:0.85rem;margin-bottom:6px;">{title}</div>
          <div style="font-size:0.75rem;color:#555;line-height:1.6;white-space:pre-line;">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title" style="margin-top:20px;">🏭 Competitors Tracked (19)</div>', unsafe_allow_html=True)
    colors = ["#38bdf8","#a78bfa","#34d399","#fcd34d","#ff8585","#67e8f9",
              "#fb923c","#f472b6","#a3e635","#e879f9","#7dd3fc","#86efac",
              "#fdba74","#c4b5fd","#6ee7b7","#fca5a5","#93c5fd","#d9f99d","#f9a8d4"]
    cc = st.columns(5)
    for i,co in enumerate(COMPETITORS):
        with cc[i%5]:
            st.markdown(
                f'<div class="mcard" style="padding:10px;margin-bottom:8px;border-top:2px solid {colors[i%len(colors)]};">'
                f'<div style="font-size:0.78rem;color:#e0e0ff;font-weight:600;">{co}</div></div>',
                unsafe_allow_html=True)
