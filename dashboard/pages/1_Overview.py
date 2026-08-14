import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from components.data_loader import (
    load_aggregate, load_long, TRADITIONAL_NATIONS
)
from components.styles import (
    load_css, apply_theme,
    CHART_COLORS, MEDAL_COLORS_LIGHT
)

st.set_page_config(page_title="Overview", page_icon="🌍", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)

df_raw, df_clean = load_aggregate()
df_long = load_long()

# Sidebar branding
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
        <div class='icon'>⛸️</div>
        <div class='name'>Break the Ice</div>
        <div class='tag'>Figure Skating Analytics</div>
    </div>
    """, unsafe_allow_html=True)

# Page header
st.markdown(
    "<div class='page-title'>🌍 Overview — The Global Picture</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='page-subtitle'>"
    "How Olympic figure skating is distributed across nations, "
    "and where the medal gap really lies."
    "</div>",
    unsafe_allow_html=True
)

# Top stat cards
medal_avg    = df_clean[df_clean['medal'] > 0]['total_tss'].mean()
no_medal_avg = df_clean[df_clean['medal'] == 0]['total_tss'].mean()
gap          = medal_avg - no_medal_avg
nations      = df_raw['nation'].nunique()
india_rows   = len(df_raw[df_raw['nation'] == 'IND'])

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class='stat-card-blue'>
        <div class='num'>{nations}</div>
        <div class='lbl'>Nations</div>
        <div class='sub'>Represented</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='stat-card-blue'>
        <div class='num'>{medal_avg:.0f}</div>
        <div class='lbl'>Medalist Avg</div>
        <div class='sub'>Total Score</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='stat-card-blue'>
        <div class='num'>{no_medal_avg:.0f}</div>
        <div class='lbl'>Non-Medalist Avg</div>
        <div class='sub'>Total Score</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='stat-card-blue'>
        <div class='num'>{gap:.0f}</div>
        <div class='lbl'>Point Gap</div>
        <div class='sub'>Medalists lead</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# India callout
st.markdown(f"""
<div class='india-callout'>
    <p>🇮🇳 <b>India has {india_rows} appearances</b> in 20 years
    of Olympic Figure Skating data (2006–2026). Across {nations}
    nations that have participated, India has never qualified
    a single skater.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Row: Two charts side by side
st.markdown(
    "<div class='section-title'>Which Nations Dominate?</div>",
    unsafe_allow_html=True
)

col_a, col_b = st.columns(2)

with col_a:
    nation_counts = (
        df_raw['nation'].value_counts().head(15).reset_index()
    )
    nation_counts.columns = ['nation', 'appearances']

    fig1 = px.bar(
        nation_counts,
        x='appearances', y='nation',
        orientation='h',
        color_discrete_sequence=[CHART_COLORS['primary']],
    )
    fig1.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Athletes",
        yaxis_title="",
        title="Olympic Appearances (Top 15 Nations)",
    )
    fig1 = apply_theme(fig1, height=450)
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    medal_df = df_raw[df_raw['medal'] > 0].copy()
    medal_counts = (
        medal_df.groupby(['nation', 'medal_label'])
        .size().reset_index(name='count')
    )
    nation_totals = (
        medal_counts.groupby('nation')['count']
        .sum().sort_values(ascending=False).head(10)
        .index.tolist()
    )
    medal_counts = medal_counts[
        medal_counts['nation'].isin(nation_totals)
    ]

    fig2 = px.bar(
        medal_counts,
        x='count', y='nation',
        color='medal_label', orientation='h',
        color_discrete_map=MEDAL_COLORS_LIGHT,
        category_orders={
            'medal_label': ['Gold', 'Silver', 'Bronze'],
            'nation': nation_totals,
        },
    )
    fig2.update_layout(
        xaxis_title="Medals",
        yaxis_title="",
        legend_title="",
        title="Medal Count by Nation (Top 10)",
    )
    fig2 = apply_theme(fig2, height=450)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Score distributions
st.markdown(
    "<div class='section-title'>Score Distributions: Medalists vs Non-Medalists</div>",
    unsafe_allow_html=True
)

gender_filter = st.radio(
    "Gender:", ['Both', 'Men', 'Women'],
    horizontal=True, key='overview_gender'
)

if gender_filter == 'Men':
    df_f = df_clean[df_clean['gender'] == 'M']
elif gender_filter == 'Women':
    df_f = df_clean[df_clean['gender'] == 'W']
else:
    df_f = df_clean.copy()

col_c, col_d = st.columns(2)

