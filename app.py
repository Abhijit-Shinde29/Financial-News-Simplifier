"""
Financial News Simplifier - Streamlit Application
A modern, AI-powered educational web dashboard for translating complex financial news into simple language.
"""

import os
import sys
from pathlib import Path

# Ensure application directory is in sys.path
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import (
    APP_TITLE,
    APP_TAGLINE,
    APP_SUBTITLE,
    OPENAI_MODEL,
    is_api_key_configured,
)
from database import (
    init_db,
    get_all_analyses,
    get_analysis_by_id,
    delete_analysis,
    get_analytics_summary,
)
from analyzer import (
    process_article,
    run_demo_analysis,
    get_demo_article_names,
    get_demo_article,
)
from modules.financial_terms import FINANCIAL_GLOSSARY, search_glossary
from modules.summarizer import format_summary_card, calculate_readability_stats
from modules.impact_analyzer import get_impact_disclaimer
from modules.entity_extractor import get_entity_badges
from utils.helpers import (
    format_date,
    get_sentiment_badge_html,
    generate_text_report,
    generate_json_report,
)

# Page configuration
st.set_page_config(
    page_title=f"{APP_TITLE} | AI Educational Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database on app startup
init_db()

# Custom Modern CSS styling
CUSTOM_CSS = """
<style>
    /* Global font and subtle styling */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Header Branding */
    .app-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F766E 100%);
        color: white;
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    }
    .app-header h1 {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        color: #F8FAFC !important;
    }
    .app-header p {
        font-size: 1.05rem;
        color: #CBD5E1;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06);
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 4px;
    }

    /* Educational Disclaimer Banner */
    .disclaimer-banner {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        color: #92400E;
        padding: 12px 18px;
        border-radius: 6px;
        font-size: 0.88rem;
        margin-bottom: 20px;
    }

    /* Term Chip / Entity Pill */
    .entity-tag {
        display: inline-block;
        background-color: #F1F5F9;
        color: #334155;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 4px 10px;
        margin: 3px 4px 3px 0;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Card Containers */
    .section-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    /* Sidebar branding */
    .sidebar-title {
        font-weight: 800;
        font-size: 1.2rem;
        color: #0F172A;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Sidebar Navigation & Status
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding-bottom: 12px; border-bottom: 1px solid #E2E8F0; margin-bottom: 14px;">
            <div class="sidebar-title">
                <span>📊</span> <span>{APP_TITLE}</span>
            </div>
            <p style="font-size: 0.82rem; color: #64748B; margin-top: 4px;">{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📰 Analyze News",
            "📚 News History",
            "📖 Financial Glossary",
            "ℹ️ About Project",
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # API Status indicator in sidebar
    api_configured = is_api_key_configured()
    if api_configured:
        st.success(f"🟢 **OpenAI Active**\nModel: `{OPENAI_MODEL}`")
    else:
        st.warning("🟡 **Demo Mode Available**\nOpenAI key not configured in `.env`.")

    st.markdown("---")
    st.caption("Capstone Project | NASSCOM Quality Standards")
    st.caption("⚠️ **Educational Tool**: Not financial advice or investment recommendations.")


# Helper function to display an analysis view
def render_analysis_view(analysis: dict, source_url: str = None, article_text: str = ""):
    """Renders the complete structured analysis view according to requirements."""
    headline = analysis.get("headline", "Financial News Analysis")
    sector = analysis.get("sector", "General Economy")
    sentiment = analysis.get("sentiment", "Neutral")
    confidence = analysis.get("confidence", 85)
    simple_exp = analysis.get("simple_explanation", "")
    short_summary = analysis.get("short_summary", "")
    key_points = analysis.get("key_points", [])
    financial_terms = analysis.get("financial_terms", [])
    entities = analysis.get("entities", {})
    uncertainties = analysis.get("uncertainties", [])

    # Top Headline Bar
    st.markdown(f"### {headline}")

    # Meta badges: Sector, Sentiment, Confidence
    col_meta1, col_meta2, col_meta3, col_meta4 = st.columns([2, 2, 2, 3])
    with col_meta1:
        st.markdown(f"**Sector:** `{sector}`")
    with col_meta2:
        st.markdown(f"**Sentiment:** {get_sentiment_badge_html(sentiment)}", unsafe_allow_html=True)
    with col_meta3:
        st.markdown(f"**Confidence:** `{confidence}%`")
    with col_meta4:
        if source_url:
            st.markdown(f"**Source:** [{source_url[:35]}...]({source_url})" if len(source_url) > 35 else f"**Source:** [{source_url}]({source_url})")
        else:
            st.markdown("**Source:** Pasted News Text")

    st.markdown("---")

    # 1. Prominent "📌 In Simple Words" Card
    st.markdown(format_summary_card(simple_exp), unsafe_allow_html=True)

    # Readability & Time Saved Metrics
    if article_text:
        stats = calculate_readability_stats(article_text, simple_exp)
        rcol1, rcol2, rcol3 = st.columns(3)
        with rcol1:
            st.metric("Source Word Count", f"{stats['original_word_count']} words")
        with rcol2:
            st.metric("Simplified Word Count", f"{stats['simplified_word_count']} words")
        with rcol3:
            st.metric("Reading Time Saved", f"{stats['reading_time_saved_pct']}% faster")

    # Executive Summary (Expander / subtext)
    if short_summary:
        with st.expander("📄 Executive Summary (2-3 Sentences)", expanded=False):
            st.write(short_summary)

    # 2. Key Takeaways Section
    st.markdown("#### 🎯 Key Takeaways")
    if key_points:
        for idx, pt in enumerate(key_points, 1):
            st.markdown(f"**{idx}.** {pt}")
    else:
        st.info("No key points generated.")

    st.markdown("---")

    # 3. Financial Terminology & Glossary Lookup
    st.markdown("#### 💡 Financial Terminology Explained")
    st.caption("Difficult financial terms identified and explained in plain English:")

    if financial_terms:
        term_cols = st.columns(2)
        for i, item in enumerate(financial_terms):
            with term_cols[i % 2]:
                term_name = item.get("term", "")
                def_text = item.get("simple_definition", "")
                ctx_text = item.get("context_in_article", "")
                with st.container(border=True):
                    st.markdown(f"**🔍 {term_name}**")
                    st.markdown(f"**Simple Meaning:** {def_text}")
                    if ctx_text:
                        st.caption(f"**Context in article:** {ctx_text}")
    else:
        st.info("No specialized terminology required definition in this article.")

    st.markdown("---")

    # 4. Categorized Entity Extraction
    st.markdown("#### 🏢 Categorized Entities")
    st.caption("Organizations, leaders, and metrics identified from the news article:")

    badge_data = get_entity_badges(entities)
    if badge_data:
        entity_cols = st.columns(min(len(badge_data), 3) or 1)
        for idx, (cat_key, meta) in enumerate(badge_data.items()):
            col_target = entity_cols[idx % len(entity_cols)]
            with col_target:
                with st.container(border=True):
                    st.markdown(f"**{meta['icon']} {meta['label']}**")
                    for item in meta["items"]:
                        st.markdown(f'<span class="entity-tag">{item}</span>', unsafe_allow_html=True)
    else:
        st.info("No distinct entities were categorized.")

    st.markdown("---")

    # 5. Possible Impact Section
    st.markdown("#### 📊 Possible Impact")
    st.markdown(
        f'<div class="disclaimer-banner">{get_impact_disclaimer()}</div>',
        unsafe_allow_html=True
    )

    tab_biz, tab_con, tab_econ, tab_mkt = st.tabs([
        "🏢 Business Impact",
        "🛒 Consumer Impact",
        "🌐 Economic Impact",
        "📈 Market Relevance",
    ])

    with tab_biz:
        st.write(analysis.get("possible_business_impact", "No specific business impact noted."))
    with tab_con:
        st.write(analysis.get("possible_consumer_impact", "Direct consumer effects may be indirect."))
    with tab_econ:
        st.write(analysis.get("possible_economic_impact", "Contributes to broader sectoral developments."))
    with tab_mkt:
        st.write(analysis.get("possible_market_relevance", "Market participants may factor this into sector views."))

    st.markdown("---")

    # 6. Uncertainties & Source Quality Notes
    if uncertainties:
        with st.expander("❓ Uncertainties & Unresolved Questions", expanded=False):
            st.caption("Factors not yet confirmed or dependent on future developments:")
            for u in uncertainties:
                st.markdown(f"- {u}")

    # 7. Sentiment & Confidence Warning
    st.caption(
        "ℹ️ **Tone & Confidence Notice:** Sentiment reflects the tone of the article and is NOT a prediction "
        "of future stock or market performance."
    )

    # 8. Report Export / Download Actions
    st.markdown("---")
    st.markdown("#### 📥 Export Analysis Report")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        txt_content = generate_text_report(analysis, source_url)
        st.download_button(
            label="📄 Download Plaintext Report (.txt)",
            data=txt_content,
            file_name=f"financial_simplifier_{sentiment.lower()}_{sector.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with exp_col2:
        json_content = generate_json_report(analysis, source_url)
        st.download_button(
            label="📊 Download JSON Data (.json)",
            data=json_content,
            file_name=f"financial_simplifier_{sentiment.lower()}_{sector.lower().replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )


# ==============================================================================
# PAGE 1: DASHBOARD
# ==============================================================================
if page == "🏠 Dashboard":
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{APP_TITLE}</h1>
            <p>{APP_SUBTITLE}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    stats = get_analytics_summary()
    total_analyses = stats["total_count"]
    today_count = stats["today_count"]
    sentiment_counts = stats["sentiment_counts"]
    sector_counts = stats["sector_counts"]
    top_terms = stats["top_terms"]
    daily_activity = stats["daily_activity"]

    # Top Summary Metrics
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("Total Articles Analyzed", f"{total_analyses}")
    with mcol2:
        st.metric("Analyzed Today", f"{today_count}")
    with mcol3:
        st.metric("Financial Terms Cataloged", f"{len(FINANCIAL_GLOSSARY)}")
    with mcol4:
        st.metric("System Mode", "Online (API)" if is_api_key_configured() else "Demo Mode Ready")

    st.markdown("---")

    if total_analyses == 0:
        # Friendly empty state
        st.info("👋 **Welcome to Financial News Simplifier!**")
        st.markdown(
            """
            No articles have been analyzed yet. You can paste a financial news story, enter an article URL,
            or click below to run an instant demonstration with preloaded realistic news!
            """
        )
        if st.button("🚀 Run Quick Demo Analysis Now", type="primary"):
            with st.spinner("Processing demo financial article..."):
                run_demo_analysis("rbi_monetary_policy")
            st.success("Demo analysis successfully generated and saved! Refreshing dashboard...")
            st.rerun()
    else:
        # Visual Analytics Charts
        st.markdown("### 📊 Analytics Overview")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("##### Sentiment Distribution")
            if sentiment_counts:
                df_sent = pd.DataFrame(list(sentiment_counts.items()), columns=["Sentiment", "Count"])
                color_map = {
                    "Positive": "#10B981",
                    "Negative": "#EF4444",
                    "Neutral": "#3B82F6",
                    "Mixed": "#F59E0B",
                    "Uncertain": "#8B5CF6",
                }
                fig_sent = px.pie(
                    df_sent,
                    values="Count",
                    names="Sentiment",
                    hole=0.45,
                    color="Sentiment",
                    color_discrete_map=color_map,
                )
                fig_sent.update_traces(textinfo="percent+label", hoverinfo="label+value")
                fig_sent.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=280)
                st.plotly_chart(fig_sent, use_container_width=True)
            else:
                st.caption("No sentiment data available.")

        with chart_col2:
            st.markdown("##### Articles by Sector")
            if sector_counts:
                df_sec = pd.DataFrame(list(sector_counts.items()), columns=["Sector", "Count"])
                fig_sec = px.bar(
                    df_sec,
                    x="Count",
                    y="Sector",
                    orientation="h",
                    color="Sector",
                    color_discrete_sequence=px.colors.qualitative.Safe,
                )
                fig_sec.update_layout(
                    showlegend=False,
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=280,
                    xaxis_title="Number of Articles",
                    yaxis_title="",
                )
                st.plotly_chart(fig_sec, use_container_width=True)
            else:
                st.caption("No sector data available.")

        # Second row of charts: Top Terms and Activity Timeline
        chart_col3, chart_col4 = st.columns(2)
        with chart_col3:
            st.markdown("##### Most Common Financial Terms Identified")
            if top_terms:
                df_terms = pd.DataFrame(top_terms, columns=["Term", "Frequency"]).head(7)
                fig_terms = px.bar(
                    df_terms,
                    x="Frequency",
                    y="Term",
                    orientation="h",
                    color="Frequency",
                    color_continuous_scale="Teal",
                )
                fig_terms.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False,
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=280,
                    yaxis={'categoryorder':'total ascending'},
                    xaxis_title="Mentions",
                    yaxis_title=""
                )
                st.plotly_chart(fig_terms, use_container_width=True)
            else:
                st.caption("No financial terms cataloged yet.")

        with chart_col4:
            st.markdown("##### Analysis Activity Over Time")
            if daily_activity:
                df_timeline = pd.DataFrame(list(daily_activity.items()), columns=["Date", "Analyses"]).sort_values("Date")
                fig_time = px.area(
                    df_timeline,
                    x="Date",
                    y="Analyses",
                    markers=True,
                    color_discrete_sequence=["#0D9488"]
                )
                fig_time.update_layout(
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=280,
                    xaxis_title="",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.caption("Activity timeline will appear as analyses are logged.")

        st.markdown("---")

        # Recent Analyses List
        st.markdown("### 🕒 Recent Analyses")
        recent_records = get_all_analyses(sort_order="newest")[:5]
        for item in recent_records:
            d = item.to_dict()
            with st.container(border=True):
                r_col1, r_col2, r_col3 = st.columns([6, 2, 2])
                with r_col1:
                    st.markdown(f"**{d['headline']}**")
                    st.caption(f"{d['short_summary'][:150]}...")
                with r_col2:
                    st.markdown(f"{get_sentiment_badge_html(d['sentiment'])}", unsafe_allow_html=True)
                    st.caption(f"Sector: `{d['sector']}`")
                with r_col3:
                    st.caption(f"Saved: {format_date(d['created_at'])}")
                    if st.button("Open Analysis", key=f"dash_open_{d['id']}"):
                        st.session_state["view_analysis_id"] = d["id"]
                        st.session_state["active_nav"] = "News History"
                        st.info(f"Navigate to 'News History' tab to view article #{d['id']}.")


# ==============================================================================
# PAGE 2: ANALYZE NEWS
# ==============================================================================
elif page == "📰 Analyze News":
    st.markdown("## 📰 Analyze Financial News")
    st.caption("Convert complex financial reports and news stories into plain, digestible insights.")

    # Educational Disclaimer Header
    st.markdown(
        """
        <div class="disclaimer-banner">
            <strong>⚠️ Educational Policy:</strong> Financial News Simplifier is strictly an educational tool. 
            It does not provide investment advice, buy/sell stock recommendations, or guaranteed market predictions.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check for missing API key notice
    if not is_api_key_configured():
        st.warning(
            "ℹ️ **OpenAI API Key is not configured.** You can still experience all features using "
            "the **'Run Demo Analysis'** button below, or add `OPENAI_API_KEY` to your `.env` file."
        )

    # Input Mode Tabs
    input_mode = st.radio(
        "Choose Input Method:",
        ["📝 Paste Article Text", "🔗 Article URL"],
        horizontal=True
    )

    # Demo Selector & Example Loader
    demo_titles = get_demo_article_names()
    sample_col1, sample_col2 = st.columns([3, 1])

    with sample_col1:
        selected_demo_key = st.selectbox(
            "Select an Example Topic / Demo News:",
            options=list(demo_titles.keys()),
            format_func=lambda k: demo_titles[k]
        )

    article_text_input = ""
    url_input = ""

    # Session state for inputs
    if "input_text_val" not in st.session_state:
        st.session_state["input_text_val"] = ""
    if "input_url_val" not in st.session_state:
        st.session_state["input_url_val"] = ""

    with sample_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("📋 Load Example News", use_container_width=True):
            chosen = get_demo_article(selected_demo_key)
            if chosen:
                st.session_state["input_text_val"] = chosen["text"]
                st.success("Example article loaded into text area!")

    if input_mode == "📝 Paste Article Text":
        article_text_input = st.text_area(
            "Paste Financial News / Article Text:",
            value=st.session_state["input_text_val"],
            height=240,
            placeholder="Paste raw financial news text here (e.g., central bank rate decisions, earnings releases, macroeconomic data)..."
        )
    else:
        url_input = st.text_input(
            "Enter Financial News / Article URL:",
            value=st.session_state["input_url_val"],
            placeholder="https://example.com/financial-news/article-headline"
        )
        st.caption("Note: Web scrapers respect site policies. If a site uses paywalls or JavaScript rendering, please paste text directly.")

    # Action Buttons
    b_col1, b_col2, b_col3, b_col4 = st.columns([2, 1, 2, 2])

    with b_col1:
        analyze_clicked = st.button("🚀 Analyze News", type="primary", use_container_width=True)

    with b_col2:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state["input_text_val"] = ""
            st.session_state["input_url_val"] = ""
            st.session_state["current_analysis"] = None
            st.rerun()

    with b_col3:
        demo_clicked = st.button("⚡ Run Demo Analysis", use_container_width=True)

    # Handle Analysis Execution
    if analyze_clicked:
        target_text = article_text_input.strip() if input_mode == "📝 Paste Article Text" else ""
        target_url = url_input.strip() if input_mode == "🔗 Article URL" else None

        if not target_text and not target_url:
            st.error("Please provide article text or enter a URL before clicking Analyze.")
        else:
            with st.spinner("Analyzing financial news with AI... Simplifying terminology and extracting insights..."):
                res = process_article(
                    input_text=target_text,
                    source_url=target_url,
                    force_demo=False
                )

                if res["success"]:
                    st.session_state["current_analysis"] = res
                    st.success("Analysis complete! See simplified breakdown below.")
                else:
                    st.error(f"Analysis Error: {res['error']}")

    if demo_clicked:
        with st.spinner("Executing Demo Mode analysis with preloaded financial dataset..."):
            res = process_article(
                input_text="",
                source_url=None,
                force_demo=True,
                demo_key=selected_demo_key
            )
            st.session_state["current_analysis"] = res
            st.info("✅ Displaying results in **Demo Mode** (Pre-computed verified dataset).")

    # Display Active Analysis
    active_analysis = st.session_state.get("current_analysis")
    if active_analysis and active_analysis.get("success"):
        st.markdown("---")
        render_analysis_view(
            analysis=active_analysis["data"],
            source_url=active_analysis.get("source_url"),
            article_text=active_analysis.get("article_text", "")
        )


# ==============================================================================
# PAGE 3: NEWS HISTORY
# ==============================================================================
elif page == "📚 News History":
    st.markdown("## 📚 Analysis History")
    st.caption("Search, filter, view, and export previously simplified articles.")

    # Search and Filters
    f_col1, f_col2, f_col3, f_col4 = st.columns([3, 2, 2, 2])

    with f_col1:
        search_query = st.text_input("🔍 Search History:", placeholder="Search by headline, summary, term...")

    with f_col2:
        sentiment_filter = st.selectbox(
            "Filter by Sentiment:",
            ["All", "Positive", "Negative", "Neutral", "Mixed", "Uncertain"]
        )

    with f_col3:
        all_records_for_sectors = get_all_analyses()
        sectors_found = sorted(list({r.sector for r in all_records_for_sectors if r.sector}))
        sector_filter = st.selectbox(
            "Filter by Sector:",
            ["All"] + sectors_found
        )

    with f_col4:
        sort_order = st.selectbox(
            "Sort Order:",
            ["Newest First", "Oldest First"]
        )
        sort_param = "newest" if sort_order == "Newest First" else "oldest"

    records = get_all_analyses(
        search_query=search_query,
        sentiment_filter=sentiment_filter,
        sector_filter=sector_filter,
        sort_order=sort_param
    )

    st.markdown(f"**Found {len(records)} saved analyses:**")
    st.markdown("---")

    if not records:
        st.info("No saved analyses found matching the selected criteria.")
    else:
        for item in records:
            d = item.to_dict()
            with st.container(border=True):
                h_col1, h_col2, h_col3 = st.columns([6, 2, 2])

                with h_col1:
                    st.markdown(f"#### {d['headline']}")
                    st.markdown(f"**Summary:** {d['short_summary']}")

                with h_col2:
                    st.markdown(get_sentiment_badge_html(d["sentiment"]), unsafe_allow_html=True)
                    st.caption(f"Sector: `{d['sector']}`")
                    st.caption(f"Confidence: `{d['confidence']}%`")

                with h_col3:
                    st.caption(f"📅 {format_date(d['created_at'])}")
                    if d.get("source_url"):
                        st.caption(f"🔗 [Source Link]({d['source_url']})")

                # Action buttons inside item card
                act_col1, act_col2, act_col3 = st.columns([2, 2, 6])
                with act_col1:
                    show_details = st.checkbox("View Full Breakdown", key=f"view_{d['id']}")

                with act_col2:
                    if st.button("🗑️ Delete", key=f"del_{d['id']}", help="Permanently delete this analysis"):
                        delete_analysis(d["id"])
                        st.success(f"Analysis #{d['id']} deleted.")
                        st.rerun()

                # Expandable details view
                if show_details:
                    st.markdown("---")
                    render_analysis_view(
                        analysis=d,
                        source_url=d.get("source_url"),
                        article_text=d.get("article_text", "")
                    )


# ==============================================================================
# PAGE 4: FINANCIAL GLOSSARY
# ==============================================================================
elif page == "📖 Financial Glossary":
    st.markdown("## 📖 Financial Glossary & Terminology Guide")
    st.caption("A beginner-friendly dictionary explaining essential financial concepts with plain-language analogies.")

    # Search and Category filter
    g_col1, g_col2 = st.columns([3, 2])
    with g_col1:
        glossary_search = st.text_input("🔍 Search Glossary:", placeholder="Search term (e.g. Repo Rate, EBITDA, Inflation)...")
    with g_col2:
        categories = ["All", "Macroeconomics", "Monetary Policy", "Stock Markets", "Corporate Finance", "Fixed Income", "Risk & Trading", "Financial System"]
        selected_category = st.selectbox("Category Filter:", categories)

    glossary_items = search_glossary(glossary_search, selected_category)

    st.markdown(f"**Showing {len(glossary_items)} terms:**")
    st.markdown("---")

    # Render terms in a 2-column grid
    g_grid_cols = st.columns(2)
    for idx, item in enumerate(glossary_items):
        with g_grid_cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"### 💡 {item['term']}")
                st.caption(f"Category: `{item.get('category', 'General')}`")

                st.markdown(f"**📌 In Simple Words:** {item['simple_explanation']}")

                with st.expander("Formal Definition & Example"):
                    st.markdown(f"**Formal Definition:** {item['definition']}")
                    st.markdown(f"**Real-World Example:** *{item['example']}*")


