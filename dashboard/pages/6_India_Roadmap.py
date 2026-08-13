import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from components.data_loader import (
    load_aggregate, load_models,
    COLORS, MEDAL_COLORS, TRADITIONAL_NATIONS, FEATURES
)

df_raw, df_clean = load_aggregate()
rf_model, lr_model, scaler = load_models()

st.title("🇮🇳 India's Roadmap — Breaking the Ice")
st.markdown("---")

# ROW 1: The Reality
st.subheader("📍 Where India Stands Today")

r1, r2, r3, r4 = st.columns(4)
r1.metric("Olympic Appearances", "0", delta="Since 2006")
r2.metric("Medals Won", "0")
r3.metric("World Ranking", "N/A",
          delta="No ranked skaters")
r4.metric("Ice Rinks (est.)", "~30",
          delta="vs 2,000+ in USA")

st.error("""
**🇮🇳 India has never qualified a single figure skater
for the Winter Olympics.**

Across 20 years of data (2006–2026), 75 nations have
been represented. India is not among them.

But the data also shows us **exactly what it would take
to change that.** The path is measurable, and
Kazakhstan's 2026 gold proves that emerging nations
**can** break through.
""")

st.markdown("---")

# ─────────────────────────────────────────────
# ROW 2: The 4-Tier Roadmap
# ─────────────────────────────────────────────

st.subheader("🗺️ The 4-Tier Development Roadmap")

# Calculate thresholds from data
last_year = df_clean['year'].max()

thresholds = {}
for gender_code, gender_name in [('M', 'Men'), ('W', 'Women')]:
    g_data = df_clean[
        (df_clean['gender'] == gender_code) &
        (df_clean['year'] == last_year)
    ]
    thresholds[gender_name] = {
        'min_compete' : g_data['total_tss'].min(),
        'median'      : g_data['total_tss'].median(),
        'medal_min'   : g_data[
            g_data['medal'] > 0
        ]['total_tss'].min(),
        'gold'        : g_data[
            g_data['medal'] == 1
        ]['total_tss'].max(),
    }

gender_road = st.radio(
    "Select Gender:",
    ['Men', 'Women'],
    horizontal=True,
    key='roadmap_gender'
)

t = thresholds[gender_road]

# Tier visualization
tiers = pd.DataFrame([
    {
        'Tier': 'Tier 1: Olympic Qualification',
        'Score Target': t['min_compete'],
        'Description': 'Qualify for the Olympics',
        'Medal Prob': '< 1%',
        'Timeline': '5-8 years',
    },
    {
        'Tier': 'Tier 2: Complete Both Segments',
        'Score Target': t['median'],
        'Description': 'Avoid FNR, finish in field',
        'Medal Prob': '< 5%',
        'Timeline': '8-12 years',
    },
    {
        'Tier': 'Tier 3: Top 10 Finish',
        'Score Target': t['medal_min'] * 0.9,
        'Description': 'Compete near medal zone',
        'Medal Prob': '15-30%',
        'Timeline': '12-16 years',
    },
    {
        'Tier': 'Tier 4: Medal Contention',
        'Score Target': t['medal_min'],
        'Description': 'Realistic medal chance',
        'Medal Prob': '> 50%',
        'Timeline': '16-20 years',
    },
])

st.dataframe(
    tiers,
    use_container_width=True,
    hide_index=True,
)

# Visual tier chart
fig_tiers = go.Figure()

tier_colors = ['#3498DB', '#F39C12', '#E67E22', '#27AE60']
tier_names  = [
    'Tier 1:\nQualify',
    'Tier 2:\nComplete',
    'Tier 3:\nTop 10',
    'Tier 4:\nMedal',
]

fig_tiers.add_trace(go.Bar(
    x=tier_names,
    y=tiers['Score Target'],
    marker_color=tier_colors,
    text=[f"{s:.0f}" for s in tiers['Score Target']],
    textposition='outside',
    textfont=dict(size=14, color='black'),
))

# Add gold standard line
fig_tiers.add_hline(
    y=t['gold'],
    line_dash="dash",
    line_color=COLORS['gold'],
    line_width=2,
    annotation_text=f"Gold Standard: {t['gold']:.0f}",
    annotation_position="top right",
)

