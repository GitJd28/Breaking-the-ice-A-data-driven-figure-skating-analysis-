import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components.styles import load_css

st.set_page_config(
    page_title="Break the Ice | Figure Skating Analytics",
    page_icon="⛸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(load_css(), unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
        <div class='icon'>⛸️</div>
        <div class='name'>Break the Ice</div>
        <div class='tag'>Figure Skating Analytics</div>
    </div>
    """, unsafe_allow_html=True)

# Page header
st.markdown("""
<div class='page-title'>Welcome to Break the Ice</div>
<div class='page-subtitle'>
    A data-driven analysis of Olympic Figure Skating —
    uncovering what separates champions from the field.
</div>
""", unsafe_allow_html=True)

# Top stat cards (blue gradient row)
c1, c2, c3, c4 = st.columns(4)

cards = [
    ("6",     "Olympic Games",   "2006 → 2026"),
    ("75",    "Nations",         "Represented"),
    ("357",   "Athletes",        "Analyzed"),
    ("0.983", "Model AUC",       "Random Forest"),
]

for col, (num, lbl, sub) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(f"""
        <div class='stat-card-blue'>
            <div class='num'>{num}</div>
            <div class='lbl'>{lbl}</div>
            <div class='sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Key Findings
st.markdown(
    "<div class='section-title'>🔍 Key Findings</div>",
    unsafe_allow_html=True
)

f1, f2, f3 = st.columns(3)

findings = [
    ("🏅 The 90-Point Wall",
     "Medal winners score an average of "
     "<b style='color:#3D7EFF;'>90+ points more</b> "
     "than non-medalists. A structural gap — not "
     "random variation."),
    ("📋 Short Program is Everything",
     "Short Program rank alone explains "
     "<b style='color:#3D7EFF;'>53.8%</b> of medal "
     "prediction — the single most important factor "
     "in our model."),
    ("🔄 The Quad Revolution",
     "Post-2014, quad jumps correlate with scores at "
     "<b style='color:#3D7EFF;'>r = 0.700</b>. "
     "Technical content now drives results above artistry."),
]

for col, (title, text) in zip([f1, f2, f3], findings):
    with col:
        st.markdown(f"""
        <div class='info-card'>
            <h3>{title}</h3>
            <p>{text}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navigation guide
st.markdown(
    "<div class='section-title'>📖 Dashboard Sections</div>",
    unsafe_allow_html=True
)

nav_items = [
    ("🌍", "Overview",        "Global picture & India's story"),
    ("🏳️", "Nation Analysis", "Compare any two nations"),
    ("🧬", "Performance DNA", "What actually wins medals"),
    ("🔄", "Quad Revolution", "How quads changed the sport"),
    ("🤖", "Medal Predictor", "Enter scores, get probability"),
    ("🇮🇳", "India Roadmap",  "The path forward"),
]

n1, n2, n3 = st.columns(3)
n4, n5, n6 = st.columns(3)

for col, (icon, title, desc) in zip(
    [n1, n2, n3, n4, n5, n6], nav_items
):
    with col:
        st.markdown(f"""
        <div class='info-card'>
            <div style='display:flex; align-items:center; gap:12px;'>
                <div style='font-size:1.8rem;'>{icon}</div>
                <div>
                    <div style='color:#1A2B4A; font-weight:700;
                                font-size:0.95rem;'>{title}</div>
                    <div style='color:#6B7B99; font-size:0.8rem;
                                margin-top:2px;'>{desc}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption(
    "Data: ISU Olympic Figure Skating Results (2006–2026) · "
    "World Championship Scores (2005–2024) · "
    "Built with Streamlit + scikit-learn + Plotly"
)