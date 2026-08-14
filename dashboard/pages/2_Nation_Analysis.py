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

st.set_page_config(page_title="Nation Analysis", page_icon="🏳️", layout="wide")
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

# Header
st.markdown(
    "<div class='page-title'>🏳️ Nation Analysis — Deep Dive</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='page-subtitle'>"
    "Explore any nation's performance, compare head-to-head, "
    "and discover each country's skating style."
    "</div>",
    unsafe_allow_html=True
)

# Nation selectors
all_nations = sorted(df_clean['nation'].unique().tolist())

col_s1, col_s2 = st.columns(2)
with col_s1:
    selected_nation = st.selectbox(
        "Select a nation:",
        all_nations,
        index=all_nations.index('JPN') if 'JPN' in all_nations else 0
    )
with col_s2:
    compare_nation = st.selectbox(
        "Compare with:",
        ['All Nations Average'] + all_nations,
        index=0
    )

nation_data   = df_clean[df_clean['nation'] == selected_nation]
nation_medals = nation_data[nation_data['medal'] > 0]

st.markdown("<br>", unsafe_allow_html=True)

# Stat row
s1, s2, s3, s4, s5 = st.columns(5)
stats = [
    (f"{nation_data['skater'].nunique()}", "Athletes", "Unique"),
    (f"{len(nation_data)}", "Appearances", "Total"),
    (f"{len(nation_medals)}", "Medals", "Won"),
    (f"{nation_data['total_tss'].mean():.0f}", "Avg Score", "TSS"),
    (f"{nation_data['total_tss'].max():.0f}", "Best Score", "TSS"),
]
for col, (num, lbl, sub) in zip([s1, s2, s3, s4, s5], stats):
    with col:
        st.markdown(f"""
        <div class='stat-card-blue'>
            <div class='num'>{num}</div>
            <div class='lbl'>{lbl}</div>
            <div class='sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Score trend + athlete table
st.markdown(
    f"<div class='section-title'>"
    f"📈 {selected_nation} — Score Trends</div>",
    unsafe_allow_html=True
)

col_trend, col_table = st.columns([2, 1])

with col_trend:
    fig_trend = go.Figure()

    for g, name, color in [
        ('M', 'Men',   CHART_COLORS['primary']),
        ('W', 'Women', CHART_COLORS['accent'])
    ]:
        gd = nation_data[nation_data['gender'] == g].sort_values('year')
        if len(gd) > 0:
            trend = gd.groupby('year')['total_tss'].mean().reset_index()
            fig_trend.add_trace(go.Scatter(
                x=trend['year'], y=trend['total_tss'],
                mode='lines+markers', name=name,
                line=dict(color=color, width=2.5),
                marker=dict(size=8),
            ))
            medals_g = gd[gd['medal'] > 0]
            if len(medals_g) > 0:
                fig_trend.add_trace(go.Scatter(
                    x=medals_g['year'], y=medals_g['total_tss'],
                    mode='markers', name=f'{name} Medals',
                    marker=dict(
                        color=CHART_COLORS['gold'], size=16,
                        symbol='star',
                        line=dict(width=1, color='black'),
                    ),
                ))

    global_avg = df_clean.groupby('year')['total_tss'].mean().reset_index()
    fig_trend.add_trace(go.Scatter(
        x=global_avg['year'], y=global_avg['total_tss'],
        mode='lines', name='Global Average',
        line=dict(color='gray', width=1.5, dash='dot'),
        opacity=0.5,
    ))

    fig_trend.update_layout(
        xaxis_title="Olympic Year", yaxis_title="Average Total Score",
        title=f"{selected_nation} Performance Over Time",
        xaxis=dict(tickmode='array', tickvals=df_clean['year'].unique()),
    )
    fig_trend = apply_theme(fig_trend, height=450)
    st.plotly_chart(fig_trend, use_container_width=True)

with col_table:
    st.markdown(f"**{selected_nation} Athletes**")
    athletes = (
        nation_data.groupby('skater')
        .agg(
            Apps=('year', 'count'),
            Best=('total_tss', 'max'),
            Medals=('is_medal', 'sum'),
        )
        .sort_values('Best', ascending=False)
        .reset_index()
    )
    athletes.columns = ['Skater', 'Apps', 'Best Score', 'Medals']
    st.dataframe(athletes, use_container_width=True, hide_index=True, height=420)

st.markdown("<br>", unsafe_allow_html=True)

# TES vs PCS style
st.markdown(
    "<div class='section-title'>"
    "🎯 Technical vs Artistic — Nation Style</div>",
    unsafe_allow_html=True
)

col_style, col_explain = st.columns([2, 1])

with col_style:
    top_nations = df_clean['nation'].value_counts().head(10).index.tolist()
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
        x='avg_tes', y='avg_pcs',
        size='avg_score', color='medals',
        text='nation',
        color_continuous_scale='Blues',
        size_max=40,
    )
    fig_style.update_traces(textposition='top center')

    min_v = min(style_data['avg_tes'].min(), style_data['avg_pcs'].min()) - 5
    max_v = max(style_data['avg_tes'].max(), style_data['avg_pcs'].max()) + 5
    fig_style.add_trace(go.Scatter(
        x=[min_v, max_v], y=[min_v, max_v],
        mode='lines', name='TES = PCS',
        line=dict(dash='dash', color='gray', width=1),
    ))

    fig_style.update_layout(
        xaxis_title="Avg Technical Score (TES)",
        yaxis_title="Avg Program Components (PCS)",
        title="Nation Skating Styles",
    )
    fig_style = apply_theme(fig_style, height=450)
    st.plotly_chart(fig_style, use_container_width=True)

with col_explain:
    if len(nation_data) > 0:
        avg_tes = nation_data['tes_total'].mean()
        avg_pcs = nation_data['pcs_total'].mean()
        ratio = avg_tes / avg_pcs if avg_pcs > 0 else 0

        st.metric(f"{selected_nation} Avg TES", f"{avg_tes:.1f}")
        st.metric(f"{selected_nation} Avg PCS", f"{avg_pcs:.1f}")
        st.metric("TES/PCS Ratio", f"{ratio:.3f}")

        if ratio > 1.05:
            st.info(
                f"**{selected_nation}** leans toward a "
                f"**technically dominant** style."
            )
        elif ratio < 0.95:
            st.info(
                f"**{selected_nation}** leans toward an "
                f"**artistically dominant** style."
            )
        else:
            st.info(
                f"**{selected_nation}** has a **balanced** approach."
            )

st.markdown("<br>", unsafe_allow_html=True)

# Head to head
st.markdown(
    f"<div class='section-title'>"
    f"⚔️ {selected_nation} vs {compare_nation}</div>",
    unsafe_allow_html=True
)

if compare_nation == 'All Nations Average':
    compare_data = df_clean.copy()
    compare_label = "All Nations Avg"
else:
    compare_data = df_clean[df_clean['nation'] == compare_nation]
    compare_label = compare_nation

metrics = [
    ('total_tss', 'Total Score'),
    ('tes_total', 'Technical'),
    ('pcs_total', 'Artistic'),
    ('tech_dominance_pct', 'TES Dominance'),
]

mc = st.columns(len(metrics))
for col, (m, label) in zip(mc, metrics):
    val_s = nation_data[m].mean()
    val_c = compare_data[m].mean()
    diff  = val_s - val_c
    col.metric(label, f"{val_s:.1f}", delta=f"{diff:+.1f} vs {compare_label}")

fig_comp = go.Figure()
for label, data, color in [
    (selected_nation, nation_data, CHART_COLORS['primary']),
    (compare_label, compare_data, CHART_COLORS['accent']),
]:
    t = data.groupby('year')['total_tss'].mean().reset_index()
    fig_comp.add_trace(go.Scatter(
        x=t['year'], y=t['total_tss'],
        mode='lines+markers', name=label,
        line=dict(color=color, width=2.5),
        marker=dict(size=8),
    ))
fig_comp.update_layout(
    xaxis_title="Year", yaxis_title="Avg Total Score",
    title=f"{selected_nation} vs {compare_label}",
    xaxis=dict(tickmode='array', tickvals=df_clean['year'].unique()),
)
fig_comp = apply_theme(fig_comp, height=400)
st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.success(
    f"📌 **{selected_nation}** has produced "
    f"**{nation_data['skater'].nunique()} athletes** across "
    f"**{nation_data['year'].nunique()} Olympic Games**, "
    f"winning **{len(nation_medals)} medals** with an "
    f"average score of **{nation_data['total_tss'].mean():.1f}**."
)