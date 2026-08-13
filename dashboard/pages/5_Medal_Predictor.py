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
    load_aggregate, load_models,
    FEATURES, COLORS, MEDAL_COLORS
)

df_raw, df_clean = load_aggregate()
rf_model, lr_model, scaler = load_models()

st.title("🤖 Medal Predictor — Interactive Model")
st.markdown("---")

# ─────────────────────────────────────────────
# ROW 1: Model Performance Summary
# ─────────────────────────────────────────────

st.subheader("📊 Model Performance")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Model", "Random Forest")
m2.metric("ROC-AUC (CV)", "0.990")
m3.metric("ROC-AUC (Test)", "0.983")
m4.metric("Class Balance", "Balanced Weights")

st.markdown("---")

# ─────────────────────────────────────────────
# ROW 2: Feature Importance
# ─────────────────────────────────────────────

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

# ─────────────────────────────────────────────
# ROW 3: Interactive Predictor
# ─────────────────────────────────────────────

st.subheader("🎛️ Try It Yourself — Enter Scores")
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
    # Build input
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

    # Display probability
    st.markdown("### 🎯 Medal Probability")

    # Color based on probability
    if rf_prob >= 0.7:
        prob_color = "🥇"
        assessment = "**Medal Likely**"
        st.success(
            f"{prob_color} {assessment} — "
            f"This performance profile is in "
            f"medal contention territory."
        )
    elif rf_prob >= 0.4:
        prob_color = "🎯"
        assessment = "**Podium Possible**"
        st.warning(
            f"{prob_color} {assessment} — "
            f"Competitive but needs a strong "
            f"Free Skate to medal."
        )
    elif rf_prob >= 0.15:
        prob_color = "📈"
        assessment = "**Competitive**"
        st.info(
            f"{prob_color} {assessment} — "
            f"In the field but unlikely to medal."
        )
    else:
        prob_color = "🚀"
        assessment = "**Development Stage**"
        st.error(
            f"{prob_color} {assessment} — "
            f"Significant gap to medal territory."
        )

    # Big number
    st.markdown(
        f"<h1 style='text-align: center; "
        f"color: {'#27AE60' if rf_prob >= 0.5 else '#E74C3C'};'>"
        f"{rf_prob*100:.1f}%</h1>",
        unsafe_allow_html=True
    )
    st.caption("Random Forest Model Prediction")

    st.markdown("---")

    # Model comparison
    st.markdown("**Model Comparison:**")
    st.metric("Random Forest",      f"{rf_prob*100:.1f}%")
    st.metric("Logistic Regression", f"{lr_prob*100:.1f}%")

    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rf_prob * 100,
        title={'text': "Medal Probability (%)"},
        delta={
            'reference': 50,
            'increasing': {'color': '#27AE60'},
            'decreasing': {'color': '#E74C3C'},
        },
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#2C3E50'},
            'steps': [
                {'range': [0, 15],   'color': '#FADBD8'},
                {'range': [15, 40],  'color': '#FDEBD0'},
                {'range': [40, 70],  'color': '#FEF9E7'},
                {'range': [70, 100], 'color': '#D5F5E3'},
            ],
            'threshold': {
                'line': {'color': 'black', 'width': 3},
                'thickness': 0.8,
                'value': 50,
            },
        },
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# ROW 4: Preset Scenarios
# ─────────────────────────────────────────────

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