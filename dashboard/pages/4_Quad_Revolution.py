import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

from components.styles import (
    load_css, apply_theme,
    CHART_COLORS, MEDAL_COLORS_LIGHT_LIGHT
)

st.set_page_config(page_title="Page Name", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
        <div class='icon'>⛸️</div>
        <div class='name'>Break the Ice</div>
        <div class='tag'>Figure Skating Analytics</div>
    </div>
    """, unsafe_allow_html=True)


sys.path.append(    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.styles import load_css, apply_theme, PLOTLY_THEME
st.markdown(load_css(), unsafe_allow_html=True)
from components.data_loader import (
    load_aggregate, load_long,
    MEDAL_COLORS_LIGHT, COLORS
)
df_raw, df_clean = load_aggregate()
df_long = load_long()
st.title("🧬 Performance DNA — What Wins Medals?")
st.markdown("---")

# ROW 1: Headline Finding
st.warning("""
**🔑 Headline Finding:**
Short Program rank alone explains **53.8%** of medal
prediction in our Random Forest model — more than
total score, technical score, or artistry combined.

**Where you stand after the Short Program is the
single most important factor in winning an Olympic medal.**
""")

st.markdown("---")

# ROW 2: SP Rank vs Final Rank
st.subheader("📋 Short Program Rank vs Final Rank")
st.markdown(
    "Does leading after the Short Program guarantee gold?"
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

col_scatter, col_insight = st.columns([2, 1])

with col_scatter:
    fig_sp = go.Figure()

    for medal_type in ['No Medal', 'Bronze', 'Silver', 'Gold']:
        subset = df_sp[df_sp['medal_label'] == medal_type]
        subset = subset.dropna(subset=['final_rank_num'])

        size = 8 if medal_type == 'No Medal' else 14
        symbol = 'circle' if medal_type == 'No Medal' \
                 else 'star'
        opacity = 0.3 if medal_type == 'No Medal' else 0.9

        if len(subset) > 0:
            fig_sp.add_trace(go.Scatter(
                x=subset['sp_rank'],
                y=subset['final_rank_num'],
                mode='markers',
                name=medal_type,
                marker=dict(
                    color=MEDAL_COLORS_LIGHT[medal_type],
                    size=size,
                    symbol=symbol,
                    opacity=opacity,
                    line=dict(width=0.5, color='white'),
                ),
                text=subset['skater'],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "SP Rank: %{x}<br>"
                    "Final Rank: %{y}<extra></extra>"
                ),
            ))

    # Perfect diagonal
    max_rank = int(df_sp['sp_rank'].max())
    fig_sp.add_trace(go.Scatter(
        x=list(range(1, max_rank + 1)),
        y=list(range(1, max_rank + 1)),
        mode='lines',
        name='SP = Final (no change)',
        line=dict(dash='dash', color='gray', width=1),
    ))

    fig_sp.update_layout(
        height=500,
        xaxis_title="Short Program Rank",
        yaxis_title="Final Rank",
        xaxis=dict(range=[0, 32], dtick=5),
        yaxis=dict(range=[0, 32], autorange='reversed'),
    )
    fig = apply_theme(fig, height=450)
    st.plotly_chart(fig_sp, use_container_width=True)

with col_insight:
    st.markdown("**SP → Gold Conversion**")

    sp1 = df_clean[df_clean['sp_rank'] == 1]
    sp1_gold = sp1[sp1['medal'] == 1]
    sp3 = df_clean[df_clean['sp_rank'] <= 3]
    sp3_medal = sp3[sp3['medal'] > 0]

    st.metric(
        "SP Rank 1 → Gold",
        f"{len(sp1_gold)}/{len(sp1)} "
        f"({len(sp1_gold)/max(len(sp1),1)*100:.0f}%)"
    )
    st.metric(
        "SP Top 3 → Any Medal",
        f"{len(sp3_medal)}/{len(sp3)} "
        f"({len(sp3_medal)/max(len(sp3),1)*100:.0f}%)"
    )

    st.markdown("---")

    # Comeback stories
    comebacks = df_clean[
        (df_clean['medal'] > 0) &
        (df_clean['sp_rank'] > 3)
    ].sort_values('sp_rank', ascending=False)

    if len(comebacks) > 0:
        st.markdown("**🔥 Biggest Comebacks**")
        st.markdown("*Medalists who ranked below 3rd after SP:*")
        for _, row in comebacks.head(5).iterrows():
            medal_emoji = {
                1: '🥇', 2: '🥈', 3: '🥉'
            }.get(row['medal'], '')

            st.markdown(
                f"- {medal_emoji} **{row['skater']}** "
                f"({row['nation']}, {int(row['year'])}): "
                f"SP #{int(row['sp_rank'])} → "
                f"Final #{int(row['final_rank_num'])}"
            )

st.markdown("---")

# ROW 3: Score Component Breakdown

st.subheader("📊 Score Anatomy — What Makes a Medal Score?")
col_bar, col_radar = st.columns(2)
with col_bar:
    st.markdown("**Average Score Breakdown by Medal Status**")
    breakdown = (
        df_clean.groupby('medal_label')
        .agg(
            TES_SP=('tes_sp', 'mean'),
            PCS_SP=('pcs_sp', 'mean'),
            TES_FS=('tes_fs', 'mean'),
            PCS_FS=('pcs_fs', 'mean'),
        )
        .reindex(['Gold', 'Silver', 'Bronze', 'No Medal'])
    )

    fig_bar = go.Figure()

    bar_colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']
    components = ['TES_SP', 'PCS_SP', 'TES_FS', 'PCS_FS']
    comp_labels = [
        'TES (Short)', 'PCS (Short)',
        'TES (Free)',  'PCS (Free)'
    ]

    for comp, label, color in zip(
        components, comp_labels, bar_colors
    ):
        fig_bar.add_trace(go.Bar(
            x=breakdown.index,
            y=breakdown[comp],
            name=label,
            marker_color=color,
        ))

    fig_bar.update_layout(
        barmode='stack',
        height=450,
        xaxis_title="Medal Status",
        yaxis_title="Score Points",
        legend_title="Score Component",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_radar:
    st.markdown("**Medal Profile — Normalized Comparison**")

    categories = [
        'TES (SP)', 'PCS (SP)',
        'TES (FS)', 'PCS (FS)',
        'Score Momentum'
    ]

    fig_radar = go.Figure()

    for medal_type, color in [
        ('Gold',     MEDAL_COLORS_LIGHT['Gold']),
        ('No Medal', MEDAL_COLORS_LIGHT['No Medal'])
    ]:
        subset = df_clean[
            df_clean['medal_label'] == medal_type
        ]
        if len(subset) > 0:
            # Normalize to 0-1 scale
            values = [
                subset['tes_sp'].mean()
                / df_clean['tes_sp'].max(),
                subset['pcs_sp'].mean()
                / df_clean['pcs_sp'].max(),
                subset['tes_fs'].mean()
                / df_clean['tes_fs'].max(),
                subset['pcs_fs'].mean()
                / df_clean['pcs_fs'].max(),
                subset['score_momentum'].mean()
                / df_clean['score_momentum'].max(),
            ]
            # Close the radar
            values.append(values[0])

            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=medal_type,
                line=dict(color=color, width=2),
                opacity=0.6,
            ))

    fig_radar.update_layout(
        height=450,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        legend=dict(x=0.8, y=1.1),
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# ROW 4: Deduction Analysis

st.subheader("⚠️ Deduction Analysis — Do Falls Cost Medals?")
# Merge long with medal info
df_long_medal = df_long.merge(
    df_clean[['year', 'gender', 'skater',
              'medal', 'medal_label']],
    on=['year', 'gender', 'skater'],
    how='left'
)
df_long_medal['medal_label'] = ( df_long_medal['medal_label'].fillna('No Medal'))

col_ded1, col_ded2 = st.columns(2)
with col_ded1:
    st.markdown(
        "**% of Segments With Deductions by Medal Status**"
    )

    ded_pct = (
        df_long_medal.groupby('medal_label')['has_deduction']
        .mean()
        .reindex(['Gold', 'Silver', 'Bronze', 'No Medal'])
        * 100
    ).reset_index()
    ded_pct.columns = ['Medal Status', 'Deduction %']

    fig_ded = px.bar(
        ded_pct,
        x='Medal Status',
        y='Deduction %',
        color='Medal Status',
        color_discrete_map=MEDAL_COLORS_LIGHT,
        text='Deduction %',
    )
    fig_ded.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    fig_ded.update_layout(
        height=400,
        showlegend=False,
        yaxis_title="% of Segments",
        yaxis=dict(range=[0, ded_pct['Deduction %'].max() * 1.3]),
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_ded, use_container_width=True)

with col_ded2:
    st.markdown(
        "**Average Deduction by Segment**"
    )

    ded_avg = (
        df_long_medal.groupby(
            ['segment', 'medal_label']
        )['ded']
        .mean()
        .reset_index()
    )
    ded_avg = ded_avg[
        ded_avg['medal_label'].isin(
            ['Gold', 'Silver', 'Bronze', 'No Medal']
        )
    ]

    fig_ded2 = px.bar(
        ded_avg,
        x='segment',
        y='ded',
        color='medal_label',
        barmode='group',
        color_discrete_map=MEDAL_COLORS_LIGHT,
    )
    fig_ded2.update_layout(
        height=400,
        xaxis_title="Segment",
        yaxis_title="Avg Deduction Points",
        legend_title="Medal Status",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_ded2, use_container_width=True)

st.markdown("---")

# ROW 5: Rank Change Distribution

st.subheader("🔄 Rank Change — SP to Final")
st.markdown(
    "*Positive = improved position in Free Skate. "
    "Negative = dropped.*"
)

col_hist, col_stats = st.columns([2, 1])
with col_hist:
    fig_rank = go.Figure()

    for medal_type in ['No Medal', 'Gold']:
        subset = df_clean[
            df_clean['medal_label'] == medal_type
        ]['rank_change']

        fig_rank.add_trace(go.Histogram(
            x=subset,
            name=medal_type,
            marker_color=MEDAL_COLORS_LIGHT[medal_type],
            opacity=0.7,
            nbinsx=25,
        ))

    fig_rank.add_vline(
        x=0, line_dash="dash",
        line_color="gray",
        annotation_text="No Change"
    )

    fig_rank.update_layout(
        barmode='overlay',
        height=400,
        xaxis_title="Rank Change (SP → Final)",
        yaxis_title="Count",
        legend_title="Medal Status",
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_rank, use_container_width=True)

with col_stats:
    st.markdown("**Rank Change Statistics**")

    for medal_type in ['Gold', 'Silver', 'Bronze', 'No Medal']:
        subset = df_clean[
            df_clean['medal_label'] == medal_type
        ]['rank_change']
        emoji = {
            'Gold': '🥇', 'Silver': '🥈',
            'Bronze': '🥉', 'No Medal': '🔵'
        }[medal_type]
        st.markdown(
            f"{emoji} **{medal_type}**: "
            f"avg {subset.mean():+.1f} | "
            f"range [{subset.min():.0f}, "
            f"{subset.max():.0f}]"
        )

    st.markdown("---")
    st.markdown("**Interpretation:**")

    gold_avg = df_clean[
        df_clean['medal'] == 1
    ]['rank_change'].mean()

    if gold_avg > 0:
        st.info(
            f"Gold medalists improve on average "
            f"**{gold_avg:.1f} positions** from "
            f"SP to Final — showing strong "
            f"Free Skate execution under pressure."
        )
    else:
        st.info(
            f"Gold medalists maintain or slightly "
            f"adjust their position ({gold_avg:+.1f}), "
            f"showing consistency across both programs."
        )

st.markdown("---")

# Key Takeaway 
st.success("""
**📌 Performance DNA Summary:**

1. **SP Rank is King** — 53.8% of medal prediction
   power. A strong Short Program sets up everything.

2. **Score Structure** — Medalists excel in ALL four
   components (TES SP, PCS SP, TES FS, PCS FS),
   but the biggest gap is in Free Skate TES.

3. **Deductions** — Medal winners have significantly
   fewer deductions. Clean programs win medals.

4. **Comeback Potential** — While SP rank dominates,
   some champions have come from behind, proving
   the Free Skate can rewrite the story.
""")