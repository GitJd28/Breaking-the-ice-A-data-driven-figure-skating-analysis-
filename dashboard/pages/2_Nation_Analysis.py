import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.styles import load_css, apply_theme, PLOTLY_THEME
st.markdown(load_css(), unsafe_allow_html=True)
from components.data_loader import (
    load_aggregate, load_long,
    MEDAL_COLORS, COLORS, TRADITIONAL_NATIONS
)

df_raw, df_clean = load_aggregate()
df_long = load_long()

st.title("🌍 Nation Analysis — Deep Dive")
st.markdown("---")

# ROW 1: Nation Selector

all_nations = sorted(df_clean['nation'].unique().tolist())

st.subheader("🔎 Explore Any Nation")

col_select, col_compare = st.columns(2)

with col_select:
    selected_nation = st.selectbox(
        "Select a nation to analyze:",
        all_nations,
        index=all_nations.index('JPN')
        if 'JPN' in all_nations else 0
    )

with col_compare:
    compare_nation = st.selectbox(
        "Compare with:",
        ['All Nations Average'] + all_nations,
        index=0
    )

st.markdown("---")

# ROW 2: Nation Profile Cards

nation_data   = df_clean[df_clean['nation'] == selected_nation]
nation_medals = nation_data[nation_data['medal'] > 0]

n1, n2, n3, n4, n5 = st.columns(5)

n1.metric("Athletes",
          f"{nation_data['skater'].nunique()}")
n2.metric("Total Appearances",
          f"{len(nation_data)}")
n3.metric("Medals Won",
          f"{len(nation_medals)}")
n4.metric("Avg Score",
          f"{nation_data['total_tss'].mean():.1f}")
n5.metric("Best Score",
          f"{nation_data['total_tss'].max():.1f}")

st.markdown("---")

# ROW 3: Nation Score Trends Over Time

st.subheader(
    f"📈 {selected_nation} — Score Trends Over Time"
)

col_trend, col_table = st.columns([2, 1])

