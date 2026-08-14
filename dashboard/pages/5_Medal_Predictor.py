import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

sys.path.append( os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.styles import load_css, apply_theme, PLOTLY_THEME
st.markdown(load_css(), unsafe_allow_html=True)
from components.data_loader import (
    load_aggregate, load_models,
    FEATURES, COLORS, MEDAL_COLORS
)

df_raw, df_clean = load_aggregate()
rf_model, lr_model, scaler = load_models()

st.title("🤖 Medal Predictor — Interactive Model")
st.markdown("---")

# ROW 1: Model Performance Summary

st.subheader("📊 Model Performance")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Model", "Random Forest")
m2.metric("ROC-AUC (CV)", "0.990")
m3.metric("ROC-AUC (Test)", "0.983")
m4.metric("Class Balance", "Balanced Weights")

st.markdown("---")

# ROW 2: Feature Importance

st.subheader("🔑 What Predicts a Medal?")

col_imp, col_explain = st.columns([2, 1])

with col_imp:
    importance_df = pd.DataFrame({
        'Feature'   : FEATURES,
        'Importance': rf_model.feature_importances_,
    }).sort_values('Importance', ascending=True)

    fig_imp = px.bar(
        importance_df,
        x='Importance',
        y='Feature',
        orientation='h',
        color='Importance',
        color_continuous_scale='Reds',
    )
    fig_imp.update_layout(
        height=450,
        xaxis_title="Importance Score",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    fig = apply_theme(fig, height=450, title="Your Title Here")
    st.plotly_chart(fig_imp, use_container_width=True)

with col_explain:
    st.markdown("**Feature Explanation**")
    st.markdown("""
    | Feature | What It Means |
    |---------|---------------|
    | `sp_rank` | Rank after Short Program |
    | `total_tss` | Total combined score |
    | `pcs_total` | Artistic/presentation score |
    | `tes_total` | Technical elements score |
    | `score_momentum` | FS score minus SP score |
    | `rank_change` | SP rank minus FS rank |
    | `tes_pcs_ratio` | Technical vs artistic balance |
    | `tech_dominance_pct` | % of score from TES |
    | `gender_encoded` | Men=1, Women=0 |
    | `year` | Olympic year |
    """)

st.markdown("---")

# ROW 3: Interactive Predictor

st.subheader("🎛️ Try It Yourself! Enter Scores")
st.markdown(
    "Adjust the sliders to simulate any skater's "
    "performance and see their medal probability."
)

col_inputs, col_results = st.columns([1, 1])

with col_inputs:
    gender = st.radio(
        "Gender:",
        ['Men', 'Women'],
        horizontal=True
    )

    gender_code = 1 if gender == 'Men' else 0

    if gender == 'Men':
        tss_range = (100.0, 340.0, 200.0)
        tes_range = (40.0, 200.0, 110.0)
        pcs_range = (40.0, 150.0, 90.0)
    else:
        tss_range = (80.0, 260.0, 150.0)
        tes_range = (30.0, 150.0, 80.0)
        pcs_range = (30.0, 120.0, 70.0)

    total_tss = st.slider(
        "Total Score (TSS)",
        min_value=tss_range[0],
        max_value=tss_range[1],
        value=tss_range[2],
        step=1.0
    )

    tes_total = st.slider(
        "Technical Score (TES)",
        min_value=tes_range[0],
        max_value=tes_range[1],
        value=tes_range[2],
        step=1.0
    )

    pcs_total = st.slider(
        "Program Components (PCS)",
        min_value=pcs_range[0],
        max_value=pcs_range[1],
        value=pcs_range[2],
        step=1.0
    )

    sp_rank = st.slider(
        "Short Program Rank",
        min_value=1,
        max_value=30,
        value=10,
        step=1
    )

    # Derived features
    tech_dom    = tes_total / (tes_total + pcs_total) \
                  if (tes_total + pcs_total) > 0 else 0.5
    momentum    = total_tss * 0.6 - total_tss * 0.4
    rank_change = max(0, sp_rank - 3)
    tes_pcs     = tes_total / pcs_total \
                  if pcs_total > 0 else 1.0

with col_results:
    input_data = pd.DataFrame([{
        'total_tss'         : total_tss,
        'tes_total'         : tes_total,
        'pcs_total'         : pcs_total,
        'tech_dominance_pct': tech_dom,
        'sp_rank'           : sp_rank,
        'score_momentum'    : momentum,
        'rank_change'       : rank_change,
        'tes_pcs_ratio'     : tes_pcs,
        'gender_encoded'    : gender_code,
        'year'              : 2028,
    }])

    input_scaled = scaler.transform(input_data)
    rf_prob = rf_model.predict_proba(input_scaled)[0][1]
    lr_prob = lr_model.predict_proba(input_scaled)[0][1]

    # Color + emoji based on probability
    if rf_prob >= 0.70:
        color   = '#00C878'
        emoji   = '🥇'
        verdict = 'MEDAL LIKELY'
        detail  = 'This performance is in medal territory.'
    elif rf_prob >= 0.40:
        color   = '#F39C12'
        emoji   = '🎯'
        verdict = 'PODIUM POSSIBLE'
        detail  = 'Strong performance, needs clean Free Skate.'
    elif rf_prob >= 0.15:
        color   = '#00D4FF'
        emoji   = '📈'
        verdict = 'COMPETITIVE'
        detail  = 'In the field but outside medal range.'
    else:
        color   = '#E74C3C'
        emoji   = '🚀'
        verdict = 'DEVELOPMENT STAGE'
        detail  = 'Significant gap to Olympic medal level.'

    # Big probability display
    st.markdown(f"""
    <div class='prob-display'>
        <div style='font-size: 3rem;'>{emoji}</div>
        <div class='prob-number' style='color: {color};'>
            {rf_prob*100:.1f}%
        </div>
        <div style='color: {color}; font-weight: 700;
                    font-size: 1rem; margin-top: 8px;
                    letter-spacing: 0.1em;'>
            {verdict}
        </div>
        <div class='prob-label'>{detail}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = rf_prob * 100,
        number = dict(
            suffix    = '%',
            font      = dict(
                color = color, size=36
            )
        ),
        gauge = dict(
            axis  = dict(
                range    = [0, 100],
                tickfont = dict(color='#7FB3D3'),
            ),
            bar   = dict(color=color, thickness=0.7),
            bgcolor = 'rgba(15,32,64,0.8)',
            borderwidth = 0,
            steps = [
                {'range': [0,  15],  'color': 'rgba(231,76,60,0.15)'},
                {'range': [15, 40],  'color': 'rgba(243,156,18,0.15)'},
                {'range': [40, 70],  'color': 'rgba(0,212,255,0.15)'},
                {'range': [70, 100], 'color': 'rgba(0,200,120,0.15)'},
            ],
            threshold = dict(
                line      = dict(color='white', width=2),
                thickness = 0.8,
                value     = 50,
            ),
        ),
    ))

    fig_gauge = apply_theme(fig_gauge, height=260)
    fig_gauge.update_layout(
        margin = dict(t=20, b=0, l=20, r=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Model comparison
    col_rf, col_lr = st.columns(2)
    col_rf.metric("Random Forest",       f"{rf_prob*100:.1f}%")
    col_lr.metric("Logistic Regression", f"{lr_prob*100:.1f}%")

    # What's holding this score back
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header' style='font-size:0.9rem;'>"
        "💡 What Would Improve This Score?</div>",
        unsafe_allow_html=True
    )

    if sp_rank > 3:
        st.markdown(f"""
        <div class='ice-card' style='padding:12px 16px;'>
            <p>🎯 <strong style='color:#00D4FF;'>
            Improve SP rank from #{sp_rank} to top 3
            </strong> — SP rank is 53.8% of medal prediction.
            This is the single biggest lever.</p>
        </div>
        """, unsafe_allow_html=True)

    if total_tss < (275 if gender_code == 1 else 220):
        gap = (275 if gender_code == 1 else 220) - total_tss
        st.markdown(f"""
        <div class='ice-card' style='padding:12px 16px;'>
            <p>📊 <strong style='color:#00D4FF;'>
            Score needs +{gap:.0f} points
            </strong> to reach medal threshold
            ({275 if gender_code == 1 else 220} pts).</p>
        </div>
        """, unsafe_allow_html=True)

    if tes_total / (total_tss + 0.001) < 0.52:
        st.markdown("""
        <div class='ice-card' style='padding:12px 16px;'>
            <p>⚡ <strong style='color:#00D4FF;'>
            Increase technical content (TES)
            </strong> — modern medals require
            TES to be 52-57% of total score.</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ROW 4: Preset Scenarios

st.subheader("📋 Preset Scenarios — Quick Comparisons")

scenarios = [
    {
        'label': '🥇 2026 Gold (Men — Shaidorov)',
        'total_tss': 291.58, 'tes_total': 167.13,
        'pcs_total': 124.45, 'tech_dominance_pct': 0.5732,
        'sp_rank': 5, 'score_momentum': 105.7,
        'rank_change': 4.0, 'tes_pcs_ratio': 1.343,
        'gender_encoded': 1, 'year': 2026,
    },
    {
        'label': '🇮🇳 India Tier 1 (Men — Just Qualify)',
        'total_tss': 150, 'tes_total': 80,
        'pcs_total': 70, 'tech_dominance_pct': 0.533,
        'sp_rank': 25, 'score_momentum': 20,
        'rank_change': 2, 'tes_pcs_ratio': 1.14,
        'gender_encoded': 1, 'year': 2028,
    },
    {
        'label': '🇮🇳 India Tier 3 (Men — Near Medal)',
        'total_tss': 240, 'tes_total': 135,
        'pcs_total': 105, 'tech_dominance_pct': 0.562,
        'sp_rank': 8, 'score_momentum': 40,
        'rank_change': 5, 'tes_pcs_ratio': 1.29,
        'gender_encoded': 1, 'year': 2028,
    },
    {
        'label': '🇮🇳 India Tier 4 (Men — Medal Contention)',
        'total_tss': 275, 'tes_total': 155,
        'pcs_total': 120, 'tech_dominance_pct': 0.563,
        'sp_rank': 3, 'score_momentum': 50,
        'rank_change': 8, 'tes_pcs_ratio': 1.29,
        'gender_encoded': 1, 'year': 2028,
    },
]

scenario_results = []
for scenario in scenarios:
    label = scenario.pop('label')
    input_df = pd.DataFrame([scenario])
    input_sc = scaler.transform(input_df)
    prob = rf_model.predict_proba(input_sc)[0][1]
    scenario_results.append({
        'Scenario': label,
        'Score': scenario['total_tss'],
        'SP Rank': scenario['sp_rank'],
        'Medal Prob': f"{prob*100:.1f}%",
        'Assessment': (
            '🥇 Medal Likely'    if prob > 0.70 else
            '🎯 Podium Possible' if prob > 0.40 else
            '📈 Competitive'     if prob > 0.15 else
            '🚀 Development'
        ),
    })
    scenario['label'] = label

results_df = pd.DataFrame(scenario_results)
st.dataframe(
    results_df,
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# ── Takeaway ─────────────────────────────────

st.success("""
**📌 Model Insights:**

1. **SP Rank dominates** — at 53.8% feature importance,
   your Short Program placement is the strongest
   predictor of a medal.

2. **Model achieves 0.983 AUC** — extremely reliable
   at distinguishing medal contenders from the field.

3. **The threshold effect** — medal probability jumps
   dramatically when scores cross ~275 (Men) or
   ~220 (Women) with a top-3 SP rank.

4. **For India** — the model shows a realistic
   progression path from Tier 1 (0.1%) to
   Tier 4 (73%) medal probability.
""")