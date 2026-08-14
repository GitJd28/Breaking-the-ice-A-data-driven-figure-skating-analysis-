import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from components.styles import load_css, apply_theme, PLOTLY_THEME
st.markdown(load_css(), unsafe_allow_html=True)
from components.data_loader import (
    load_aggregate, load_long,
    MEDAL_COLORS, COLORS, TRADITIONAL_NATIONS
)

# ── Load Data ────────────────────────────────
df_raw, df_clean = load_aggregate()
df_long = load_long()

st.title("🌍 Overview — The Global Picture")
st.markdown("---")


# ROW 1: Big Metrics
medal_avg    = df_clean[df_clean['medal'] > 0]['total_tss'].mean()
no_medal_avg = df_clean[df_clean['medal'] == 0]['total_tss'].mean()
gap          = medal_avg - no_medal_avg
nations      = df_raw['nation'].nunique()
india_rows   = len(df_raw[df_raw['nation'] == 'IND'])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Nations Represented", f"{nations}")
c2.metric("Medalist Avg Score",  f"{medal_avg:.1f}")
c3.metric("Non-Medalist Avg",    f"{no_medal_avg:.1f}")
c4.metric("Score Gap",           f"{gap:.1f} pts",
          delta="Medalists lead", delta_color="normal")

st.markdown("---")

# ROW 2: India Callout
st.error(
    f"🇮🇳 **India has {india_rows} appearances** in "
    f"20 years of Olympic Figure Skating data "
    f"(2006–2026). Across {nations} nations that "
    f"have participated, India has never qualified "
    f"a single skater."
)


# ROW 3: Nation Dominance

st.subheader("📊 Which Nations Dominate?")
col_left, col_right = st.columns(2)

# ── Chart 1: Appearances by nation ───────────
with col_left:
    st.markdown("**Olympic Appearances (Top 15 Nations)**")

    nation_counts = (
        df_raw['nation']
        .value_counts()
        .head(15)
        .reset_index()
    )
    nation_counts.columns = ['nation', 'appearances']

    fig_apps = px.bar(
        nation_counts,
        x='appearances',
        y='nation',
        orientation='h',
        color='appearances',
        color_continuous_scale='Blues',
    )
    fig_apps.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=500,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Number of Athletes",
        yaxis_title="",
    ) 
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_apps, use_container_width=True)


# ── Chart 2: Medal count by nation ───────────
with col_right:
    st.markdown("**Medal Count by Nation**")

    medal_df = df_raw[df_raw['medal'] > 0].copy()

    if len(medal_df) > 0:
        medal_counts = (
            medal_df.groupby(['nation', 'medal_label'])
            .size()
            .reset_index(name='count')
        )

        # Get total medals per nation for ordering
        nation_totals = (
            medal_counts.groupby('nation')['count']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .index.tolist()
        )

        medal_counts = medal_counts[
            medal_counts['nation'].isin(nation_totals)
        ]

        color_map = {
            'Gold'  : MEDAL_COLORS['Gold'],
            'Silver': MEDAL_COLORS['Silver'],
            'Bronze': MEDAL_COLORS['Bronze'],
        }

        fig_medals = px.bar(
            medal_counts,
            x='count',
            y='nation',
            color='medal_label',
            orientation='h',
            color_discrete_map=color_map,
            category_orders={
                'medal_label': ['Gold', 'Silver', 'Bronze'],
                'nation'     : nation_totals[::-1],
            },
        )
        fig_medals.update_layout(
            height=500,
            xaxis_title="Number of Medals",
            yaxis_title="",
            legend_title="Medal",
        )
        fig = apply_theme(fig, height=450, title="Your Title Here")
        st.plotly_chart(fig_medals, use_container_width=True)

st.markdown("---")


# ROW 4: Score Distributions
st.subheader("📈 Score Distributions: Medalists vs Non-Medalists")

gender_filter = st.radio(
    "Select Gender:",
    ['Both', 'Men', 'Women'],
    horizontal=True
)

if gender_filter == 'Men':
    df_filtered = df_clean[df_clean['gender'] == 'M']
elif gender_filter == 'Women':
    df_filtered = df_clean[df_clean['gender'] == 'W']
else:
    df_filtered = df_clean.copy()

col_tss, col_breakdown = st.columns(2)

# ── Chart 3: Total Score Distribution ────────
with col_tss:
    st.markdown("**Total Score (TSS) Distribution**")

    fig_dist = go.Figure()

    for medal_type in ['No Medal', 'Gold', 'Silver', 'Bronze']:
        subset = df_filtered[
            df_filtered['medal_label'] == medal_type
        ]['total_tss']

        if len(subset) > 0:
            fig_dist.add_trace(go.Histogram(
                x=subset,
                name=medal_type,
                marker_color=MEDAL_COLORS[medal_type],
                opacity=0.7,
                nbinsx=20,
            ))

    fig_dist.update_layout(
        barmode='overlay',
        height=400,
        xaxis_title="Total Score (TSS)",
        yaxis_title="Count",
        legend_title="Medal Status",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_dist, use_container_width=True)

