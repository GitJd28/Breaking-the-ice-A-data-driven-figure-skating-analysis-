import streamlit as st

st.set_page_config(
    page_title = "Breaking the Ice | Figure Skating Analytics",
    page_icon  = "⛸️",
    layout     = "wide",
    initial_sidebar_state = "expanded"
)

# ── Header ───────────────────────────────────
st.title("⛸️ Breaking the Ice")
st.subheader(
    "A Data-Driven Analysis of Olympic Figure Skating — "
    "What Separates Champions from the Rest"
)
st.markdown("---")

# ── Introduction ─────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### The Question
    
    Across **20 years** of Olympic figure skating data,  
    one pattern is clear — a small group of nations  
    consistently dominate the podium while the rest  
    of the world watches.
    
    **What exactly separates medal winners from everyone else?**  
    And what would it take for an emerging nation  
    to break through?
    
    This dashboard uses **357 athlete records** across  
    6 Olympic Games, combined with World Championship  
    data spanning 19 years, to answer that question  
    with data — not assumptions.
    """)

with col2:
    st.markdown("### By The Numbers")
    st.metric("Olympic Games Covered",  "6",    "2006 → 2026")
    st.metric("Athletes Analyzed",      "357",  "75 Nations")
    st.metric("Model Accuracy (AUC)",   "0.983","Random Forest")

st.markdown("---")

# ── Key Findings Preview ──────────────────────
st.markdown("### 🔍 Key Findings")

f1, f2, f3 = st.columns(3)

with f1:
    st.info("""
    **🏅 The 90-Point Wall**
    
    Medal winners score an average of
    **90+ points more** than non-medalists.
    A structural gap — not random variation.
    """)

with f2:
    st.info("""
    **📋 Short Program is Everything**
    
    Short Program rank alone explains
    **53% of medal prediction** — the single
    most important factor in our model.
    """)

with f3:
    st.info("""
    **🔄 The Quad Revolution**
    
    Post-2014, quad jumps correlate with
    scores at **r = 0.700**. Technical
    content now drives results above artistry.
    """)

st.markdown("---")

# ── Navigation Guide ─────────────────────────
st.markdown("### 📖 How to Navigate")

nav1, nav2, nav3 = st.columns(3)

with nav1:
    st.markdown("""
    **Explore the Data**
    - 🌍 Nation Analysis
    - 🧬 Performance DNA
    - 🔄 Quad Revolution
    """)

with nav2:
    st.markdown("""
    **Use the Model**
    - 🤖 Medal Predictor
    - Enter any skater's scores
    - Get medal probability live
    """)

with nav3:
    st.markdown("""
    **See the Roadmap**
    - 🇮🇳 India's Path Forward
    - Score benchmarks
    - Data-backed recommendations
    """)

st.markdown("---")
st.caption(
    "Data sources: ISU Olympic Figure Skating Results (2006–2026) "
    "| World Championship Scores (2005–2024) "
    "| Built with Streamlit + scikit-learn"
)