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
    load_aggregate, load_models, FEATURES
)
from components.styles import (
    load_css, apply_theme, CHART_COLORS
)

st.set_page_config(page_title="Medal Predictor", page_icon="🤖", layout="wide")
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
rf_model, lr_model, scaler = load_models()

st.markdown(
    "<div class='page-title'>🤖 Medal Predictor</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='page-subtitle'>"
    "Enter any skater's performance data and get a real-time "
    "medal probability prediction powered by our machine learning model."
    "</div>",
    unsafe_allow_html=True
)

# Model performance row
m1, m2, m3, m4 = st.columns(4)
perf = [
    ("Random Forest", "Model", "Primary"),
    ("0.990", "ROC-AUC (CV)", "5-Fold"),
    ("0.983", "ROC-AUC (Test)", "Holdout Set"),
    ("53.8%", "Top Feature", "SP Rank"),
]
for col, (num, lbl, sub) in zip([m1, m2, m3, m4], perf):
    with col:
        st.markdown(f"""
        <div class='stat-card-blue'>
            <div class='num'>{num}</div>
            <div class='lbl'>{lbl}</div>
            <div class='sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Feature importance
st.markdown(
    "<div class='section-title'>🔑 What Predicts a Medal?</div>",
    unsafe_allow_html=True
)

col_imp, col_exp = st.columns([2, 1])

with col_imp:
    imp_df = pd.DataFrame({
        'Feature': FEATURES,
        'Importance': rf_model.feature_importances_,
    }).sort_values('Importance', ascending=True)

    fig_imp = px.bar(
        imp_df, x='Importance', y='Feature', orientation='h',
        color='Importance', color_continuous_scale='Blues',
    )
    fig_imp.update_layout(
        xaxis_title="Importance", yaxis_title="",
        title="Feature Importance (Random Forest)",
        coloraxis_showscale=False,
    )
    fig_imp = apply_theme(fig_imp, height=420)
    st.plotly_chart(fig_imp, use_container_width=True)

with col_exp:
    st.markdown("""
    <div class='info-card'>
        <h3>Feature Guide</h3>
        <p><b>sp_rank</b> — Rank after Short Program</p>
        <p><b>total_tss</b> — Total combined score</p>
        <p><b>pcs_total</b> — Artistic/presentation</p>
        <p><b>tes_total</b> — Technical elements</p>
        <p><b>score_momentum</b> — FS minus SP score</p>
        <p><b>rank_change</b> — SP rank minus FS rank</p>
        <p><b>tes_pcs_ratio</b> — Technical vs artistic</p>
        <p><b>tech_dominance</b> — % score from TES</p>
        <p><b>gender</b> — Men=1, Women=0</p>
        <p><b>year</b> — Olympic year</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Interactive predictor
st.markdown(
    "<div class='section-title'>🎛️ Try It — Enter Scores</div>",
    unsafe_allow_html=True
)

col_in, col_out = st.columns([1, 1])

with col_in:
    gender = st.radio("Gender:", ['Men', 'Women'], horizontal=True)
    gender_code = 1 if gender == 'Men' else 0

    if gender == 'Men':
        tss_r, tes_r, pcs_r = (100.0, 340.0, 200.0), (40.0, 200.0, 110.0), (40.0, 150.0, 90.0)
    else:
        tss_r, tes_r, pcs_r = (80.0, 260.0, 150.0), (30.0, 150.0, 80.0), (30.0, 120.0, 70.0)

    total_tss = st.slider("Total Score (TSS)", tss_r[0], tss_r[1], tss_r[2], 1.0)
    tes_total = st.slider("Technical Score (TES)", tes_r[0], tes_r[1], tes_r[2], 1.0)
    pcs_total = st.slider("Program Components (PCS)", pcs_r[0], pcs_r[1], pcs_r[2], 1.0)
    sp_rank   = st.slider("Short Program Rank", 1, 30, 10, 1)

    tech_dom  = tes_total / (tes_total + pcs_total) if (tes_total + pcs_total) > 0 else 0.5
    momentum  = total_tss * 0.6 - total_tss * 0.4
    rank_chg  = max(0, sp_rank - 3)
    tes_pcs   = tes_total / pcs_total if pcs_total > 0 else 1.0

with col_out:
    input_data = pd.DataFrame([{
        'total_tss': total_tss, 'tes_total': tes_total,
        'pcs_total': pcs_total, 'tech_dominance_pct': tech_dom,
        'sp_rank': sp_rank, 'score_momentum': momentum,
        'rank_change': rank_chg, 'tes_pcs_ratio': tes_pcs,
        'gender_encoded': gender_code, 'year': 2028,
    }])

    input_scaled = scaler.transform(input_data)
    rf_prob = rf_model.predict_proba(input_scaled)[0][1]
    lr_prob = lr_model.predict_proba(input_scaled)[0][1]

    if rf_prob >= 0.70:
        color, emoji, verdict = '#00C878', '🥇', 'MEDAL LIKELY'
        detail = 'This performance is in medal territory.'
    elif rf_prob >= 0.40:
        color, emoji, verdict = '#F39C12', '🎯', 'PODIUM POSSIBLE'
        detail = 'Strong performance, needs clean Free Skate.'
    elif rf_prob >= 0.15:
        color, emoji, verdict = '#3D7EFF', '📈', 'COMPETITIVE'
        detail = 'In the field but outside medal range.'
    else:
        color, emoji, verdict = '#E74C3C', '🚀', 'DEVELOPMENT STAGE'
        detail = 'Significant gap to Olympic medal level.'

    st.markdown(f"""
    <div class='prob-box'>
        <div style='font-size: 2.5rem;'>{emoji}</div>
        <div class='prob-num' style='color: {color};'>{rf_prob*100:.1f}%</div>
        <div class='prob-verdict' style='color: {color};'>{verdict}</div>
        <div class='prob-detail'>{detail}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig_g = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rf_prob * 100,
        number=dict(suffix='%', font=dict(color=color, size=32)),
        gauge=dict(
            axis=dict(range=[0, 100], tickfont=dict(color='#6B7B99')),
            bar=dict(color=color, thickness=0.7),
            bgcolor='#F0F4FA',
            steps=[
                {'range': [0, 15],  'color': '#FDE8E8'},
                {'range': [15, 40], 'color': '#FEF3E0'},
                {'range': [40, 70], 'color': '#E8F4FD'},
                {'range': [70, 100],'color': '#E8FDF0'},
            ],
            threshold=dict(line=dict(color='#1A2B4A', width=2), thickness=0.8, value=50),
        ),
    ))
    fig_g = apply_theme(fig_g, height=250)
    fig_g.update_layout(margin=dict(t=20, b=0, l=20, r=20))
    st.plotly_chart(fig_g, use_container_width=True)

    cr, cl = st.columns(2)
    cr.metric("Random Forest", f"{rf_prob*100:.1f}%")
    cl.metric("Logistic Regression", f"{lr_prob*100:.1f}%")

    # Improvement tips
    st.markdown("<br>", unsafe_allow_html=True)
    if sp_rank > 3:
        st.info(f"🎯 **Improve SP rank from #{sp_rank} to top 3** — "
                f"SP rank is 53.8% of prediction.")
    medal_thresh = 275 if gender_code == 1 else 220
    if total_tss < medal_thresh:
        st.info(f"📊 **Score needs +{medal_thresh - total_tss:.0f} points** "
                f"to reach medal threshold ({medal_thresh}).")

st.markdown("<br>", unsafe_allow_html=True)

# Preset scenarios
st.markdown(
    "<div class='section-title'>📋 Preset Scenarios</div>",
    unsafe_allow_html=True
)

scenarios = [
    ('🥇 2026 Gold (Shaidorov)', 291.58, 167.13, 124.45, 0.573, 5, 105.7, 4.0, 1.343, 1, 2026),
    ('🇮🇳 India Tier 1 (Qualify)', 150, 80, 70, 0.533, 25, 20, 2, 1.14, 1, 2028),
    ('🇮🇳 India Tier 3 (Near Medal)', 240, 135, 105, 0.562, 8, 40, 5, 1.29, 1, 2028),
    ('🇮🇳 India Tier 4 (Contention)', 275, 155, 120, 0.563, 3, 50, 8, 1.29, 1, 2028),
]

results = []
for label, *vals in scenarios:
    keys = ['total_tss', 'tes_total', 'pcs_total', 'tech_dominance_pct',
            'sp_rank', 'score_momentum', 'rank_change', 'tes_pcs_ratio',
            'gender_encoded', 'year']
    inp = pd.DataFrame([dict(zip(keys, vals))])
    prob = rf_model.predict_proba(scaler.transform(inp))[0][1]
    results.append({
        'Scenario': label, 'Score': vals[0], 'SP Rank': vals[4],
        'Medal Prob': f"{prob*100:.1f}%",
        'Assessment': '🥇 Likely' if prob > 0.7 else '🎯 Possible' if prob > 0.4
                      else '📈 Competitive' if prob > 0.15 else '🚀 Development',
    })

st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)
st.success(
    "📌 **Model Insight:** The threshold effect is real — medal probability "
    "jumps dramatically at ~275 (Men) / ~220 (Women) with a top-3 SP rank. "
    "For India, the model provides a measurable development pathway."
)