# ── Chart 4: TES vs PCS ─────────────────────
with col_breakdown:
    st.markdown("**Technical (TES) vs Artistic (PCS)**")

    fig_scatter = go.Figure()

    for medal_type in ['No Medal', 'Bronze', 'Silver', 'Gold']:
        subset = df_filtered[
            df_filtered['medal_label'] == medal_type
        ]
        size = 15 if medal_type == 'No Medal' else 20
        symbol = 'circle' if medal_type == 'No Medal' \
                 else 'star'

        if len(subset) > 0:
            fig_scatter.add_trace(go.Scatter(
                x=subset['tes_total'],
                y=subset['pcs_total'],
                mode='markers',
                name=medal_type,
                marker=dict(
                    color=MEDAL_COLORS[medal_type],
                    size=size,
                    symbol=symbol,
                    line=dict(width=0.5, color='white'),
                    opacity=0.8 if medal_type != 'No Medal'
                            else 0.4,
                ),
            ))

    # Add TES=PCS diagonal line
    min_v = min(df_filtered['tes_total'].min(),
                df_filtered['pcs_total'].min())
    max_v = max(df_filtered['tes_total'].max(),
                df_filtered['pcs_total'].max())
    fig_scatter.add_trace(go.Scatter(
        x=[min_v, max_v],
        y=[min_v, max_v],
        mode='lines',
        name='TES = PCS',
        line=dict(dash='dash', color='gray', width=1),
    ))

    fig_scatter.update_layout(
        height=400,
        xaxis_title="Technical Score (TES)",
        yaxis_title="Program Components (PCS)",
        legend_title="Medal Status",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ROW 5: Trends Over Time
st.subheader("📅 Score Trends Across Olympic Games (2006–2026)")
metric_choice = st.selectbox(
    "Select Metric:",
    ['total_tss', 'tes_total', 'pcs_total',
     'tech_dominance_pct'],
    format_func=lambda x: {
        'total_tss'          : 'Total Score (TSS)',
        'tes_total'          : 'Technical Score (TES)',
        'pcs_total'          : 'Program Components (PCS)',
        'tech_dominance_pct' : 'TES Dominance Ratio',
    }[x]
)

fig_trend = go.Figure()

for gender_code, gender_name, color in [
    ('M', 'Men',   COLORS['accent']),
    ('W', 'Women', COLORS['no_medal'])
]:
    # All athletes
    trend_all = (
        df_clean[df_clean['gender'] == gender_code]
        .groupby('year')[metric_choice]
        .mean()
        .reset_index()
    )
    fig_trend.add_trace(go.Scatter(
        x=trend_all['year'],
        y=trend_all[metric_choice],
        mode='lines+markers',
        name=f'{gender_name} (All)',
        line=dict(color=color, width=2),
        marker=dict(size=6),
        opacity=0.6,
    ))

    # Medalists only
    trend_med = (
        df_clean[
            (df_clean['gender'] == gender_code) &
            (df_clean['medal'] > 0)
        ]
        .groupby('year')[metric_choice]
        .mean()
        .reset_index()
    )
    fig_trend.add_trace(go.Scatter(
        x=trend_med['year'],
        y=trend_med[metric_choice],
        mode='lines+markers',
        name=f'{gender_name} (Medalists)',
        line=dict(color=color, width=3, dash='dash'),
        marker=dict(size=10, symbol='star'),
    ))

fig_trend.update_layout(
    height=450,
    xaxis_title="Olympic Year",
    yaxis_title=metric_choice,
    legend_title="Group",
    xaxis=dict(
        tickmode='array',
        tickvals=df_clean['year'].unique()
    ),
)
fig = apply_theme(fig, height=450, title="Your Title Here")
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# ROW 6: Traditional vs Emerging Nations
# ─────────────────────────────────────────────

st.subheader("🌐 Traditional Powers vs Emerging Nations")

df_clean['nation_type'] = df_clean['nation'].apply(
    lambda x: 'Traditional Power'
    if x in TRADITIONAL_NATIONS
    else 'Emerging Nation'
)

col_box, col_stats = st.columns([2, 1])

with col_box:
    fig_box = px.box(
        df_clean,
        x='nation_type',
        y='total_tss',
        color='nation_type',
        color_discrete_map={
            'Traditional Power': COLORS['accent'],
            'Emerging Nation'  : COLORS['no_medal'],
        },
        points='all',
    )
    fig_box.update_layout(
        height=400,
        xaxis_title="",
        yaxis_title="Total Score (TSS)",
        showlegend=False,
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_box, use_container_width=True)

with col_stats:
    trad_avg = df_clean[
        df_clean['nation_type'] == 'Traditional Power'
    ]['total_tss'].mean()
    emrg_avg = df_clean[
        df_clean['nation_type'] == 'Emerging Nation'
    ]['total_tss'].mean()
    gap_nations = trad_avg - emrg_avg

    st.metric("Traditional Power Avg", f"{trad_avg:.1f}")
    st.metric("Emerging Nation Avg",   f"{emrg_avg:.1f}")
    st.metric("Gap", f"{gap_nations:.1f} pts",
              delta="Traditional leads",
              delta_color="normal")

    st.markdown("---")

    trad_medals = df_clean[
        (df_clean['nation_type'] == 'Traditional Power')
        & (df_clean['medal'] > 0)
    ].shape[0]
    emrg_medals = df_clean[
        (df_clean['nation_type'] == 'Emerging Nation')
        & (df_clean['medal'] > 0)
    ].shape[0]
    total_medals = trad_medals + emrg_medals

    st.metric("Traditional Medals",
              f"{trad_medals}/{total_medals}")
    st.metric("Emerging Medals",
              f"{emrg_medals}/{total_medals}")

st.markdown("---")

# ── Key Takeaway ─────────────────────────────
st.success("""
**📌 Key Takeaway from Overview:**

Figure skating is dominated by a small group of
traditional powers (JPN, USA, CAN, RUS). The average
score gap between medalists and non-medalists is
**~90 points** — a structural barrier.

However, emerging nations ARE participating, and
Kazakhstan's 2026 gold proves breakthrough is possible.

**India has never participated** — but understanding
what it takes is the first step toward changing that.
""")