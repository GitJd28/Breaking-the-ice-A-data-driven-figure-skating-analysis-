import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components.styles import load_css
from components.data_loader import load_aggregate, load_worldchamp

st.set_page_config(
    page_title = "Break the Ice | Figure Skating Analytics",
    page_icon  = "⛸️",
    layout     = "wide",
    initial_sidebar_state = "expanded"
)

st.markdown(load_css(), unsafe_allow_html=True)

# ── Sidebar Branding ──────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 24px 0;'>
        <div style='font-size: 2.5rem;'>⛸️</div>
        <div style='color: #00D4FF; font-weight: 700;
                    font-size: 1.1rem; margin-top: 8px;'>
            Break the Ice
        </div>
        <div style='color: #4A7FA5; font-size: 0.75rem;
                    margin-top: 4px;'>
            Figure Skating Analytics
        </div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='color: #4A7FA5; font-size: 0.75rem;
                padding: 0 8px;'>
        <p>📊 6 Olympic Games</p>
        <p>🌍 75 Nations</p>
        <p>👤 357 Athletes</p>
        <p>🤖 AUC: 0.983</p>
    </div>
    """, unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────
st.markdown("""
<div class='page-header'>
    <h1>⛸️ Break the Ice</h1>
    <p>
        A data-driven analysis of Olympic Figure Skating —
        uncovering what separates champions from the field,
        and charting a path for emerging nations.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Top Metrics ───────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class='stat-card'>
        <div class='stat-number'>6</div>
        <div class='stat-label'>Olympic Games</div>
        <div class='stat-sub'>2006 → 2026</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class='stat-card'>
        <div class='stat-number'>75</div>
        <div class='stat-label'>Nations</div>
        <div class='stat-sub'>Represented</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class='stat-card'>
        <div class='stat-number'>0.983</div>
        <div class='stat-label'>Model AUC</div>
        <div class='stat-sub'>Random Forest</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class='stat-card'>
        <div class='stat-number'>90+</div>
        <div class='stat-label'>Point Gap</div>
        <div class='stat-sub'>Medal vs Field</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Key Findings Cards ────────────────────────
st.markdown(
    "<div class='section-header'>🔍 Key Findings</div>",
    unsafe_allow_html=True
)

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
    <div class='ice-card'>
        <h3>🏅 The 90-Point Wall</h3>
        <p>
            Medal winners score an average of
            <strong style='color:#00D4FF;'>90+ points more</strong>
            than non-medalists. A consistent,
            structural gap — not random variation.
        </p>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class='ice-card'>
        <h3>📋 Short Program is Everything</h3>
        <p>
            Short Program rank explains
            <strong style='color:#00D4FF;'>53.8%</strong>
            of medal prediction — the single most
            important factor in our model.
        </p>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class='ice-card'>
        <h3>🔄 The Quad Revolution</h3>
        <p>
            Post-2014, quad jumps correlate with
            scores at <strong style='color:#00D4FF;'>
            r = 0.700</strong>. Technical content
            now drives results above artistry.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation Guide ─────────────────────────
st.markdown(
    "<div class='section-header'>📖 Navigate the Dashboard</div>",
    unsafe_allow_html=True
)

n1, n2, n3, n4, n5, n6 = st.columns(6)

nav_items = [
    ("🌍", "Overview",        "Global picture,\nIndia's story"),
    ("🏳️", "Nation Analysis", "Compare any\ntwo nations"),
    ("🧬", "Performance DNA", "What actually\nwins medals"),
    ("🔄", "Quad Revolution", "How quads changed\nthe sport"),
    ("🤖", "Medal Predictor", "Enter scores,\nget probability"),
    ("🇮🇳", "India Roadmap",  "The path\nforward"),
]

for col, (icon, title, desc) in zip(
    [n1, n2, n3, n4, n5, n6], nav_items
):
    with col:
        st.markdown(f"""
        <div class='ice-card' style='text-align:center;
                    padding: 16px 12px;'>
            <div style='font-size:1.8rem;'>{icon}</div>
            <div style='color:#00D4FF; font-weight:600;
                        font-size:0.85rem; margin:6px 0 4px;'>
                {title}
            </div>
            <div style='color:#4A7FA5; font-size:0.72rem;
                        white-space:pre-line;'>
                {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────
st.markdown("""
<div class='footer'>
    Data: ISU Olympic Figure Skating Results (2006–2026)
    · World Championship Scores (2005–2024)
    · Built with Streamlit · scikit-learn · Plotly
</div>
""", unsafe_allow_html=True)