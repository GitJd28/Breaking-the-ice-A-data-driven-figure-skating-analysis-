import pandas as pd
import joblib
import os

# Paths — relative to project root
BASE_DIR   = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
             )

DATA_DIR   = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")


# Data loaders — cached so Streamlit doesn't
# reload on every interaction

import streamlit as st

@st.cache_data
def load_aggregate():
    path = os.path.join(DATA_DIR, "agg_clean.csv")
    df = pd.read_csv(path)
    df['medal_label'] = df['medal'].map({
        0: 'No Medal',
        1: 'Gold',
        2: 'Silver',
        3: 'Bronze'
    })
    # Filter out FNR/WD/DSQ for most analyses
    df_clean = df[
        (df['skater_status'] == 'COMPLETED') &
        (df['total_tss'] > 0)
    ].copy()
    return df, df_clean   # raw, clean


@st.cache_data
def load_long():
    path = os.path.join(DATA_DIR, "long_clean.csv")
    return pd.read_csv(path)


@st.cache_data
def load_worldchamp():
    path = os.path.join(DATA_DIR, "wc_clean.csv")
    return pd.read_csv(path)


@st.cache_resource
def load_models():
    rf     = joblib.load(os.path.join(MODELS_DIR, "rf_medal_predictor.pkl"))
    lr     = joblib.load(os.path.join(MODELS_DIR, "lr_medal_predictor.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    return rf, lr, scaler

# Shared constants
MEDAL_COLORS = {
    'Gold'    : '#FFD700',
    'Silver'  : '#C0C0C0',
    'Bronze'  : '#CD7F32',
    'No Medal': '#4A90D9',
}

COLORS = {
    'gold'      : '#FFD700',
    'silver'    : '#C0C0C0',
    'bronze'    : '#CD7F32',
    'no_medal'  : '#4A90D9',
    'accent'    : '#E74C3C',
    'positive'  : '#27AE60',
    'neutral'   : '#95A5A6',
    'text'      : '#2C3E50',
    'pre_quad'  : '#95A5A6',
    'post_quad' : '#E74C3C',
}

TRADITIONAL_NATIONS = [
    'USA', 'JPN', 'CAN', 'RUS',
    'FRA', 'ITA', 'CHN', 'GER',
    'UKR', 'SUI'
]

FEATURES = [
    'total_tss',
    'tes_total',
    'pcs_total',
    'tech_dominance_pct',
    'sp_rank',
    'score_momentum',
    'rank_change',
    'tes_pcs_ratio',
    'gender_encoded',
    'year',
]