fig_tiers.update_layout(
    height=450,
    xaxis_title="Development Tier",
    yaxis_title=f"Target Score ({gender_road})",
    title=f"India's {gender_road}'s Score Targets",
)
st.plotly_chart(fig_tiers, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# ROW 3: Kazakhstan Case Study
# ─────────────────────────────────────────────

st.subheader("🇰🇿 The Kazakhstan Blueprint — Proof It's Possible")

kaz_data = df_clean[
    df_clean['nation'] == 'KAZ'
].sort_values('year')

col_kaz, col_lesson = st.columns([2, 1])

with col_kaz:
    if len(kaz_data) > 0:
        fig_kaz = go.Figure()

        fig_kaz.add_trace(go.Scatter(
            x=kaz_data['year'],
            y=kaz_data['total_tss'],
            mode='lines+markers+text',
            text=kaz_data['skater'],
            textposition='top center',
            textfont=dict(size=8),
            line=dict(color=COLORS['positive'], width=2.5),
            marker=dict(size=10),
            name='KAZ Skaters',
        ))

        # Highlight gold
        kaz_gold = kaz_data[kaz_data['medal'] == 1]
        if len(kaz_gold) > 0:
            fig_kaz.add_trace(go.Scatter(
                x=kaz_gold['year'],
                y=kaz_gold['total_tss'],
                mode='markers',
                marker=dict(
                    color=MEDAL_COLORS['Gold'],
                    size=20, symbol='star',
                    line=dict(width=2, color='black'),
                ),
                name='GOLD MEDAL',
            ))

        # Add global average
        global_avg = (
            df_clean.groupby('year')['total_tss']
            .mean()
            .reset_index()
        )
        fig_kaz.add_trace(go.Scatter(
            x=global_avg['year'],
            y=global_avg['total_tss'],
            mode='lines',
            line=dict(
                color='gray', width=1.5, dash='dot'
            ),
            name='Global Average',
            opacity=0.5,
        ))

        fig_kaz.update_layout(
            height=400,
            xaxis_title="Olympic Year",
            yaxis_title="Total Score",
            title="Kazakhstan's Olympic Journey",
        )
        st.plotly_chart(fig_kaz, use_container_width=True)

with col_lesson:
    st.markdown("**Key Lessons from Kazakhstan:**")

    if len(kaz_data) > 0:
        kaz_first = kaz_data['year'].min()
        kaz_gold_year = kaz_gold['year'].max() \
            if len(kaz_gold) > 0 else 'N/A'
        years_to_gold = (
            kaz_gold_year - kaz_first
            if kaz_gold_year != 'N/A' else 'N/A'
        )

        st.metric(
            "First Olympic Appearance",
            f"{kaz_first}"
        )
        st.metric(
            "First Gold Medal",
            f"{kaz_gold_year}"
        )
        st.metric(
            "Years from Entry to Gold",
            f"{years_to_gold} years"
        )

        st.markdown("---")

        st.info("""
        **Kazakhstan's Recipe:**
        1. Consistent Olympic qualification
        2. Gradual score improvement
        3. Investment in technical training
        4. Breakthrough athlete (Shaidorov)
        
        **India can replicate this model.**
        """)

st.markdown("---")

# ─────────────────────────────────────────────
# ROW 4: Qualification Threshold History
# ─────────────────────────────────────────────

st.subheader(
    "📊 Historical Qualification Thresholds — "
    "What Score Gets You In?"
)

fig_thresh = go.Figure()

for gender_code, gender_name, color in [
    ('M', 'Men',   COLORS['accent']),
    ('W', 'Women', COLORS['no_medal'])
]:
    g_data = df_clean[df_clean['gender'] == gender_code]

    # Min score to compete each year
    min_scores = (
        g_data.groupby('year')['total_tss']
        .min()
        .reset_index()
    )
    fig_thresh.add_trace(go.Scatter(
        x=min_scores['year'],
        y=min_scores['total_tss'],
        mode='lines+markers',
        name=f'{gender_name} (Min to Compete)',
        line=dict(color=color, width=2, dash='dot'),
        marker=dict(size=6),
    ))

    # Medal minimum each year
    medal_min = (
        g_data[g_data['medal'] > 0]
        .groupby('year')['total_tss']
        .min()
        .reset_index()
    )
    fig_thresh.add_trace(go.Scatter(
        x=medal_min['year'],
        y=medal_min['total_tss'],
        mode='lines+markers',
        name=f'{gender_name} (Min to Medal)',
        line=dict(color=color, width=3),
        marker=dict(size=10, symbol='star'),
    ))

fig_thresh.update_layout(
    height=450,
    xaxis_title="Olympic Year",
    yaxis_title="Total Score (TSS)",
    xaxis=dict(
        tickmode='array',
        tickvals=df_clean['year'].unique()
    ),
)
st.plotly_chart(fig_thresh, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# ROW 5: Data-Backed Recommendations
# ─────────────────────────────────────────────

st.subheader("✅ Data-Backed Recommendations for India")

rec1, rec2 = st.columns(2)

with rec1:
    st.markdown("### Immediate Actions (0-5 Years)")
    st.markdown("""
    **1. Infrastructure Investment**
    - Build 50+ international-standard ice rinks
    - Currently ~30 rinks vs 2,000+ in USA
    - Concentrate in 3-4 training centers
    
    **2. Talent Pipeline**
    - Identify athletes from roller skating,
      gymnastics, and dance backgrounds
    - Start competitive training before age 8
    - Send top prospects to train in Japan/Canada
    
    **3. International Exposure**
    - Compete in ISU Challenger Series
    - Target Asian Open competitions
    - Build ISU ranking points
    """)

with rec2:
    st.markdown("### Long-Term Strategy (5-20 Years)")
    st.markdown("""
    **4. Technical Focus**
    - Our model shows SP rank is 53.8% of medal prediction
    - Prioritize Short Program consistency
    - Develop quad jump capability
    
    **5. Score Targets (from our model)**
    - **Year 1-5:** Achieve 100+ (W) / 150+ (M) at
      international competitions
    - **Year 5-10:** Qualify for Olympics (152+ W / 202+ M)
    - **Year 10-15:** Top-10 finish (190+ W / 240+ M)
    - **Year 15-20:** Medal contention (220+ W / 275+ M)
    
    **6. Follow the Kazakhstan Model**
    - KAZ went from first appearance to gold
      in a defined timeline
    - Consistent participation + breakthrough athlete
    - India's population advantage = larger talent pool
    """)

st.markdown("---")

# ── Final Callout ────────────────────────────
st.success("""
**📌 The Bottom Line:**

India's absence from Olympic figure skating is not
inevitable — it's a **measurable gap** with a
**data-backed path forward.**

Our model shows:
- **Tier 1** (just qualifying) requires ~150-200 points
- **Tier 4** (medal contention) requires ~220-275 points
- **SP rank** is the single most important factor

Kazakhstan proved that an emerging nation can go from
zero to gold. With targeted investment in infrastructure,
talent development, and technical training,
**India can break the ice.**

*Built with data. Powered by possibility.*
""")