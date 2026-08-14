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
    load_aggregate, load_models, FEATURES, TRADITIONAL_NATIONS
)
from components.styles import (
    load_css, apply_theme, CHART_COLORS
)

st.set_page_config(page_title="India Roadmap", page_icon="🇮🇳", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
        <div class='icon'>⛸️</div>
        <div class='name'>Break the Ice</div>
        <div class='tag'>Figure Skating Analytics</div>
    </div>
    """, unsafe_allow_html=True)

df_raw, df_clean = load_aggregate()
rf_model, lr_model, scaler = load_models()

st.markdown(
    "<div class='page-title'>🇮🇳 India's Roadmap - Breaking the Ice</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='page-subtitle'>"
    "A data-backed development pathway for India's entry into "
    "Olympic figure skating; from first qualification to medal contention."
    "</div>",
    unsafe_allow_html=True
)

# Reality metrics
r1, r2, r3, r4 = st.columns(4)
reality = [
    ("0", "Olympic Appearances", "Since 2006"),
    ("0", "Medals Won", "All time"),
    ("N/A", "World Ranking", "No ranked skaters"),
    ("~30", "Ice Rinks (est.)", "vs 2,000+ in USA"),
]
for col, (num, lbl, sub) in zip([r1, r2, r3, r4], reality):
    with col:
        st.markdown(f"""
        <div class='stat-card-blue'>
            <div class='num'>{num}</div>
            <div class='lbl'>{lbl}</div>
            <div class='sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class='india-callout'>
    <p>🇮🇳 <b>India has never qualified a single figure skater for the
    Winter Olympics.</b> Across 20 years and 75 nations, India is absent.
    But the data shows us exactly what it would take to change that
    and Kazakhstan's 2026 gold proves emerging nations CAN break through.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4-Tier Roadmap
st.markdown(
    "<div class='section-title'>🗺️ The 4-Tier Development Roadmap</div>",
    unsafe_allow_html=True
)

gender_road = st.radio("Gender:", ['Men', 'Women'], horizontal=True, key='road_g')

last_year = df_clean['year'].max()
gc = 'M' if gender_road == 'Men' else 'W'
g_data = df_clean[(df_clean['gender'] == gc) & (df_clean['year'] == last_year)]

min_comp  = g_data['total_tss'].min()
median_sc = g_data['total_tss'].median()
medal_min = g_data[g_data['medal'] > 0]['total_tss'].min()
gold_sc   = g_data[g_data['medal'] == 1]['total_tss'].max()

tiers = pd.DataFrame([
    {'Tier': 'Tier 1: Qualify', 'Score': f"{min_comp:.0f}", 'Prob': '< 1%', 'Timeline': '5-8 yrs'},
    {'Tier': 'Tier 2: Complete', 'Score': f"{median_sc:.0f}", 'Prob': '< 5%', 'Timeline': '8-12 yrs'},
    {'Tier': 'Tier 3: Top 10', 'Score': f"{medal_min*0.9:.0f}", 'Prob': '15-30%', 'Timeline': '12-16 yrs'},
    {'Tier': 'Tier 4: Medal', 'Score': f"{medal_min:.0f}", 'Prob': '> 50%', 'Timeline': '16-20 yrs'},
])

col_tbl, col_chart = st.columns([1, 2])

with col_tbl:
    st.dataframe(tiers, use_container_width=True, hide_index=True)

with col_chart:
    tier_scores = [min_comp, median_sc, medal_min * 0.9, medal_min]
    tier_names  = ['Qualify', 'Complete', 'Top 10', 'Medal']
    tier_colors = ['#B8C5D6', '#3D7EFF', '#F39C12', '#00C878']

    fig_tier = go.Figure()
    fig_tier.add_trace(go.Bar(
        x=tier_names, y=tier_scores,
        marker_color=tier_colors,
        text=[f"{s:.0f}" for s in tier_scores],
        textposition='outside',
        textfont=dict(size=16, color='#1A2B4A'),
    ))
    fig_tier.add_hline(
        y=gold_sc, line_dash="dash", line_color=CHART_COLORS['gold'],
        annotation_text=f"Gold: {gold_sc:.0f}",
    )
    fig_tier.update_layout(
        xaxis_title="Development Tier",
        yaxis_title=f"Score Target ({gender_road})",
        title=f"India's {gender_road}'s Score Targets",
    )
    fig_tier = apply_theme(fig_tier, height=420)
    st.plotly_chart(fig_tier, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Kazakhstan case study
st.markdown(
    "<div class='section-title'>🇰🇿 The Kazakhstan Blueprint</div>",
    unsafe_allow_html=True
)

kaz = df_clean[df_clean['nation'] == 'KAZ'].sort_values('year')
kaz_gold = kaz[kaz['medal'] == 1]

col_kc, col_kl = st.columns([2, 1])

with col_kc:
    if len(kaz) > 0:
        fig_k = go.Figure()
        fig_k.add_trace(go.Scatter(
            x=kaz['year'], y=kaz['total_tss'],
            mode='lines+markers+text',
            text=kaz['skater'], textposition='top center',
            textfont=dict(size=8, color='#6B7B99'),
            line=dict(color=CHART_COLORS['success'], width=2.5),
            marker=dict(size=10), name='KAZ Skaters',
        ))
        if len(kaz_gold) > 0:
            fig_k.add_trace(go.Scatter(
                x=kaz_gold['year'], y=kaz_gold['total_tss'],
                mode='markers', name='GOLD',
                marker=dict(color=CHART_COLORS['gold'], size=20, symbol='star',
                            line=dict(width=2, color='black')),
            ))

        ga = df_clean.groupby('year')['total_tss'].mean().reset_index()
        fig_k.add_trace(go.Scatter(
            x=ga['year'], y=ga['total_tss'],
            mode='lines', name='Global Avg',
            line=dict(color='gray', dash='dot', width=1.5), opacity=0.5,
        ))
        fig_k.update_layout(
            xaxis_title="Year", yaxis_title="Total Score",
            title="Kazakhstan's Olympic Journey",
        )
        fig_k = apply_theme(fig_k, height=400)
        st.plotly_chart(fig_k, use_container_width=True)

with col_kl:
    st.markdown("""
    <div class='info-card'>
        <h3>Key Lessons</h3>
        <p>✅ Consistent Olympic qualification</p>
        <p>✅ Gradual score improvement</p>
        <p>✅ Investment in technical training</p>
        <p>✅ Breakthrough athlete (Shaidorov)</p>
        <p style='margin-top:16px;'><b>India can replicate this model.</b></p>
    </div>
    """, unsafe_allow_html=True)

    if len(kaz) > 0:
        kf = kaz['year'].min()
        kg = kaz_gold['year'].max() if len(kaz_gold) > 0 else 'N/A'
        st.metric("First Appearance", f"{kf}")
        st.metric("First Gold", f"{kg}")
        st.metric("Years to Gold", f"{kg - kf}" if kg != 'N/A' else 'N/A')

st.markdown("<br>", unsafe_allow_html=True)

# Thresholds over time
st.markdown(
    "<div class='section-title'>📊 Historical Qualification Thresholds</div>",
    unsafe_allow_html=True
)

fig_th = go.Figure()
for gc2, gn, color in [('M', 'Men', CHART_COLORS['primary']), ('W', 'Women', CHART_COLORS['accent'])]:
    gd = df_clean[df_clean['gender'] == gc2]
    mins = gd.groupby('year')['total_tss'].min().reset_index()
    fig_th.add_trace(go.Scatter(
        x=mins['year'], y=mins['total_tss'],
        mode='lines+markers', name=f'{gn} (Min Compete)',
        line=dict(color=color, width=2, dash='dot'), marker=dict(size=6),
    ))
    mm = gd[gd['medal'] > 0].groupby('year')['total_tss'].min().reset_index()
    fig_th.add_trace(go.Scatter(
        x=mm['year'], y=mm['total_tss'],
        mode='lines+markers', name=f'{gn} (Min Medal)',
        line=dict(color=color, width=3), marker=dict(size=10, symbol='star'),
    ))

fig_th.update_layout(
    xaxis_title="Year", yaxis_title="Total Score",
    title="What Score Gets You In?",
    xaxis=dict(tickmode='array', tickvals=df_clean['year'].unique()),
)
fig_th = apply_theme(fig_th, height=420)
st.plotly_chart(fig_th, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Recommendations
st.markdown(
    "<div class='section-title'>✅ Data-Backed Recommendations:</div>",
    unsafe_allow_html=True
)

col_now, col_future = st.columns(2)

with col_now:
    st.markdown("""
    <div class='info-card'>
        <h3>🏃 Immediate Actions (0-5 Years)</h3>
        <p><b>1. Infrastructure:</b> Build 50+ international-standard 
        ice rinks concentrated in 3-4 training centers.</p>
        <p><b>2. Talent Pipeline:</b> Identify athletes from roller skating, 
        gymnastics, and dance. Start competitive training before age 8.</p>
        <p><b>3. International Exposure:</b> Compete in ISU Challenger Series. 
        Target Asian Open competitions. Build ISU ranking points.</p>
    </div>
    """, unsafe_allow_html=True)

with col_future:
    st.markdown("""
    <div class='info-card'>
        <h3>🎯 Long-Term Strategy (5-20 Years)</h3>
        <p><b>4. Technical Focus:</b> SP rank is 53.8% of medal prediction. 
        Prioritize Short Program consistency. Develop quad jump capability.</p>
        <p><b>5. Score Targets:</b><br>
        Year 1-5: 100+ (W) / 150+ (M)<br>
        Year 5-10: Qualify for Olympics<br>
        Year 10-15: Top-10 finish<br>
        Year 15-20: Medal contention</p>
        <p><b>6. Follow the Kazakhstan Model:</b> Consistent participation 
        + breakthrough athlete. India's population = larger talent pool.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.success(
    "📌 **The Bottom Line:** India's absence is a measurable gap with a "
    "data-backed path forward. Kazakhstan proved emerging nations can win gold. "
    "With targeted investment, India can break the ice. "
    "*Built with data. Powered by possibility.*"
)