with col_trend:
    fig_trend = go.Figure()

    for gender_code, gender_name, color in [
        ('M', 'Men',   COLORS['accent']),
        ('W', 'Women', COLORS['no_medal'])
    ]:
        gender_data = nation_data[
            nation_data['gender'] == gender_code
        ].sort_values('year')

        if len(gender_data) > 0:
            trend = (
                gender_data.groupby('year')['total_tss']
                .mean()
                .reset_index()
            )
            fig_trend.add_trace(go.Scatter(
                x=trend['year'],
                y=trend['total_tss'],
                mode='lines+markers',
                name=f'{gender_name}',
                line=dict(color=color, width=2.5),
                marker=dict(size=8),
            ))

            # Highlight medal performances
            medals_g = gender_data[gender_data['medal'] > 0]
            if len(medals_g) > 0:
                fig_trend.add_trace(go.Scatter(
                    x=medals_g['year'],
                    y=medals_g['total_tss'],
                    mode='markers',
                    name=f'{gender_name} Medals',
                    marker=dict(
                        color=MEDAL_COLORS['Gold'],
                        size=16,
                        symbol='star',
                        line=dict(width=1, color='black'),
                    ),
                ))

    # Add global average line
    global_avg = (
        df_clean.groupby('year')['total_tss']
        .mean()
        .reset_index()
    )
    fig_trend.add_trace(go.Scatter(
        x=global_avg['year'],
        y=global_avg['total_tss'],
        mode='lines',
        name='Global Average',
        line=dict(color='gray', width=1.5, dash='dot'),
        opacity=0.5,
    ))

    fig_trend.update_layout(
        height=450,
        xaxis_title="Olympic Year",
        yaxis_title="Average Total Score",
        xaxis=dict(
            tickmode='array',
            tickvals=df_clean['year'].unique()
        ),
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_table:
    st.markdown(f"**{selected_nation} Athletes**")

    athletes = (
        nation_data.groupby('skater')
        .agg(
            appearances=('year', 'count'),
            best_score=('total_tss', 'max'),
            medals=('is_medal', 'sum'),
            best_rank=('final_rank_num', 'min'),
        )
        .sort_values('best_score', ascending=False)
        .reset_index()
    )
    athletes.columns = [
        'Skater', 'Apps', 'Best Score', 'Medals', 'Best Rank'
    ]

    st.dataframe(
        athletes,
        use_container_width=True,
        hide_index=True,
        height=400,
    )

st.markdown("---")

# ROW 4: TES vs PCS by Nation Style

st.subheader("🎯 Technical (TES) vs Artistic (PCS) — Nation Style")
col_style, col_analysis = st.columns([2, 1])

with col_style:
    # Get top 10 nations by appearances
    top_nations = (
        df_clean['nation']
        .value_counts()
        .head(10)
        .index.tolist()
    )

    style_data = (
        df_clean[df_clean['nation'].isin(top_nations)]
        .groupby('nation')
        .agg(
            avg_tes=('tes_total', 'mean'),
            avg_pcs=('pcs_total', 'mean'),
            avg_score=('total_tss', 'mean'),
            medals=('is_medal', 'sum'),
        )
        .reset_index()
    )

    fig_style = px.scatter(
        style_data,
        x='avg_tes',
        y='avg_pcs',
        size='avg_score',
        color='medals',
        text='nation',
        color_continuous_scale='YlOrRd',
        size_max=40,
    )
    fig_style.update_traces(textposition='top center')

    # Add TES=PCS diagonal
    min_v = min(style_data['avg_tes'].min(),
                style_data['avg_pcs'].min()) - 5
    max_v = max(style_data['avg_tes'].max(),
                style_data['avg_pcs'].max()) + 5
    fig_style.add_trace(go.Scatter(
        x=[min_v, max_v],
        y=[min_v, max_v],
        mode='lines',
        name='TES = PCS',
        line=dict(dash='dash', color='gray', width=1),
        showlegend=True,
    ))

    fig_style.update_layout(
        height=500,
        xaxis_title="Average Technical Score (TES)",
        yaxis_title="Average Program Components (PCS)",
        coloraxis_colorbar_title="Medals",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_style, use_container_width=True)

with col_analysis:
    st.markdown("**Style Analysis**")

    nation_style = df_clean[
        df_clean['nation'] == selected_nation
    ]
    if len(nation_style) > 0:
        avg_tes = nation_style['tes_total'].mean()
        avg_pcs = nation_style['pcs_total'].mean()
        ratio   = avg_tes / avg_pcs if avg_pcs > 0 else 0

        st.metric(f"{selected_nation} Avg TES",
                  f"{avg_tes:.1f}")
        st.metric(f"{selected_nation} Avg PCS",
                  f"{avg_pcs:.1f}")
        st.metric("TES/PCS Ratio", f"{ratio:.3f}")

        st.markdown("---")

        if ratio > 1.05:
            st.info(
                f"**{selected_nation}** leans toward a "
                f"**technically dominant** style — "
                f"scoring more from jumps and spins "
                f"than artistry."
            )
        elif ratio < 0.95:
            st.info(
                f"**{selected_nation}** leans toward an "
                f"**artistically dominant** style — "
                f"scoring more from presentation "
                f"than technical elements."
            )
        else:
            st.info(
                f"**{selected_nation}** has a **balanced** "
                f"approach — technical and artistic scores "
                f"are roughly equal."
            )

st.markdown("---")

# ROW 5: Head to Head Comparison
st.subheader(
    f"⚔️ {selected_nation} vs "
    f"{compare_nation}"
)

if compare_nation == 'All Nations Average':
    compare_data = df_clean.copy()
    compare_label = "All Nations Avg"
else:
    compare_data = df_clean[
        df_clean['nation'] == compare_nation
    ]
    compare_label = compare_nation

metrics_compare = [
    ('total_tss', 'Total Score'),
    ('tes_total', 'Technical Score'),
    ('pcs_total', 'Program Components'),
    ('tech_dominance_pct', 'TES Dominance'),
]

comp_cols = st.columns(len(metrics_compare))

for col, (metric, label) in zip(comp_cols, metrics_compare):
    with col:
        val_selected = nation_data[metric].mean()
        val_compare  = compare_data[metric].mean()
        diff         = val_selected - val_compare

        col.metric(
            f"{label}",
            f"{val_selected:.2f}",
            delta=f"{diff:+.2f} vs {compare_label}",
            delta_color="normal"
        )

st.markdown("---")

# Comparison Chart 
fig_compare = go.Figure()

for label, data, color in [
    (selected_nation, nation_data, COLORS['accent']),
    (compare_label,   compare_data, COLORS['no_medal']),
]:
    trend = (
        data.groupby('year')['total_tss']
        .mean()
        .reset_index()
    )
    fig_compare.add_trace(go.Scatter(
        x=trend['year'],
        y=trend['total_tss'],
        mode='lines+markers',
        name=label,
        line=dict(color=color, width=2.5),
        marker=dict(size=8),
    ))

fig_compare.update_layout(
    height=400,
    xaxis_title="Olympic Year",
    yaxis_title="Average Total Score",
    title=f"Score Trend: {selected_nation} vs {compare_label}",
    xaxis=dict(
        tickmode='array',
        tickvals=df_clean['year'].unique()
    ),
)
fig = apply_theme(fig, height=450, title="Your Title Here")
st.plotly_chart(fig_compare, use_container_width=True)
st.markdown("---")

# Takeaway 
st.success(f"""
**📌 Key Takeaway — {selected_nation}:**

{selected_nation} has produced
**{nation_data['skater'].nunique()} athletes**
across **{nation_data['year'].nunique()} Olympic Games**,
winning **{len(nation_medals)} medals**.
Their average score is **{nation_data['total_tss'].mean():.1f}**
(global average: {df_clean['total_tss'].mean():.1f}).
""")
