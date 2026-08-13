import pandas as pd
import numpy as np
import os

os.makedirs("data/processed", exist_ok=True)

# ─────────────────────────────────────────────
# 1. LOAD RAW DATA
# ─────────────────────────────────────────────

df_agg = pd.read_csv("data/raw/olympics_singles_agg.csv")
df_long = pd.read_csv("data/raw/olympics_singles_long.csv")
df_wc = pd.read_csv("data/raw/WC Scores Men.csv")


# ─────────────────────────────────────────────
# 2. CLEAN DATASET 1 — Olympics Aggregate
# ─────────────────────────────────────────────

def clean_aggregate(df):
    df = df.copy()

    # Fix 1: Separate special statuses from numeric ranks
    special_statuses = ['FNR', 'WD', 'DSQ']
    df['skater_status'] = df['final_rank'].apply(
        lambda x: x if x in special_statuses else 'COMPLETED'
    )

    # Fix 2: Convert final_rank to numeric (NaN for special cases)
    df['final_rank_num'] = pd.to_numeric(
        df['final_rank'], errors='coerce'
    )

    # Fix 3: Convert tech_dominance from "57.32%" to 0.5732
    df['tech_dominance_pct'] = (
        df['tech_dominance']
        .str.replace('%', '', regex=False)
        .astype(float) / 100
    )
    df = df.drop(columns=['tech_dominance'])

    # Fix 4: Handle fs_rank nulls (6 nulls = skaters who withdrew)
    # Fill with a large number to indicate they didn't finish
    max_fs_rank = df['fs_rank'].max()
    df['fs_rank'] = df['fs_rank'].fillna(max_fs_rank + 1)

    # Fix 5: Add medal binary columns for easier modeling
    df['is_medal'] = (df['medal'] > 0).astype(int)
    df['is_gold']  = (df['medal'] == 1).astype(int)

    # Fix 6: Feature engineering — rank change SP to FS
    # Positive = improved in FS (clutch), Negative = dropped
    df['rank_change'] = df['sp_rank'] - df['fs_rank']

    # Fix 7: Score momentum — did FS score beat SP score?
    df['score_momentum'] = df['tss_fs'] - df['tss_sp']

    # Fix 8: TES to PCS ratio (clean float version)
    df['tes_pcs_ratio'] = df['tes_total'] / df['pcs_total']

    # Fix 9: Ensure gender is consistent
    df['gender'] = df['gender'].str.upper().str.strip()

    return df


# ─────────────────────────────────────────────
# 3. CLEAN DATASET 2 — Olympics Long
# ─────────────────────────────────────────────

def clean_long(df):
    df = df.copy()

    # Fix 1: Standardize segment values
    df['segment'] = df['segment'].str.upper().str.strip()
    # Should be 'SP' or 'FS'

    # Fix 2: Convert rank_segment to numeric
    df['rank_segment_num'] = pd.to_numeric(
        df['rank_segment'], errors='coerce'
    )

    # Fix 3: Standardize gender
    df['gender'] = df['gender'].str.upper().str.strip()

    # Fix 4: Flag deductions
    df['has_deduction'] = (df['ded'] > 0).astype(int)

    # Fix 5: TES to PCS ratio per segment
    df['tes_pcs_ratio'] = df['tes'] / df['pcs']

    return df


# ─────────────────────────────────────────────
# 4. CLEAN DATASET 3 — World Championships
# ─────────────────────────────────────────────

def clean_worldchamp(df):
    df = df.copy()

    # Fix 1: Standardize column names
    df.columns = (
        df.columns
        .str.lower()
        .str.replace(' ', '_', regex=False)
    )
    # Result: year, skater, sp_total, sp_tes, sp_pc,
    #         quads_in_sp, fs_total, fs_tes, fs_pc, quads_in_fs

    # Fix 2: Total quads (SP + FS)
    df['total_quads'] = df['quads_in_sp'] + df['quads_in_fs']

    # Fix 3: Overall total score
    df['total_score'] = df['sp_total'] + df['fs_total']

    # Fix 4: TES dominance ratio
    df['tes_total'] = df['sp_tes'] + df['fs_tes']
    df['pcs_total'] = df['sp_pc']  + df['fs_pc']
    df['tes_pcs_ratio'] = df['tes_total'] / df['pcs_total']

    # Fix 5: Score momentum
    df['score_momentum'] = df['fs_total'] - df['sp_total']

    # Fix 6: Quad era flag
    # Quad revolution is generally considered post-2014
    df['quad_era'] = (df['year'] >= 2014).astype(int)

    return df


# ─────────────────────────────────────────────
# 5. RUN CLEANING
# ─────────────────────────────────────────────

df_agg_clean  = clean_aggregate(df_agg)
df_long_clean = clean_long(df_long)
df_wc_clean   = clean_worldchamp(df_wc)


# ─────────────────────────────────────────────
# 6. SAVE PROCESSED DATA
# ─────────────────────────────────────────────

df_agg_clean.to_csv("data/processed/agg_clean.csv",  index=False)
df_long_clean.to_csv("data/processed/long_clean.csv", index=False)
df_wc_clean.to_csv("data/processed/wc_clean.csv",    index=False)

print("✅ All datasets cleaned and saved to data/processed/")


# ─────────────────────────────────────────────
# 7. VALIDATION CHECKS
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("  VALIDATION — AGGREGATE DATASET")
print("="*60)
print(f"\n  Skater statuses:\n"
      f"  {df_agg_clean['skater_status'].value_counts().to_dict()}")

print(f"\n  Tech dominance (sample):\n"
      f"  {df_agg_clean['tech_dominance_pct'].head().tolist()}")

print(f"\n  Rank change (SP → FS) sample:\n"
      f"  {df_agg_clean['rank_change'].describe()}")

print(f"\n  New columns added:\n"
      f"  {[c for c in df_agg_clean.columns if c not in df_agg.columns]}")

print("\n" + "="*60)
print("  VALIDATION — WORLD CHAMPIONSHIP DATASET")
print("="*60)
print(f"\n  Columns after rename:\n"
      f"  {df_wc_clean.columns.tolist()}")

print(f"\n  Quad era distribution:\n"
      f"  {df_wc_clean['quad_era'].value_counts().to_dict()}")

print(f"\n  Total quads range: "
      f"  {df_wc_clean['total_quads'].min()} → "
      f"  {df_wc_clean['total_quads'].max()}")

print(f"\n  Sample:\n{df_wc_clean.head(3)}")

print("\n" + "="*60)
print("  CLASS IMBALANCE CHECK (for modeling)")
print("="*60)
print(f"\n  Medal classes:\n"
      f"  {df_agg_clean['medal'].value_counts().to_dict()}")
print(f"\n  Is_medal:\n"
      f"  {df_agg_clean['is_medal'].value_counts().to_dict()}")
print(f"\n  Imbalance ratio: "
      f"  {321/36:.1f}:1 (non-medal:medal)")
print(f"\n  → Will use class_weight='balanced' in model")