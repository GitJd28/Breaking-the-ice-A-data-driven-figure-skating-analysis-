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
from components.data_loader import load_aggregate, load_long
from components.styles import (
    load_css, apply_theme,
    CHART_COLORS, MEDAL_COLORS_LIGHT
)

st.set_page_config(page_title="Performance DNA", page_icon="🧬", layout="wide")
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
df_long = load_long()

st.markdown(
    "<div class='page-title'>🧬 Performance DNA — What Wins Medals?</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='page-subtitle'>"
    "Dissecting the anatomy of winning performances — "
    "from Short Program strategy to score composition."
    "</div>",
    unsafe_allow_html=True
)

# Headline finding
st.markdown("""
<div class='info-card' style='border-left: 4px solid #3D7EFF;'>
    <h3>🔑 Headline Finding</h3>
    <p>Short Program rank alone explains <b style='color:#3D7EFF;'>53.8%</b>
    of medal prediction in our Random Forest model — more than total score,
    technical score, or artistry combined. <b>Where you stand after the
    Short Program is the single most important factor in winning an
    Olympic medal.</b></p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# SP vs Final Rank
st.markdown(
    "<div class='section-title'>📋 Short Program Rank vs Final Rank</div>",
    unsafe_allow_html=True
)

gender_sp = st.radio(
    "Gender:", ['Both', 'Men', 'Women'],
    horizontal=True, key='sp_gender'
)
if gender_sp == 'Men':
    df_sp = df_clean[df_clean['gender'] == 'M']
elif gender_sp == 'Women':
    df_sp = df_clean[df_clean['gender'] == 'W']
else:
    df_sp = df_clean.copy()

col_sc, col_in = st.columns([2, 1])

with col_sc:
    fig_sp = go.Figure()
    for m in ['No Medal', 'Bronze', 'Silver', 'Gold']:
        subset = df_sp[df_sp['medal_label'] == m].dropna(subset=['final_rank_num'])
        size = 8 if m == 'No Medal' else 14
        symbol = 'circle' if m == 'No Medal' else 'star'
        opacity = 0.4 if m == 'No Medal' else 0.9
        if len(subset) > 0:
            fig_sp.add_trace(go.Scatter(
                x=subset['sp_rank'], y=subset['final_rank_num'],
                mode='markers', name=m,
                marker=dict(
                    color=MEDAL_COLORS_LIGHT[m], size=size,
                    symbol=symbol, opacity=opacity,
                    line=dict(width=0.5, color='white'),
                ),
                text=subset['skater'],
                hovertemplate="<b>%{text}</b><br>SP: %{x}<br>Final: %{y}<extra></extra>",
            ))

    max_rank = int(df_sp['sp_rank'].max())
    fig_sp.add_trace(go.Scatter(
        x=list(range(1, max_rank + 1)),
        y=list(range(1, max_rank + 1)),
        mode='lines', name='SP = Final',
        line=dict(dash='dash', color='gray', width=1),
    ))
    fig_sp.update_layout(
        xaxis_title="Short Program Rank",
        yaxis_title="Final Rank",
        title="Does SP Performance Predict Gold?",
        xaxis=dict(range=[0, 32]),
        yaxis=dict(range=[0, 32], autorange='reversed'),
    )
    fig_sp = apply_theme(fig_sp, height=500)
    st.plotly_chart(fig_sp, use_container_width=True)

with col_in:
    sp1 = df_clean[df_clean['sp_rank'] == 1]
    sp1_gold = sp1[sp1['medal'] == 1]
    sp3 = df_clean[df_clean['sp_rank'] <= 3]
    sp3_medal = sp3[sp3['medal'] > 0]

    st.metric(
        "SP #1 → Gold",
        f"{len(sp1_gold)}/{len(sp1)} ({len(sp1_gold)/max(len(sp1),1)*100:.0f}%)"
    )
    st.metric(
        "SP Top 3 → Medal",
        f"{len(sp3_medal)}/{len(sp3)} ({len(sp3_medal)/max(len(sp3),1)*100:.0f}%)"
    )

    st.markdown("---")
    st.markdown("**🔥 Biggest Comebacks**")

    comebacks = df_clean[
        (df_clean['medal'] > 0) & (df_clean['sp_rank'] > 3)
    ].sort_values('sp_rank', ascending=False)

    for _, row in comebacks.head(5).iterrows():
        emoji = {1: '🥇', 2: '🥈', 3: '🥉'}.get(row['medal'], '')
        st.markdown(
            f"- {emoji} **{row['skater']}** ({row['nation']}, "
            f"{int(row['year'])}): SP #{int(row['sp_rank'])} → "
            f"Final #{int(row['final_rank_num'])}"
        )

st.markdown("<br>", unsafe_allow_html=True)

# Score Anatomy
st.markdown(
    "<div class='section-title'>📊 Score Anatomy — What Makes a Medal Score?</div>",
    unsafe_allow_html=True
)

col_bar, col_radar = st.columns(2)

with col_bar:
    breakdown = (
        df_clean.groupby('medal_label')
        .agg(TES_SP=('tes_sp', 'mean'), PCS_SP=('pcs_sp', 'mean'),
             TES_FS=('tes_fs', 'mean'), PCS_FS=('pcs_fs', 'mean'))
        .reindex(['Gold', 'Silver', 'Bronze', 'No Medal'])
    )
    fig_bar = go.Figure()
    comps = [('TES_SP', 'TES (Short)', CHART_COLORS['primary']),
             ('PCS_SP', 'PCS (Short)', CHART_COLORS['accent']),
             ('TES_FS', 'TES (Free)',  CHART_COLORS['success']),
             ('PCS_FS', 'PCS (Free)',  CHART_COLORS['gold'])]
    for comp, label, color in comps:
        fig_bar.add_trace(go.Bar(
            x=breakdown.index, y=breakdown[comp],
            name=label, marker_color=color,
        ))
    fig_bar.update_layout(
        barmode='stack', xaxis_title="", yaxis_title="Score Points",
        title="Score Breakdown by Medal Status",
    )
    fig_bar = apply_theme(fig_bar, height=450)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_radar:
    categories = ['TES (SP)', 'PCS (SP)', 'TES (FS)', 'PCS (FS)', 'Momentum']
    fig_radar = go.Figure()
    for m, color in [('Gold', CHART_COLORS['gold']), ('No Medal', CHART_COLORS['no_medal'])]:
        subset = df_clean[df_clean['medal_label'] == m]
        if len(subset) > 0:
            vals = [
                subset['tes_sp'].mean() / df_clean['tes_sp'].max(),
                subset['pcs_sp'].mean() / df_clean['pcs_sp'].max(),
                subset['tes_fs'].mean() / df_clean['tes_fs'].max(),
                subset['pcs_fs'].mean() / df_clean['pcs_fs'].max(),
                subset['score_momentum'].mean() / df_clean['score_momentum'].max(),
            ]
            vals.append(vals[0])
            fig_radar.add_trace(go.Scatterpolar(
                r=vals, theta=categories + [categories[0]],
                fill='toself', name=m,
                line=dict(color=color, width=2), opacity=0.6,
            ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Medal Profile — Gold vs Field",
    )
    fig_radar = apply_theme(fig_radar, height=450)
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Deduction analysis
st.markdown(
    "<div class='section-title'>⚠️ Deduction Analysis — Do Falls Cost Medals?</div>",
    unsafe_allow_html=True
)

df_long_medal = df_long.merge(
    df_clean[['year', 'gender', 'skater', 'medal', 'medal_label']],
    on=['year', 'gender', 'skater'], how='left'
)
df_long_medal['medal_label'] = df_long_medal['medal_label'].fillna('No Medal')

col_d1, col_d2 = st.columns(2)

with col_d1:
    ded_pct = (
        df_long_medal.groupby('medal_label')['has_deduction']
        .mean().reindex(['Gold', 'Silver', 'Bronze', 'No Medal']) * 100
    ).reset_index()
    ded_pct.columns = ['Medal', 'Pct']

    fig_d1 = px.bar(
        ded_pct, x='Medal', y='Pct', color='Medal',
        color_discrete_map=MEDAL_COLORS_LIGHT,
        text='Pct',
    )
    fig_d1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_d1.update_layout(
        showlegend=False, xaxis_title="", yaxis_title="% Segments",
        title="% Segments With Deductions",
        yaxis=dict(range=[0, ded_pct['Pct'].max() * 1.4]),
    )
    fig_d1 = apply_theme(fig_d1, height=400)
    st.plotly_chart(fig_d1, use_container_width=True)

with col_d2:
    ded_avg = (
        df_long_medal.groupby(['segment', 'medal_label'])['ded']
        .mean().reset_index()
    )
    ded_avg = ded_avg[ded_avg['medal_label'].isin(
        ['Gold', 'Silver', 'Bronze', 'No Medal']
    )]
    fig_d2 = px.bar(
        ded_avg, x='segment', y='ded', color='medal_label',
        barmode='group', color_discrete_map=MEDAL_COLORS_LIGHT,
    )
    fig_d2.update_layout(
        xaxis_title="Segment", yaxis_title="Avg Deduction",
        title="Avg Deduction by Segment",
        legend_title="",
    )
    fig_d2 = apply_theme(fig_d2, height=400)
    st.plotly_chart(fig_d2, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Rank Change
st.markdown(
    "<div class='section-title'>🔄 Rank Change — SP to Final</div>",
    unsafe_allow_html=True
)

col_h, col_st = st.columns([2, 1])

with col_h:
    fig_rc = go.Figure()
    for m, color in [('No Medal', CHART_COLORS['no_medal']), ('Gold', CHART_COLORS['gold'])]:
        subset = df_clean[df_clean['medal_label'] == m]['rank_change']
        fig_rc.add_trace(go.Histogram(
            x=subset, name=m, marker_color=color, opacity=0.7, nbinsx=25,
        ))
    fig_rc.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text="No Change")
    fig_rc.update_layout(
        barmode='overlay', xaxis_title="Rank Change (SP → Final)",
        yaxis_title="Count", title="Rank Change Distribution",
    )
    fig_rc = apply_theme(fig_rc, height=400)
    st.plotly_chart(fig_rc, use_container_width=True)

with col_st:
    st.markdown("**Rank Change Stats**")
    for m in ['Gold', 'Silver', 'Bronze', 'No Medal']:
        subset = df_clean[df_clean['medal_label'] == m]['rank_change']
        emoji = {'Gold': '🥇', 'Silver': '🥈', 'Bronze': '🥉', 'No Medal': '🔵'}[m]
        st.markdown(
            f"{emoji} **{m}**: avg {subset.mean():+.1f} | "
            f"range [{subset.min():.0f}, {subset.max():.0f}]"
        )

st.markdown("<br>", unsafe_allow_html=True)
st.success(
    "📌 **Summary:** SP Rank is king (53.8%). Medal winners excel in ALL "
    "four score components, but the biggest gap is Free Skate TES. "
    "Clean programs (fewer deductions) win medals."
)