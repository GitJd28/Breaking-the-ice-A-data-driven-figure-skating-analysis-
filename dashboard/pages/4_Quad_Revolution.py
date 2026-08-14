import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.styles import load_css, apply_theme, PLOTLY_THEME
st.markdown(load_css(), unsafe_allow_html=True)
from components.data_loader import (
    load_aggregate, load_worldchamp,
    MEDAL_COLORS, COLORS
)

df_raw, df_clean = load_aggregate()
df_wc = load_worldchamp()

st.title("🔄 The Quad Revolution")
st.markdown("---")

# ROW 1: Context
st.warning("""
**The Quad Revolution** — Around 2014, figure skating
underwent a fundamental shift. Quad jumps (4 rotations)
went from rare feats to mandatory requirements.
This section explores how that changed the sport using
World Championship data from 2005–2024.
""")

q1, q2, q3 = st.columns(3)

pre_quad  = df_wc[df_wc['quad_era'] == 0]
post_quad = df_wc[df_wc['quad_era'] == 1]

q1.metric(
    "Avg Quads Pre-2014",
    f"{pre_quad['total_quads'].mean():.2f}",
    delta="per skater"
)
q2.metric(
    "Avg Quads Post-2014",
    f"{post_quad['total_quads'].mean():.2f}",
    delta=f"+{post_quad['total_quads'].mean() - pre_quad['total_quads'].mean():.2f} increase"
)
q3.metric(
    "Quads ↔ Score Correlation",
    f"r = {df_wc['total_quads'].corr(df_wc['total_score']):.3f}",
    delta="Strong positive"
)

st.markdown("---")

# ─────────────────────────────────────────────
# ROW 2: Quads Over Time
# ─────────────────────────────────────────────

st.subheader("📈 Quad Jumps Per Skater Over Time")

col_trend, col_dist = st.columns(2)