# ==============================================================================
# PAGE 5: ABOUT PROJECT
# ==============================================================================
elif page == "ℹ️ About Project":
    st.markdown("## ℹ️ About Financial News Simplifier")
    st.caption("NASSCOM Capstone Quality AI Educational Tool")

    st.markdown(
        """
        ### 1. Project Overview & Motivation
        Financial news often contains specialized jargon, macroeconomic acronyms, and complex corporate disclosures 
        that intimidate students, beginners, retail investors, and general citizens. 

        **Financial News Simplifier** bridges this literacy gap by using modern Generative AI to translate dense financial 
        articles into plain, conversational language while preserving numerical precision and factual integrity.

        ### 2. Core Capabilities
        - **Plain Language Translation**: Converts central bank policy statements and earnings releases into beginner-friendly explanations.
        - **Term Detection & Glossary**: Detects difficult financial terminology and attaches plain-English definitions and context.
        - **Entity Categorization**: Systematically groups companies, commercial banks, regulatory bodies, and indicators.
        - **Structured Key Points**: Outlines what happened, who is involved, important numbers, and what remains uncertain.
        - **Neutral Impact Framing**: Explains possible business, consumer, and macroeconomic relevance using cautious, non-advisory phrasing.
        - **Historical Tracking & Analytics**: Persists analyses in SQLite with interactive Plotly visualizations.
        - **Multi-Format Export**: Generates printable plaintext reports (.txt) and JSON data payloads (.json).
        - **Fail-Safe Demo Mode**: Fully runnable offline without requiring an OpenAI API key.

        ### 3. Architecture & Technology Stack
        - **Frontend & Dashboard**: Streamlit with custom CSS and Plotly data visualizations.
        - **AI Core**: OpenAI Python SDK (`gpt-4o-mini` configurable via environment variables).
        - **Data Ingestion**: `requests` and `BeautifulSoup4` with automated cleaning and safety limits.
        - **Database**: SQLite3 managed via SQLAlchemy ORM.
        - **Validation**: Pydantic schema validation.

        ### 4. Ethical Safeguards & Non-Advisory Guarantee
        1. **Zero Financial Advice**: The system never provides personalized stock picks, buy/sell recommendations, or price targets.
        2. **No Hallucinations**: Constrained to rely strictly on verifiable facts present in the source text.
        3. **Tone vs Prediction**: Clear notices clarify that sentiment analysis reflects article tone, not market direction.
        4. **Probabilistic Language**: Replaces certainty claims with cautious phrasing (*"may affect"*, *"could influence"*, *"the article suggests"*).

        ### 5. Educational Disclaimer
        *Financial News Simplifier is an educational tool designed for literacy and understanding. It does not provide 
        financial, investment, legal, or tax advice. Users should consult licensed financial advisors for investment decisions.*
        """
    )
