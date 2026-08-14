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
from components.data_loader import load_aggregate, load_worldchamp
from components.styles import (
    load_css, apply_theme, CHART_COLORS
)

st.set_page_config(page_title="Quad Revolution", page_icon="🔄", layout="wide")
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
df_wc = load_worldchamp()

st.markdown(
    "<div class='page-title'>🔄 The Quad Revolution</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='page-subtitle'>"
    "How quad jumps fundamentally changed figure skating post-2014, "
    "using World Championship data from 2005–2024."
    "</div>",
    unsafe_allow_html=True
)

# Metrics
pre  = df_wc[df_wc['quad_era'] == 0]
post = df_wc[df_wc['quad_era'] == 1]
corr = df_wc['total_quads'].corr(df_wc['total_score'])

q1, q2, q3 = st.columns(3)
cards = [
    (f"{pre['total_quads'].mean():.2f}", "Avg Quads Pre-2014", "Per skater"),
    (f"{post['total_quads'].mean():.2f}", "Avg Quads Post-2014",
     f"+{post['total_quads'].mean()-pre['total_quads'].mean():.2f} increase"),
    (f"r = {corr:.3f}", "Quads ↔ Score", "Strong positive"),
]
for col, (num, lbl, sub) in zip([q1, q2, q3], cards):
    with col:
        st.markdown(f"""
        <div class='stat-card-blue'>
            <div class='num'>{num}</div>
            <div class='lbl'>{lbl}</div>
            <div class='sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quads over time
st.markdown(
    "<div class='section-title'>📈 Quad Jumps Per Skater Over Time</div>",
    unsafe_allow_html=True
)

col_t, col_p = st.columns(2)

with col_t:
    qt = df_wc.groupby('year').agg(
        avg=('total_quads', 'mean'), mx=('total_quads', 'max')
    ).reset_index()

    fig_t = go.Figure()
    fig_t.add_trace(go.Bar(
        x=qt['year'], y=qt['avg'], name='Avg Quads',
        marker_color=[
            CHART_COLORS['no_medal'] if y < 2014 else CHART_COLORS['primary']
            for y in qt['year']
        ],
    ))
    fig_t.add_trace(go.Scatter(
        x=qt['year'], y=qt['mx'], name='Max Quads',
        mode='lines+markers',
        line=dict(color=CHART_COLORS['danger'], width=2),
        marker=dict(size=7), yaxis='y2',
    ))
    fig_t.add_vline(x=2014, line_dash="dash", line_color="black",
                    annotation_text="Quad Era")
    fig_t.update_layout(
        xaxis_title="Year", yaxis_title="Avg Quads",
        yaxis2=dict(title="Max Quads", overlaying='y', side='right'),
        title="Average & Max Quads Per Year",
    )
    fig_t = apply_theme(fig_t, height=420)
    st.plotly_chart(fig_t, use_container_width=True)

with col_p:
    qt2 = df_wc.groupby('year')['total_quads'].apply(
        lambda x: (x > 0).mean() * 100
    ).reset_index()
    qt2.columns = ['year', 'pct']

    fig_p = px.area(qt2, x='year', y='pct',
                    color_discrete_sequence=[CHART_COLORS['primary']])
    fig_p.add_vline(x=2014, line_dash="dash", line_color="black")
    fig_p.update_layout(
        xaxis_title="Year", yaxis_title="% With Quads",
        yaxis=dict(range=[0, 105]),
        title="% Skaters Attempting Quads", showlegend=False,
    )
    fig_p = apply_theme(fig_p, height=420)
    st.plotly_chart(fig_p, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quads vs Score
st.markdown(
    "<div class='section-title'>🎯 Quads vs Total Score</div>",
    unsafe_allow_html=True
)

col_s, col_b = st.columns(2)

with col_s:
    fig_qs = go.Figure()
    for era, label, color in [
        (0, 'Pre-2014',  CHART_COLORS['no_medal']),
        (1, 'Post-2014', CHART_COLORS['primary']),
    ]:
        subset = df_wc[df_wc['quad_era'] == era]
        fig_qs.add_trace(go.Scatter(
            x=subset['total_quads'], y=subset['total_score'],
            mode='markers', name=label,
            marker=dict(color=color, size=7, opacity=0.6),
        ))

    x_vals = df_wc['total_quads'].values
    y_vals = df_wc['total_score'].values
    z = np.polyfit(x_vals, y_vals, 1)
    p = np.poly1d(z)
    x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
    fig_qs.add_trace(go.Scatter(
        x=x_line, y=p(x_line), mode='lines',
        name=f'Trend (r={corr:.3f})',
        line=dict(color='black', width=2, dash='dash'),
    ))
    fig_qs.update_layout(
        xaxis_title="Total Quads", yaxis_title="Total Score",
        title="Quads vs Score Correlation",
    )
    fig_qs = apply_theme(fig_qs, height=420)
    st.plotly_chart(fig_qs, use_container_width=True)

with col_b:
    df_wc['quad_bucket'] = pd.cut(
        df_wc['total_quads'], bins=[-1, 0, 1, 2, 3, 8],
        labels=['0', '1', '2', '3', '4+']
    )
    fig_box = px.box(
        df_wc, x='quad_bucket', y='total_score',
        color='quad_bucket',
        color_discrete_sequence=px.colors.sequential.Blues[2:],
    )
    fig_box.update_layout(
        xaxis_title="Quads", yaxis_title="Total Score",
        title="Score by Quad Count", showlegend=False,
    )
    fig_box = apply_theme(fig_box, height=420)
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# TES vs PCS over time
st.markdown(
    "<div class='section-title'>⚖️ Technical vs Artistic Over Time</div>",
    unsafe_allow_html=True
)

col_l, col_r = st.columns(2)

with col_l:
    tp = df_wc.groupby('year')[['tes_total', 'pcs_total']].mean().reset_index()
    fig_tp = go.Figure()
    fig_tp.add_trace(go.Scatter(
        x=tp['year'], y=tp['tes_total'],
        mode='lines+markers', name='Technical (TES)',
        line=dict(color=CHART_COLORS['primary'], width=3), marker=dict(size=8),
    ))
    fig_tp.add_trace(go.Scatter(
        x=tp['year'], y=tp['pcs_total'],
        mode='lines+markers', name='Artistic (PCS)',
        line=dict(color=CHART_COLORS['accent'], width=3), marker=dict(size=8),
    ))
    fig_tp.add_vline(x=2014, line_dash="dash", line_color="black")
    fig_tp.update_layout(
        xaxis_title="Year", yaxis_title="Avg Score Component",
        title="TES vs PCS Over Time",
    )
    fig_tp = apply_theme(fig_tp, height=420)
    st.plotly_chart(fig_tp, use_container_width=True)

with col_r:
    sp_fs = df_wc.groupby('year')[['quads_in_sp', 'quads_in_fs']].mean().reset_index()
    fig_sf = go.Figure()
    fig_sf.add_trace(go.Bar(
        x=sp_fs['year'], y=sp_fs['quads_in_sp'],
        name='Quads in SP', marker_color=CHART_COLORS['no_medal'],
    ))
    fig_sf.add_trace(go.Bar(
        x=sp_fs['year'], y=sp_fs['quads_in_fs'],
        name='Quads in FS', marker_color=CHART_COLORS['primary'],
    ))
    fig_sf.update_layout(
        barmode='group', xaxis_title="Year", yaxis_title="Avg Quads",
        title="SP vs FS Quad Distribution",
    )
    fig_sf = apply_theme(fig_sf, height=420)
    st.plotly_chart(fig_sf, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.success(
    f"📌 **Summary:** Average quads jumped from "
    f"{pre['total_quads'].mean():.1f} to {post['total_quads'].mean():.1f} "
    f"post-2014. Correlation with score is r={corr:.3f}. "
    f"For India: quad capability is now mandatory for men's competition."
)