"""
tiktok_apify_app.py
TikTok Shop Intelligence Dashboard

Flow:
  1. Load JSON (converted from Excel) for category/hashtag/brand selection
  2. User picks categories/types → hashtags/keywords (Sheet 1 JSON)
  3. User picks brands → brand hashtags auto-populate (Sheet 2 JSON)
  4. Combined search sent to Apify clockworks/tiktok-scraper
  5. Filter: ALL sheet-1 tags must exist + AT LEAST ONE sheet-2 brand tag
  6. Dark pattern analysis via OpenAI gpt-4o-mini + LangChain (original Gemini prompt)
"""

import streamlit as st
import pandas as pd
import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import List, Optional

from apify_client import ApifyClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Utility path for original prompt
sys.path.append(os.path.join(os.path.dirname(__file__), "Utility"))
from Utility.config import get_default_gemini_prompt

load_dotenv()

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TikTok Shop Intelligence",
    page_icon="🎵",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.metric-card {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a42 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
    margin-bottom: 8px;
}
.metric-val { font-size: 1.7rem; font-weight: 700; color: #a78bfa; }
.metric-lbl { font-size: 0.75rem; color: #9ca3af; margin-top: 2px; }

.confirmed-badge {
    background: rgba(16,185,129,0.15);
    color: #6ee7b7;
    border: 1px solid rgba(16,185,129,0.35);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}
.not-confirmed-badge {
    background: rgba(239,68,68,0.15);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}
.tag {
    display: inline-block;
    background: rgba(139,92,246,0.18);
    color: #c4b5fd;
    border-radius: 6px;
    padding: 2px 7px;
    font-size: 0.73rem;
    margin: 2px;
}
.sec-header {
    font-size: 1rem;
    font-weight: 600;
    color: #e2e8f0;
    border-left: 3px solid #8b5cf6;
    padding-left: 10px;
    margin: 14px 0 8px 0;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# Pydantic models – same as original
# ════════════════════════════════════════════════════════════════════════════

class RegulatoryViolationReference(BaseModel):
    lawGuidance: str = Field(description="The law or guidance reference")
    articleClause: str = Field(description="The specific article or clause")
    highLevelSynthesis: str = Field(description="High-level synthesis of the violation")

class DarkPatternAnalysis(BaseModel):
    category: str = Field(description="The category of dark pattern identified")
    excerpt: str = Field(description="Specific excerpt from the content")
    sectionType: str = Field(description="Type of section (transcript, caption, or description)")
    reasoning: str = Field(description="Explanation of why this qualifies as a dark pattern")
    confidenceScore: int = Field(description="Confidence score (0-100)")
    regulatoryViolationReference: List[RegulatoryViolationReference] = Field(
        description="List of regulatory violations that apply to this dark pattern"
    )

class DarkPatternAnalysisResult(BaseModel):
    darkPatternAnalysis: List[DarkPatternAnalysis] = Field(
        description="List of dark patterns identified in the content"
    )
    overallConfidenceScore: int = Field(description="Overall confidence score (0-100)")
    productNames: List[str] = Field(description="List of product names mentioned")

# ════════════════════════════════════════════════════════════════════════════
# Session state
# ════════════════════════════════════════════════════════════════════════════

def init_session():
    for k, v in {
        "scraped_data": None,
        "analysis_results": {},
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ════════════════════════════════════════════════════════════════════════════
# JSON data loading (no pandas Excel reads in production)
# ════════════════════════════════════════════════════════════════════════════

DATA_DIR = os.path.join(os.path.dirname(__file__), "data_files")
S1_PATH = os.path.join(DATA_DIR, "sheet1_hashtags_keywords.json")
S2_PATH = os.path.join(DATA_DIR, "sheet2_brands.json")

@st.cache_data
def load_json_data():
    """Load both JSON files. Auto-regenerate from Excel if missing."""
    if not os.path.exists(S1_PATH) or not os.path.exists(S2_PATH):
        st.warning("⚠️ JSON files not found. Generating from Excel…")
        import subprocess, sys as _sys
        result = subprocess.run(
            [_sys.executable, "convert_excel_to_json.py"],
            capture_output=True, text=True,
            cwd=os.path.dirname(__file__)
        )
        if result.returncode != 0:
            st.error(f"Failed to generate JSON: {result.stderr}")
            return [], []

    with open(S1_PATH, encoding="utf-8") as f:
        sheet1 = json.load(f)
    with open(S2_PATH, encoding="utf-8") as f:
        sheet2 = json.load(f)
    return sheet1, sheet2

# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════

def extract_tags(raw: str) -> List[str]:
    """Parse hashtags/keywords from a raw string."""
    if not raw or raw in ("nan", ""):
        return []
    parts = re.split(r"[\s,]+", raw.strip())
    return [p.lstrip("#").strip().lower() for p in parts if p.strip()]

def video_tags_set(item: dict) -> set:
    """All hashtag names found in the video (from hashtags array + caption text)."""
    tags = set()
    for h in item.get("hashtags", []):
        name = h.get("name", h) if isinstance(h, dict) else str(h)
        tags.add(name.lower().lstrip("#").strip())
    text = (item.get("text", "") or "").lower()
    for word in text.split():
        if word.startswith("#"):
            tags.add(word.lstrip("#").strip())
    return tags

def fmt_num(n) -> str:
    try:
        n = int(n)
        if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
        if n >= 1_000:     return f"{n/1_000:.1f}K"
        return str(n)
    except Exception:
        return str(n)

def check_confirmation(item, s1_hashtags, s1_keywords, s2_tags):
    """
    Returns (confirmed: bool, reason: str)
    Rules:
      - ALL sheet-1 hashtags must be in video tags
      - ALL sheet-1 keywords must appear in caption text
      - AT LEAST ONE sheet-2 brand tag must be in video tags (if any selected)
    """
    vtags = video_tags_set(item)
    vtext = (item.get("text", "") or "").lower()

    missing_s1_tags = [t for t in s1_hashtags if t not in vtags]
    missing_s1_kw   = [k for k in s1_keywords  if k.lower() not in vtext]
    s2_ok = (not s2_tags) or any(t in vtags for t in s2_tags)
    missing_s2 = [] if s2_ok else [f"Need one of: {', '.join(['#'+t for t in s2_tags])}"]

    issues = []
    if missing_s1_tags:
        issues.append(f"Missing hashtags: {', '.join(['#'+t for t in missing_s1_tags])}")
    if missing_s1_kw:
        issues.append(f"Missing keywords: {', '.join(missing_s1_kw)}")
    if missing_s2:
        issues.extend(missing_s2)

    confirmed = not issues
    reason = " | ".join(issues) if issues else "All required tags/keywords matched"
    return confirmed, reason

# ════════════════════════════════════════════════════════════════════════════
# Apify scraping
# ════════════════════════════════════════════════════════════════════════════

def fetch_from_apify(api_key, hashtags, keywords, max_results, days_filter):
    client = ApifyClient(api_key)
    run_input = {
        "excludePinnedPosts": False,
        "hashtags": hashtags,
        "search": " ".join(keywords) if keywords else "",
        "resultsPerPage": max_results,
        "scrapeRelatedVideos": False,
        "shouldDownloadAvatars": False,
        "shouldDownloadCovers": False,
        "shouldDownloadMusicCovers": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadVideos": False,
        "profileScrapeSections": ["videos"],
        "profileSorting": "latest",
        "searchSection": "",
        "maxProfilesPerQuery": 10,
    }
    try:
        with st.spinner("🚀 Running Apify TikTok Scraper…"):
            run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
            results = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if days_filter:
            cutoff = (datetime.utcnow() - timedelta(days=days_filter)).timestamp()
            results = [r for r in results if r.get("createTime", 0) >= cutoff]
        return results
    except Exception as e:
        st.error(f"❌ Apify error: {e}")
        return None

# ════════════════════════════════════════════════════════════════════════════
# LLM analysis – OpenAI gpt-4o-mini + LangChain + ORIGINAL Gemini prompt
# ════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_structured_llm(api_key: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    return llm.with_structured_output(DarkPatternAnalysisResult)

def build_video_content_str(item: dict) -> str:
    """Build rich text description of all available video metadata for the LLM."""
    author   = item.get("authorMeta", {}) or {}
    music    = item.get("musicMeta", {}) or {}
    vmeta    = item.get("videoMeta", {}) or {}
    effects  = item.get("effectStickers", []) or []
    mentions = item.get("mentions", []) or []

    hashtag_names = [
        (h.get("name") if isinstance(h, dict) else str(h))
        for h in item.get("hashtags", [])
    ]
    text = item.get("text", "") or ""
    # pull extra hashtags from caption
    for word in text.split():
        if word.startswith("#") and word.lstrip("#") not in hashtag_names:
            hashtag_names.append(word.lstrip("#"))

    lines = [
        f"=== TikTok Video Metadata ===",
        f"Video URL       : {item.get('webVideoUrl', item.get('submittedVideoUrl', 'N/A'))}",
        f"Video ID        : {item.get('id', 'N/A')}",
        f"Created At      : {item.get('createTimeISO', 'N/A')}",
        f"Location        : {item.get('locationCreated', 'N/A')}",
        f"Language        : {item.get('textLanguage', 'N/A')}",
        f"Is Ad           : {item.get('isAd', False)}",
        f"Is Sponsored    : {item.get('isSponsored', False)}",
        f"Is Pinned       : {item.get('isPinned', False)}",
        f"Is Slideshow    : {item.get('isSlideshow', False)}",
        f"",
        f"--- Caption / Text ---",
        text or "(no caption)",
        f"",
        f"--- Hashtags ---",
        ", ".join(["#"+h for h in hashtag_names]) if hashtag_names else "(none)",
        f"",
        f"--- Mentions ---",
        ", ".join(mentions) if mentions else "(none)",
        f"",
        f"--- Author Info ---",
        f"Name            : {author.get('nickName', author.get('name', 'Unknown'))}",
        f"Handle          : @{author.get('name', 'unknown')}",
        f"Profile URL     : {author.get('profileUrl', 'N/A')}",
        f"Verified        : {author.get('verified', False)}",
        f"Followers       : {fmt_num(author.get('fans', 0))}",
        f"Total Likes     : {fmt_num(author.get('heart', 0))}",
        f"Total Videos    : {author.get('video', 0)}",
        f"Bio             : {author.get('signature', '')}",
        f"Bio Link        : {author.get('bioLink', 'N/A')}",
        f"TT Seller       : {author.get('ttSeller', False)}",
        f"Private Account : {author.get('privateAccount', False)}",
        f"",
        f"--- Traction Stats ---",
        f"Plays           : {fmt_num(item.get('playCount', 0))}",
        f"Likes           : {fmt_num(item.get('diggCount', 0))}",
        f"Comments        : {fmt_num(item.get('commentCount', 0))}",
        f"Shares          : {fmt_num(item.get('shareCount', 0))}",
        f"Saves/Collects  : {fmt_num(item.get('collectCount', 0))}",
        f"",
        f"--- Video Specs ---",
        f"Duration (s)    : {vmeta.get('duration', 'N/A')}",
        f"Resolution      : {vmeta.get('width', '?')}x{vmeta.get('height', '?')}",
        f"Format          : {vmeta.get('format', 'N/A')}",
        f"Definition      : {vmeta.get('definition', 'N/A')}",
        f"",
        f"--- Music ---",
        f"Name            : {music.get('musicName', 'N/A')}",
        f"Author          : {music.get('musicAuthor', 'N/A')}",
        f"Original Sound  : {music.get('musicOriginal', False)}",
        f"",
        f"--- Effects ---",
        ", ".join([e.get("name", "") for e in effects]) if effects else "(none)",
    ]
    return "\n".join(lines)

def analyse_video_openai(item: dict, openai_key: str) -> dict:
    """
    Run gpt-4o-mini structured analysis using the original Gemini prompt as system prompt.
    Messages are passed directly (not via ChatPromptTemplate) so that the JSON schema
    curly braces inside the Gemini prompt are never interpreted as template variables.
    """
    try:
        structured_llm = get_structured_llm(openai_key)
        original_prompt = get_default_gemini_prompt()
        video_content   = build_video_content_str(item)

        human_text = (
            "Analyse the following TikTok video for dark patterns and deceptive practices.\n\n"
            + video_content +
            "\n\nReturn the analysis as a valid JSON object following the schema described above."
        )

        # Pass messages directly — no template parsing, so {…} in Gemini prompt are safe
        messages = [
            SystemMessage(content=original_prompt),
            HumanMessage(content=human_text),
        ]

        result: DarkPatternAnalysisResult = structured_llm.invoke(messages)
        return {"success": True, "result": result.model_dump()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ════════════════════════════════════════════════════════════════════════════
# UI: video card (full info)
# ════════════════════════════════════════════════════════════════════════════

def render_video_card(item: dict, idx: int):
    author  = item.get("authorMeta", {}) or {}
    vmeta   = item.get("videoMeta",  {}) or {}
    music   = item.get("musicMeta",  {}) or {}
    effects = item.get("effectStickers", []) or []
    url     = item.get("webVideoUrl", item.get("submittedVideoUrl", "#"))
    caption = item.get("text", "") or "(no caption)"
    cover   = vmeta.get("coverUrl") or vmeta.get("originalCoverUrl")
    hashtag_names = [
        (h.get("name") if isinstance(h, dict) else str(h))
        for h in item.get("hashtags", [])
    ]
    confirmed = item.get("_confirmed", False)
    reason    = item.get("_not_confirmed_reason", "")

    img_col, info_col = st.columns([1, 3])
    with img_col:
        if cover:
            st.image(cover, use_container_width=True)
        else:
            st.markdown("🎵")

    with info_col:
        badge = ('<span class="confirmed-badge">✅ Confirmed</span>' if confirmed
                 else '<span class="not-confirmed-badge">❌ Not Confirmed</span>')
        st.markdown(badge, unsafe_allow_html=True)
        if not confirmed and reason:
            st.caption(f"Reason: {reason}")

        st.markdown(
            f"**[@{author.get('name','unknown')}]({author.get('profileUrl','#')})** "
            f"— {author.get('nickName','')} | "
            f"👥 {fmt_num(author.get('fans',0))} followers"
        )
        st.markdown(f"[🔗 Open Video on TikTok]({url})")
        st.caption(caption[:250] + ("…" if len(caption) > 250 else ""))

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("▶️ Plays",    fmt_num(item.get("playCount",0)))
        c2.metric("❤️ Likes",    fmt_num(item.get("diggCount",0)))
        c3.metric("💬 Comments", fmt_num(item.get("commentCount",0)))
        c4.metric("↗️ Shares",   fmt_num(item.get("shareCount",0)))
        c5.metric("⭐ Saves",    fmt_num(item.get("collectCount",0)))

        # Full metadata expandable
        with st.expander("📋 Full Video Metadata"):
            st.json({
                "id":              item.get("id"),
                "createdAt":       item.get("createTimeISO"),
                "location":        item.get("locationCreated"),
                "language":        item.get("textLanguage"),
                "isAd":            item.get("isAd"),
                "isSponsored":     item.get("isSponsored"),
                "isPinned":        item.get("isPinned"),
                "isSlideshow":     item.get("isSlideshow"),
                "duration_s":      vmeta.get("duration"),
                "resolution":      f"{vmeta.get('width')}×{vmeta.get('height')}",
                "format":          vmeta.get("format"),
                "definition":      vmeta.get("definition"),
                "music_name":      music.get("musicName"),
                "music_author":    music.get("musicAuthor"),
                "music_original":  music.get("musicOriginal"),
                "effects":         [e.get("name") for e in effects],
                "mentions":        item.get("mentions", []),
                "author_bio":      author.get("signature"),
                "author_bioLink":  author.get("bioLink"),
                "author_verified": author.get("verified"),
                "author_seller":   author.get("ttSeller"),
                "author_videos":   author.get("video"),
                "author_digg":     author.get("digg"),
                "author_friends":  author.get("friends"),
            })

        if hashtag_names:
            tags_html = " ".join([f'<span class="tag">#{h}</span>' for h in hashtag_names])
            st.markdown(tags_html, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# UI: analysis result
# ════════════════════════════════════════════════════════════════════════════

def render_analysis_result(res: dict):
    r = res.get("result", {})
    overall  = r.get("overallConfidenceScore", 0)
    products = r.get("productNames", [])
    patterns = r.get("darkPatternAnalysis", [])

    col1, col2 = st.columns([1, 3])
    col1.metric("Overall Confidence", f"{overall}%")
    if products:
        col2.markdown(f"**Products mentioned:** {', '.join(products)}")

    if not patterns:
        st.success("✅ No dark patterns detected in this video.")
        return

    for dp in patterns:
        score = dp.get("confidenceScore", 0)
        icon  = "🔴" if score >= 70 else "🟡" if score >= 40 else "🟢"
        with st.expander(f"{icon} **{dp.get('category','?')}** — Confidence: {score}%"):
            st.markdown(f"**Section:** `{dp.get('sectionType','')}`")
            st.markdown(f"**Excerpt:** _{dp.get('excerpt','')}_")
            st.markdown(f"**Reasoning:** {dp.get('reasoning','')}")
            refs = dp.get("regulatoryViolationReference", [])
            if refs:
                st.markdown("**Regulatory References:**")
                for ref in refs:
                    st.markdown(
                        f"- **{ref.get('lawGuidance','')}** "
                        f"§ _{ref.get('articleClause','')}_: "
                        f"{ref.get('highLevelSynthesis','')}"
                    )

# ════════════════════════════════════════════════════════════════════════════
# Architecture page
# ════════════════════════════════════════════════════════════════════════════

def render_architecture():
    st.header("🏗️ System Architecture & Flow")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Full Flow", "📋 Data Sources", "🔍 Filter Logic", "🤖 LLM Input"])

    # ── Tab 1: Full end-to-end flow ─────────────────────────────────────────
    with tab1:
        st.markdown("""
### End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXCEL WORKBOOK                              │
│  Sheet 1: Hashtags & Keywords  │  Sheet 2: Brands               │
│  (Category / Details / Type)   │  (Brand / Hashtags / Keywords) │
└────────────┬───────────────────┴──────────────┬─────────────────┘
             │  convert_excel_to_json.py         │
             ▼                                   ▼
  sheet1_hashtags_keywords.json       sheet2_brands.json
             │                                   │
             ▼                                   ▼
┌────────────────────────────────────────────────────────────────┐
│                   STEP 1 — USER SELECTION (UI)                 │
│                                                                │
│  Left panel                      Right panel                   │
│  ─────────────                   ───────────                   │
│  Select Category                 Select Brand(s)              │
│  Select Type                       → auto-populates all       │
│  Select Details (multi)              brand hashtags           │
│  → parsed as hashtags            → parsed as hashtags/kw      │
│           │                                   │                │
│           └──────────── COMBINED ─────────────┘                │
│                    hashtags + keywords                         │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              STEP 2 — APIFY SCRAPING                          │
│                                                               │
│  Actor: clockworks/tiktok-scraper                             │
│  Inputs:                                                      │
│    hashtags:       [all combined hashtags]                    │
│    search:         "keyword1 keyword2 ..."                    │
│    resultsPerPage: N (user-configured, 5-100)                 │
│    time filter:    applied client-side after fetch            │
│                                                               │
│  Returns: Full TikTok video JSON objects (see Data Sources)   │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              STEP 3 — HASHTAG FILTER (Confirmation)           │
│                                                               │
│  ✅ CONFIRMED if ALL of:                                      │
│     • ALL sheet-1 hashtags present in video tags              │
│     • ALL sheet-1 keywords present in caption text            │
│     • AT LEAST ONE sheet-2 brand tag present in video         │
│                                                               │
│  ❌ NOT CONFIRMED → reason stored per video                   │
│     e.g. "Missing hashtags: #ootd | Need one of: #HM #Zara"  │
│                                                               │
│  Two extra columns added to results table:                    │
│     Confirmed (Yes/No)   |   Not Confirmed Reason             │
└───────────────────────────┬───────────────────────────────────┘
                            │   User selects videos from table
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              STEP 4 — LLM DARK PATTERN ANALYSIS               │
│                                                               │
│  Model:   OpenAI gpt-4o-mini                                  │
│  Library: LangChain (.with_structured_output)                 │
│  System:  Original Gemini regulatory prompt (unchanged)       │
│  Human:   Full video metadata block (see LLM Input tab)       │
│                                                               │
│  Output (Pydantic → dict):                                    │
│    darkPatternAnalysis[]                                      │
│      ├ category          ├ excerpt        ├ sectionType       │
│      ├ reasoning         ├ confidenceScore                    │
│      └ regulatoryViolationReference[]                         │
│           ├ lawGuidance  ├ articleClause  └ highLevelSynthesis│
│    overallConfidenceScore                                     │
│    productNames[]                                             │
└───────────────────────────────────────────────────────────────┘
```
        """)

    # ── Tab 2: Data sources ─────────────────────────────────────────────────
    with tab2:
        st.markdown("""
### Excel → JSON Conversion

Run once (or whenever Excel changes):
```bash
python convert_excel_to_json.py
```

#### Sheet 1 — `sheet1_hashtags_keywords.json`
| Field | Description | Example |
|-------|-------------|---------|
| `category` | Top-level grouping | `"Fashion & Style"` |
| `details` | The raw hashtag/keyword string | `"#OOTD #OutfitInspo"` |
| `type` | `"Hashtag"` or `"KEYWORDS"` | `"Hashtag"` |

Each `details` entry is split on whitespace/commas and each tag is lowercased + `#` stripped for matching.

#### Sheet 2 — `sheet2_brands.json`
| Field | Description | Example |
|-------|-------------|---------|
| `brand` | Brand name (shown in UI) | `"H&M"` |
| `hashtags` | Brand-specific hashtag string | `"#HM #HMFashion"` |
| `keywords` | Additional brand keywords | `"Scandinavian fashion"` |

Both `hashtags` and `keywords` from a selected brand are combined and used in both the **Apify search query** and the **confirmation filter**.
        """)

    # ── Tab 3: Filter logic ─────────────────────────────────────────────────
    with tab3:
        st.markdown("""
### Hashtag Confirmation Logic

For every video returned by Apify, the app checks three conditions:

```python
# 1. Collect all hashtag names from the video
video_tags = {hashtag names from .hashtags[]} ∪ {#words in caption text}

# 2. Sheet-1 rule — ALL must be present
missing_s1_tags = [t for t in sheet1_hashtags if t not in video_tags]
missing_s1_kw   = [k for k in sheet1_keywords if k not in caption_text]

# 3. Sheet-2 rule — AT LEAST ONE must be present
sheet2_ok = any(t in video_tags for t in sheet2_brand_tags)

# 4. Final verdict
confirmed = (no missing_s1_tags) AND (no missing_s1_kw) AND sheet2_ok
```

**If no brands selected** from Sheet 2 → the brand check is skipped (pass by default).

#### Example reason strings
| Situation | Reason |
|-----------|--------|
| Missing a sheet-1 hashtag | `Missing hashtags: #ootd` |
| Missing a sheet-1 keyword | `Missing keywords: summer fashion` |
| No brand tag found | `Need one of: #HM, #HMFashion` |
| Multiple issues | `Missing hashtags: #ootd \| Need one of: #HM` |
        """)

    # ── Tab 4: LLM input ────────────────────────────────────────────────────
    with tab4:
        st.markdown("""
### What We Pass to GPT-4o-mini

Every selected video is analysed by sending **two messages** directly to the model (no template parsing — avoids `{curly brace}` conflicts with the Gemini prompt's JSON schema):

```
SystemMessage  →  Original Gemini dark-pattern regulatory prompt
                  (unchanged — same categories, same laws, same output schema)

HumanMessage   →  Full video metadata block (see below)
```

#### Exact Metadata Block Sent
```
=== TikTok Video Metadata ===
Video URL       : https://www.tiktok.com/@author/video/123
Video ID        : 7533731959172861206
Created At      : 2025-08-01T21:27:45.000Z
Location        : GB
Language        : en
Is Ad           : False
Is Sponsored    : False
Is Pinned       : False
Is Slideshow    : False

--- Caption / Text ---
Full caption text including emojis and hashtags

--- Hashtags ---
#OOTD, #FashionTok, #HM

--- Mentions ---
@username1, @username2

--- Author Info ---
Name            : AuthorNickName
Handle          : @handle
Profile URL     : https://www.tiktok.com/@handle
Verified        : False
Followers       : 2.2M
Total Likes     : 126M
Total Videos    : 1036
Bio             : SHOP THE E-BOOK OUT NOW
Bio Link        : https://myshopify.com/...
TT Seller       : False
Private Account : False

--- Traction Stats ---
Plays           : 573.9K
Likes           : 25.9K
Comments        : 346
Shares          : 352
Saves/Collects  : 1.4K

--- Video Specs ---
Duration (s)    : 74
Resolution      : 576x1024
Format          : mp4
Definition      : 540p

--- Music ---
Name            : original sound
Author          : AuthorName
Original Sound  : True

--- Effects ---
Green Screen
```

#### Why this matters for analysis
| Field | Dark pattern signal |
|-------|---------------------|
| `Is Ad / Is Sponsored` | Undisclosed commercial intent |
| `Bio Link` | Affiliate / shop link without disclosure |
| `Caption text` | Urgency language, vague disclosure terms |
| `Hashtags` | `#ad`, `#collab`, `#sp` presence/absence |
| `Followers + Likes` | Implied social proof manipulation |
| `Traction stats` | Inflated engagement signals |
| `Music (original)` | Branded/sponsored sound tracks |
| `Effects` (e.g. Green Screen) | Misleading visual context |
        """)

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    st.sidebar.title("🎵 TikTok Scraper")
    page = st.sidebar.radio("Navigate", ["🔍 Scrape & Analyse", "🏗️ Architecture & Flow"])

    if page == "🏗️ Architecture & Flow":
        render_architecture()
        return

    # API Keys
    st.sidebar.divider()
    st.sidebar.header("🔑 API Keys")
    apify_key  = st.sidebar.text_input("Apify API Key",  value=os.getenv("API_KEY", ""),         type="password")
    openai_key = st.sidebar.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""),   type="password")

    if not apify_key or not openai_key:
        st.warning("⚠️ Enter both API keys in the sidebar.")
        st.stop()

    st.title("🎵 TikTok Scraper")
    st.caption("Scrape TikTok with Excel-curated hashtags · filter by brand presence · analyse dark patterns with ai")

    # Load JSON data
    sheet1, sheet2 = load_json_data()
    if not sheet1 or not sheet2:
        st.error("❌ Could not load data. Run `python convert_excel_to_json.py` first.")
        st.stop()

    # ══════════════════════════════════════════════════════════════════════
    # STEP 1 — Selection
    # ══════════════════════════════════════════════════════════════════════
    st.header("1️⃣  Select Hashtags & Keywords")
    left, right = st.columns(2, gap="large")

    # ── Sheet 1: Category / Type / Details ──────────────────────────────
    with left:
        st.markdown('<div class="sec-header">📋 Sheet 1 — Category-based hashtags/keywords</div>', unsafe_allow_html=True)

        all_cats = sorted(set(e["category"] for e in sheet1))
        sel_cat  = st.selectbox("Category", ["(All)"] + all_cats, key="sel_cat")

        sub1 = sheet1 if sel_cat == "(All)" else [e for e in sheet1 if e["category"] == sel_cat]

        all_types = sorted(set(e["type"] for e in sub1))
        sel_type  = st.selectbox("Type", ["(All)"] + all_types, key="sel_type")

        if sel_type != "(All)":
            sub1 = [e for e in sub1 if e["type"] == sel_type]

        detail_options = [e["details"] for e in sub1]
        sel_details    = st.multiselect("Select Details (hashtags / keywords)", detail_options, key="sel_details")

        # Classify selected details
        s1_hashtags: List[str] = []
        s1_keywords: List[str] = []
        for d in sel_details:
            entry = next((e for e in sub1 if e["details"] == d), None)
            if not entry:
                continue
            tags = extract_tags(d)
            if "keyword" in entry["type"].lower():
                s1_keywords.extend(tags)
            else:
                s1_hashtags.extend(tags)

        if s1_hashtags:
            st.caption(f"🏷️ Hashtags: {' '.join(['#'+h for h in s1_hashtags])}")
        if s1_keywords:
            st.caption(f"🔑 Keywords: {' '.join(s1_keywords)}")

    # ── Sheet 2: Brands ──────────────────────────────────────────────────
    with right:
        st.markdown('<div class="sec-header">🏢 Sheet 2 — Brand Hashtags</div>', unsafe_allow_html=True)

        brand_names = sorted(set(e["brand"] for e in sheet2))
        sel_brands  = st.multiselect("Select Brand(s)", brand_names, key="sel_brands")

        s2_tags: List[str] = []
        for brand in sel_brands:
            entry = next((e for e in sheet2 if e["brand"] == brand), None)
            if not entry:
                continue
            htags = extract_tags(entry.get("hashtags", ""))
            ktags = extract_tags(entry.get("keywords", ""))
            all_btags = htags + ktags
            s2_tags.extend(all_btags)
            if all_btags:
                st.markdown(f"**{brand}:** {' '.join(['`#'+t+'`' for t in all_btags])}")

    # Combined
    all_hashtags_query = list(dict.fromkeys(s1_hashtags + s2_tags))   # dedup, preserve order
    all_keywords_query = list(dict.fromkeys(s1_keywords))

    st.divider()
    if all_hashtags_query or all_keywords_query:
        st.info(
            f"**Combined search →** "
            f"Hashtags: `{', '.join(['#'+h for h in all_hashtags_query]) or '(none)'}` | "
            f"Keywords: `{', '.join(all_keywords_query) or '(none)'}`"
        )
    else:
        st.info("ℹ️ Select hashtags/keywords from Sheet 1 and/or brands from Sheet 2.")

    # ══════════════════════════════════════════════════════════════════════
    # STEP 2 — Scrape config
    # ══════════════════════════════════════════════════════════════════════
    st.header("2️⃣  Scrape Configuration")
    sc1, sc2, sc3 = st.columns(3)
    max_results = sc1.slider("Max videos", 5, 100, 20)
    days_filter = sc2.selectbox(
        "Time window",
        [None, 7, 14, 30, 60, 90],
        format_func=lambda x: "No limit" if x is None else f"Last {x} days",
    )
    _ = sc3

    can_scrape = bool(all_hashtags_query or all_keywords_query)
    scrape_btn = st.button("🚀 Fetch TikTok Videos", type="primary", disabled=not can_scrape)
    if not can_scrape:
        st.caption("Select at least one hashtag or keyword to enable scraping.")

    if scrape_btn:
        results = fetch_from_apify(apify_key, all_hashtags_query, all_keywords_query, max_results, days_filter)
        if results is not None:
            for item in results:
                confirmed, reason = check_confirmation(item, s1_hashtags, s1_keywords, s2_tags)
                item["_confirmed"]              = confirmed
                item["_not_confirmed_reason"]   = "" if confirmed else reason

            st.session_state.scraped_data = results
            confirmed_n = sum(1 for r in results if r.get("_confirmed"))
            st.success(f"✅ Fetched **{len(results)}** videos — **{confirmed_n}** confirmed, **{len(results)-confirmed_n}** not confirmed.")

    # ══════════════════════════════════════════════════════════════════════
    # STEP 3 — Results
    # ══════════════════════════════════════════════════════════════════════
    if not st.session_state.scraped_data:
        return

    st.header("3️⃣  Scraped Videos")

    raw_data = st.session_state.scraped_data
    show_confirmed_only = st.checkbox("Show confirmed videos only", value=False, key="conf_only")
    display_data = [d for d in raw_data if d.get("_confirmed")] if show_confirmed_only else raw_data

    # Summary metrics
    mc = st.columns(5)
    mc[0].markdown(f'<div class="metric-card"><div class="metric-val">{len(display_data)}</div><div class="metric-lbl">Videos</div></div>', unsafe_allow_html=True)
    mc[1].markdown(f'<div class="metric-card"><div class="metric-val">{sum(1 for d in display_data if d.get("_confirmed"))}</div><div class="metric-lbl">Confirmed</div></div>', unsafe_allow_html=True)
    mc[2].markdown(f'<div class="metric-card"><div class="metric-val">{fmt_num(sum(d.get("playCount",0) for d in display_data))}</div><div class="metric-lbl">Total Plays</div></div>', unsafe_allow_html=True)
    mc[3].markdown(f'<div class="metric-card"><div class="metric-val">{fmt_num(sum(d.get("diggCount",0) for d in display_data))}</div><div class="metric-lbl">Total Likes</div></div>', unsafe_allow_html=True)
    mc[4].markdown(f'<div class="metric-card"><div class="metric-val">{fmt_num(sum(d.get("shareCount",0) for d in display_data))}</div><div class="metric-lbl">Total Shares</div></div>', unsafe_allow_html=True)

    st.markdown("")

    # Flat selection table
    rows = []
    for item in display_data:
        auth  = item.get("authorMeta", {}) or {}
        vmeta = item.get("videoMeta", {}) or {}
        rows.append({
            "Select":                False,
            "Confirmed":             "✅ Yes" if item.get("_confirmed") else "❌ No",
            "Not Confirmed Reason":  item.get("_not_confirmed_reason", ""),
            "Video URL":             item.get("webVideoUrl", ""),
            "Author":                auth.get("nickName") or auth.get("name", ""),
            "Followers":             fmt_num(auth.get("fans", 0)),
            "Caption":               (item.get("text","") or "")[:120],
            "Plays":                 item.get("playCount", 0),
            "Likes":                 item.get("diggCount", 0),
            "Comments":              item.get("commentCount", 0),
            "Shares":                item.get("shareCount", 0),
            "Saves":                 item.get("collectCount", 0),
            "Duration (s)":          (vmeta.get("duration") or 0),
            "Is Ad":                 item.get("isAd", False),
            "Created":               item.get("createTimeISO", ""),
            "Location":              item.get("locationCreated", ""),
        })

    df_table = pd.DataFrame(rows)
    edited   = st.data_editor(
        df_table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Select":               st.column_config.CheckboxColumn("Select for Analysis", default=False),
            "Video URL":            st.column_config.LinkColumn("Video URL"),
            "Confirmed":            st.column_config.TextColumn("Confirmed"),
            "Not Confirmed Reason": st.column_config.TextColumn("Reason (if not confirmed)", width="large"),
        },
        disabled=[c for c in df_table.columns if c != "Select"],
        key="video_table",
    )

    selected_indices = edited[edited["Select"] == True].index.tolist()

    # Card view
    with st.expander("🃏 Card View (all visible videos)", expanded=False):
        for idx, item in enumerate(display_data):
            render_video_card(item, idx)
            st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # STEP 4 — Analysis
    # ══════════════════════════════════════════════════════════════════════
    st.header("4️⃣  AI Analysis ")

    if not selected_indices:
        st.info("ℹ️ Tick the **Select** checkbox in the table above to choose videos for analysis.")
    else:
        st.markdown(f"**{len(selected_indices)} video(s)** selected.")
        analyse_btn = st.button("🧠 Analyse Selected Videos", type="primary")

        if analyse_btn:
            for tbl_idx in selected_indices:
                # Map table row index back to original data
                item = display_data[tbl_idx]
                url  = item.get("webVideoUrl", item.get("submittedVideoUrl", f"video_{tbl_idx}"))

                with st.status(f"🔍 Analysing: {url}", expanded=True) as status:
                    res = analyse_video_openai(item, openai_key)
                    if res["success"]:
                        st.session_state.analysis_results[url] = res
                        status.update(label=f"✅ Done: {url}", state="complete")
                    else:
                        st.error(f"❌ {res.get('error')}")
                        status.update(label=f"❌ Failed: {url}", state="error")

    # Cached results
    if st.session_state.analysis_results:
        st.subheader("📊 Analysis Results")
        for url, res in st.session_state.analysis_results.items():
            with st.expander(f"🎬 {url}", expanded=True):
                if res.get("success"):
                    render_analysis_result(res)
                else:
                    st.error(f"Analysis failed: {res.get('error')}")

        # CSV export
        export_rows = []
        for url, res in st.session_state.analysis_results.items():
            if res.get("success"):
                r = res["result"]
                for dp in r.get("darkPatternAnalysis", []):
                    export_rows.append({
                        "video_url":           url,
                        "category":            dp.get("category"),
                        "confidence":          dp.get("confidenceScore"),
                        "excerpt":             dp.get("excerpt"),
                        "section_type":        dp.get("sectionType"),
                        "reasoning":           dp.get("reasoning"),
                        "overall_confidence":  r.get("overallConfidenceScore"),
                        "products":            ", ".join(r.get("productNames", [])),
                        "regulations":         " | ".join(
                            f"{ref.get('lawGuidance')} {ref.get('articleClause')}"
                            for ref in dp.get("regulatoryViolationReference", [])
                        ),
                    })

        if export_rows:
            df_exp = pd.DataFrame(export_rows)
            st.download_button(
                "📥 Download Analysis CSV",
                df_exp.to_csv(index=False).encode("utf-8"),
                file_name=f"dark_pattern_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()