with col_trend:
    quad_trend = (
        df_wc.groupby('year')
        .agg(
            avg_quads=('total_quads', 'mean'),
            max_quads=('total_quads', 'max'),
            pct_with_quads=(
                'total_quads',
                lambda x: (x > 0).mean() * 100
            ),
        )
        .reset_index()
    )

    fig_trend = go.Figure()

    fig_trend.add_trace(go.Bar(
        x=quad_trend['year'],
        y=quad_trend['avg_quads'],
        name='Avg Quads',
        marker_color=[
            COLORS['pre_quad'] if y < 2014
            else COLORS['post_quad']
            for y in quad_trend['year']
        ],
        opacity=0.8,
    ))

    fig_trend.add_trace(go.Scatter(
        x=quad_trend['year'],
        y=quad_trend['max_quads'],
        name='Max Quads (Best Skater)',
        mode='lines+markers',
        line=dict(color=COLORS['accent'], width=2),
        marker=dict(size=8),
        yaxis='y2',
    ))

    fig_trend.add_vline(
        x=2014, line_dash="dash",
        line_color="black", line_width=2,
        annotation_text="Quad Era Begins",
        annotation_position="top left",
    )

    fig_trend.update_layout(
        height=450,
        xaxis_title="Year",
        yaxis_title="Average Quads Per Skater",
        yaxis2=dict(
            title="Max Quads",
            overlaying='y',
            side='right',
        ),
        legend=dict(x=0.01, y=0.99),
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_dist:
    st.markdown("**% of Skaters Attempting Quads**")

    quad_trend2 = (
        df_wc.groupby('year')['total_quads']
        .apply(lambda x: (x > 0).mean() * 100)
        .reset_index()
    )
    quad_trend2.columns = ['year', 'pct_with_quads']

    fig_pct = px.area(
        quad_trend2,
        x='year',
        y='pct_with_quads',
        color_discrete_sequence=[COLORS['accent']],
    )

    fig_pct.add_vline(
        x=2014, line_dash="dash",
        line_color="black", line_width=2,
    )

    fig_pct.update_layout(
        height=450,
        xaxis_title="Year",
        yaxis_title="% Skaters With Quads",
        yaxis=dict(range=[0, 105]),
        showlegend=False,
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_pct, use_container_width=True)

st.markdown("---")

# ROW 3: Quads vs Score

st.subheader("🎯 Quads vs Total Score — The Correlation")
col_scatter, col_box = st.columns(2)
with col_scatter:
    fig_qs = px.scatter(
        df_wc,
        x='total_quads',
        y='total_score',
        color='quad_era',
        color_discrete_map={
            0: COLORS['pre_quad'],
            1: COLORS['post_quad'],
        },
        opacity=0.6,
        trendline='ols',
        labels={
            'total_quads': 'Total Quads Attempted',
            'total_score': 'Total Score',
            'quad_era'   : 'Era',
        },
    )

    fig_qs.update_layout(
        height=450,
        legend_title="Era",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")

    # Fix legend labels
    fig_qs.for_each_trace(
        lambda t: t.update(
            name='Pre-2014' if t.name == '0'
            else ('Post-2014' if t.name == '1' else t.name)
        )
    )

    st.plotly_chart(fig_qs, use_container_width=True)

with col_box:
    st.markdown("**Score Distribution by Quad Count**")

    df_wc['quad_bucket'] = pd.cut(
        df_wc['total_quads'],
        bins=[-1, 0, 1, 2, 3, 8],
        labels=['0', '1', '2', '3', '4+']
    )

    fig_box = px.box(
        df_wc,
        x='quad_bucket',
        y='total_score',
        color='quad_bucket',
        color_discrete_sequence=px.colors.sequential.Reds,
    )
    fig_box.update_layout(
        height=450,
        xaxis_title="Number of Quads",
        yaxis_title="Total Score",
        showlegend=False,
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# ROW 4: TES vs PCS Over Time
st.subheader(
    "⚖️ Technical (TES) vs Artistic (PCS) — "
    "Which Matters More Now?"
)
col_line, col_ratio = st.columns(2)
with col_line:
    tes_pcs_trend = (
        df_wc.groupby('year')[['tes_total', 'pcs_total']]
        .mean()
        .reset_index()
    )
    fig_tp = go.Figure()
    fig_tp.add_trace(go.Scatter(
        x=tes_pcs_trend['year'],
        y=tes_pcs_trend['tes_total'],
        mode='lines+markers',
        name='Technical (TES)',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=8),
    ))
    fig_tp.add_trace(go.Scatter(
        x=tes_pcs_trend['year'],
        y=tes_pcs_trend['pcs_total'],
        mode='lines+markers',
        name='Artistic (PCS)',
        line=dict(color=COLORS['no_medal'], width=3),
        marker=dict(size=8),
    ))

    fig_tp.add_vline(
        x=2014, line_dash="dash",
        line_color="black", line_width=1.5,
        annotation_text="Quad Era",
    )

    fig_tp.update_layout(
        height=400,
        xaxis_title="Year",
        yaxis_title="Average Score Component",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_tp, use_container_width=True)

with col_ratio:
    st.markdown("**TES/PCS Ratio Over Time**")

    ratio_trend = (
        df_wc.groupby('year')['tes_pcs_ratio']
        .mean()
        .reset_index()
    )

    fig_ratio = go.Figure()

    fig_ratio.add_trace(go.Scatter(
        x=ratio_trend['year'],
        y=ratio_trend['tes_pcs_ratio'],
        mode='lines+markers+text',
        line=dict(color=COLORS['accent'], width=2.5),
        marker=dict(size=8),
        text=[f"{v:.3f}" for v in ratio_trend['tes_pcs_ratio']],
        textposition='top center',
        textfont=dict(size=8),
    ))

    fig_ratio.add_hline(
        y=1.0, line_dash="dash",
        line_color="gray",
        annotation_text="TES = PCS",
    )

    fig_ratio.update_layout(
        height=400,
        xaxis_title="Year",
        yaxis_title="TES / PCS Ratio",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_ratio, use_container_width=True)

st.markdown("---")

# ROW 5: SP vs FS Quads
st.subheader(
    "🏋️ Quad Distribution — Short Program vs Free Skate"
)
col_sp_fs, col_heatmap = st.columns(2)
with col_sp_fs:
    sp_fs_quads = (
        df_wc.groupby('year')[['quads_in_sp', 'quads_in_fs']]
        .mean()
        .reset_index()
    )
    fig_spfs = go.Figure()
    fig_spfs.add_trace(go.Bar(
        x=sp_fs_quads['year'],
        y=sp_fs_quads['quads_in_sp'],
        name='Quads in SP',
        marker_color=COLORS['no_medal'],
    ))
    fig_spfs.add_trace(go.Bar(
        x=sp_fs_quads['year'],
        y=sp_fs_quads['quads_in_fs'],
        name='Quads in FS',
        marker_color=COLORS['accent'],
    ))

    fig_spfs.update_layout(
        barmode='group',
        height=400,
        xaxis_title="Year",
        yaxis_title="Average Quads",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_spfs, use_container_width=True)

with col_heatmap:
    st.markdown("**Quads SP vs FS — Heatmap**")

    heatmap_data = (
        df_wc.groupby(['quads_in_sp', 'quads_in_fs'])
        .size()
        .reset_index(name='count')
    )

    heatmap_pivot = heatmap_data.pivot(
        index='quads_in_fs',
        columns='quads_in_sp',
        values='count'
    ).fillna(0)

    fig_heat = px.imshow(
        heatmap_pivot,
        color_continuous_scale='YlOrRd',
        labels=dict(
            x="Quads in SP",
            y="Quads in FS",
            color="Count"
        ),
        text_auto=True,
    )
    fig_heat.update_layout(
        height=400,
        yaxis=dict(autorange='reversed'),
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ── Takeaway ─────────────────────────────────
st.success(f"""
**📌 Quad Revolution Summary:**

1. **Average quads per skater** jumped from
   {pre_quad['total_quads'].mean():.1f} (pre-2014) to
   {post_quad['total_quads'].mean():.1f} (post-2014).

2. **Correlation with score** is strong (r =
   {df_wc['total_quads'].corr(df_wc['total_score']):.3f}).
   More quads = higher scores — consistently.

3. **TES has overtaken PCS** as the primary score driver
   in recent years. Technical content now matters more
   than artistry for winning.

4. **For India:** Any aspiring Olympic skater must
   develop quad jump capability. Without quads,
   competing at the modern Olympic level is
   effectively impossible for men.
""")