with col_c:
    fig3 = go.Figure()
    for m in ['No Medal', 'Gold', 'Silver', 'Bronze']:
        subset = df_f[df_f['medal_label'] == m]['total_tss']
        if len(subset) > 0:
            fig3.add_trace(go.Histogram(
                x=subset, name=m,
                marker_color=MEDAL_COLORS_LIGHT[m],
                opacity=0.75, nbinsx=20,
            ))
    fig3.update_layout(
        barmode='overlay',
        xaxis_title="Total Score",
        yaxis_title="Count",
        title="Score Distribution",
        legend_title="",
    )
    fig3 = apply_theme(fig3, height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    fig4 = go.Figure()
    for m in ['No Medal', 'Bronze', 'Silver', 'Gold']:
        subset = df_f[df_f['medal_label'] == m]
        size = 8 if m == 'No Medal' else 14
        symbol = 'circle' if m == 'No Medal' else 'star'
        if len(subset) > 0:
            fig4.add_trace(go.Scatter(
                x=subset['tes_total'], y=subset['pcs_total'],
                mode='markers', name=m,
                marker=dict(
                    color=MEDAL_COLORS_LIGHT[m],
                    size=size, symbol=symbol,
                    opacity=0.9 if m != 'No Medal' else 0.5,
                    line=dict(width=0.5, color='white'),
                ),
            ))
    fig4.update_layout(
        xaxis_title="Technical Score (TES)",
        yaxis_title="Program Components (PCS)",
        title="TES vs PCS",
        legend_title="",
    )
    fig4 = apply_theme(fig4, height=400)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Trends over time
st.markdown(
    "<div class='section-title'>Score Trends Across Olympic Games</div>",
    unsafe_allow_html=True
)

metric_choice = st.selectbox(
    "Metric:",
    ['total_tss', 'tes_total', 'pcs_total', 'tech_dominance_pct'],
    format_func=lambda x: {
        'total_tss': 'Total Score (TSS)',
        'tes_total': 'Technical Score (TES)',
        'pcs_total': 'Program Components (PCS)',
        'tech_dominance_pct': 'TES Dominance Ratio',
    }[x]
)

fig5 = go.Figure()
for g, name, color in [
    ('M', 'Men',   CHART_COLORS['primary']),
    ('W', 'Women', CHART_COLORS['accent'])
]:
    all_ = df_clean[df_clean['gender'] == g].groupby('year')[metric_choice].mean().reset_index()
    fig5.add_trace(go.Scatter(
        x=all_['year'], y=all_[metric_choice],
        mode='lines+markers', name=f'{name} (All)',
        line=dict(color=color, width=2), opacity=0.5,
    ))
    med = df_clean[(df_clean['gender'] == g) & (df_clean['medal'] > 0)].groupby('year')[metric_choice].mean().reset_index()
    fig5.add_trace(go.Scatter(
        x=med['year'], y=med[metric_choice],
        mode='lines+markers', name=f'{name} (Medalists)',
        line=dict(color=color, width=3, dash='dash'),
        marker=dict(size=10, symbol='star'),
    ))

fig5.update_layout(
    xaxis_title="Year",
    yaxis_title=metric_choice,
    title=f"{metric_choice} over Olympic Games",
    xaxis=dict(tickmode='array', tickvals=df_clean['year'].unique()),
)
fig5 = apply_theme(fig5, height=450)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Traditional vs Emerging
st.markdown(
    "<div class='section-title'>Traditional Powers vs Emerging Nations</div>",
    unsafe_allow_html=True
)

df_clean['nation_type'] = df_clean['nation'].apply(
    lambda x: 'Traditional Power' if x in TRADITIONAL_NATIONS
    else 'Emerging Nation'
)

col_e, col_f = st.columns([2, 1])

with col_e:
    fig6 = px.box(
        df_clean, x='nation_type', y='total_tss',
        color='nation_type',
        color_discrete_map={
            'Traditional Power': CHART_COLORS['primary'],
            'Emerging Nation'  : CHART_COLORS['accent'],
        },
        points='all',
    )
    fig6.update_layout(
        xaxis_title="",
        yaxis_title="Total Score",
        title="Score Distribution",
        showlegend=False,
    )
    fig6 = apply_theme(fig6, height=400)
    st.plotly_chart(fig6, use_container_width=True)

with col_f:
    trad_avg = df_clean[df_clean['nation_type'] == 'Traditional Power']['total_tss'].mean()
    emrg_avg = df_clean[df_clean['nation_type'] == 'Emerging Nation']['total_tss'].mean()

    st.metric("Traditional Powers Avg", f"{trad_avg:.1f}")
    st.metric("Emerging Nations Avg",   f"{emrg_avg:.1f}")
    st.metric("Score Gap", f"{trad_avg - emrg_avg:.1f} pts")

st.markdown("<br>", unsafe_allow_html=True)
st.success(
    "📌 **Key Takeaway:** Figure skating is dominated by a handful of "
    "nations. The 90-point gap between medalists and non-medalists is "
    "structural. But Kazakhstan's 2026 gold proves emerging nations "
    "CAN break through."
)