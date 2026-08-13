import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import joblib
import os
import warnings

warnings.filterwarnings('ignore')

from sklearn.ensemble          import RandomForestClassifier
from sklearn.linear_model      import LogisticRegression
from sklearn.preprocessing     import StandardScaler, LabelEncoder
from sklearn.model_selection   import (train_test_split, cross_val_score, StratifiedKFold)
from sklearn.metrics           import (classification_report, confusion_matrix,  roc_auc_score, roc_curve, precision_recall_curve)
from sklearn.inspection        import permutation_importance

os.makedirs("outputs/model", exist_ok=True)
os.makedirs("models",        exist_ok=True)

# ─────────────────────────────────────────────
# 1. LOAD + PREPARE DATA
# ─────────────────────────────────────────────

print("="*60)
print("  FIGURE SKATING MEDAL PREDICTOR")
print("  Model Training Pipeline")
print("="*60)

df = pd.read_csv("data/processed/agg_clean.csv")

print(f"\n📂 Raw data loaded: {df.shape}")

# ── Filter: completed skaters only ──────────
df_model = df[
    (df['skater_status'] == 'COMPLETED') &
    (df['total_tss'] > 0)
].copy()

print(f"📂 After filtering FNR/WD/DSQ: {df_model.shape}")

# ── Encode gender ────────────────────────────
df_model['gender_encoded'] = (
    df_model['gender']
    .map({'M': 1, 'W': 0})
)

# ── Select features ──────────────────────────
# Option A (aggregate) + Option C (derived)
# Deliberately exclude segment-level scores
# to avoid multicollinearity

FEATURES = [
    # Option A — Aggregate scores
    'total_tss',
    'tes_total',
    'pcs_total',

    # Option C — Derived / behavioral features
    'tech_dominance_pct',  # TES ratio
    'sp_rank',             # Short program standing
    'score_momentum',      # FS - SP score diff
    'rank_change',         # SP rank - FS rank
    'tes_pcs_ratio',       # Technical vs artistic balance

    # Context
    'gender_encoded',
    'year',
]

TARGET = 'is_medal'

# ── Build X, y ───────────────────────────────
X = df_model[FEATURES].copy()
y = df_model[TARGET].copy()

print(f"\n📊 Feature matrix : {X.shape}")
print(f"📊 Target vector  : {y.shape}")
print(f"\n📊 Class distribution:")
print(f"   No Medal : {(y==0).sum()} ({(y==0).mean()*100:.1f}%)")
print(f"   Medal    : {(y==1).sum()} ({(y==1).mean()*100:.1f}%)")

# 2. TRAIN / TEST SPLIT   80-20 ratio
print("\n" + "─"*60)
print("  STEP 1: Train/Test Split")
print("─"*60)

# Stratified split preserves class balance
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"\n  Training set : {X_train.shape[0]} rows")
print(f"  Test set     : {X_test.shape[0]} rows")
print(f"\n  Train medals : {y_train.sum()} "
      f"({y_train.mean()*100:.1f}%)")
print(f"  Test medals  : {y_test.sum()} "
      f"({y_test.mean()*100:.1f}%)")


# 3. SCALE FEATURES
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# Keep as DataFrames for readability
X_train_scaled = pd.DataFrame(
    X_train_scaled, columns=FEATURES
)
X_test_scaled = pd.DataFrame(
    X_test_scaled, columns=FEATURES
)

# 4. TRAIN MODELS
print("\n" + "─"*60)
print("  STEP 2: Model Training")
print("─"*60)

# ── Model A: Random Forest ───────────────────
print("\n  Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=500,
    max_depth=6,
    min_samples_leaf=3,
    class_weight='balanced',   # handles 8.9:1 imbalance
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)
print("  ✅ Random Forest trained")

# ── Model B: Logistic Regression ─────────────
print("\n  Training Logistic Regression...")
lr_model = LogisticRegression(
    class_weight='balanced',
    max_iter=1000,
    random_state=42
)
lr_model.fit(X_train_scaled, y_train)
print("  ✅ Logistic Regression trained")


# 5. CROSS VALIDATION
print("\n" + "─"*60)
print("  STEP 3: Cross Validation (5-Fold Stratified)")
print("─"*60)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, model in [("Random Forest",       rf_model),
                    ("Logistic Regression",  lr_model)]:

    # ROC-AUC scores
    auc_scores = cross_val_score(
        model, X_train_scaled, y_train,
        cv=cv, scoring='roc_auc'
    )
    # F1 scores (macro — treats both classes equally)
    f1_scores = cross_val_score(
        model, X_train_scaled, y_train,
        cv=cv, scoring='f1'
    )
    # Precision scores
    prec_scores = cross_val_score(
        model, X_train_scaled, y_train,
        cv=cv, scoring='precision'
    )
    # Recall scores
    rec_scores = cross_val_score(
        model, X_train_scaled, y_train,
        cv=cv, scoring='recall'
    )

    print(f"\n  {name}:")
    print(f"    ROC-AUC   : {auc_scores.mean():.3f} "
          f"(±{auc_scores.std():.3f})")
    print(f"    F1 Score  : {f1_scores.mean():.3f} "
          f"(±{f1_scores.std():.3f})")
    print(f"    Precision : {prec_scores.mean():.3f} "
          f"(±{prec_scores.std():.3f})")
    print(f"    Recall    : {rec_scores.mean():.3f} "
          f"(±{rec_scores.std():.3f})")


# ─────────────────────────────────────────────
# 6. TEST SET EVALUATION
# ─────────────────────────────────────────────

print("\n" + "─"*60)
print("  STEP 4: Test Set Evaluation")
print("─"*60)

for name, model in [("Random Forest",      rf_model),
                    ("Logistic Regression", lr_model)]:

    y_pred      = model.predict(X_test_scaled)
    y_pred_prob = model.predict_proba(X_test_scaled)[:, 1]
    auc         = roc_auc_score(y_test, y_pred_prob)

    print(f"\n  {name}:")
    print(f"    ROC-AUC on test set: {auc:.3f}")
    print(f"\n    Classification Report:")
    report = classification_report(
        y_test, y_pred,
        target_names=['No Medal', 'Medal']
    )
    for line in report.split('\n'):
        print(f"      {line}")


# ─────────────────────────────────────────────
# 7. FEATURE IMPORTANCE
# ─────────────────────────────────────────────

print("\n" + "─"*60)
print("  STEP 5: Feature Importance Analysis")
print("─"*60)

# ── Random Forest built-in importance ────────
rf_importance = pd.DataFrame({
    'feature'   : FEATURES,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n  Random Forest Feature Importance:")
for _, row in rf_importance.iterrows():
    bar = "█" * int(row['importance'] * 50)
    print(f"    {row['feature']:<22} {bar} "
          f"{row['importance']:.4f}")

# ── Logistic Regression coefficients ─────────
lr_coef = pd.DataFrame({
    'feature'    : FEATURES,
    'coefficient': lr_model.coef_[0]
}).sort_values('coefficient', ascending=False)

print("\n  Logistic Regression Coefficients:")
for _, row in lr_coef.iterrows():
    direction = "▲" if row['coefficient'] > 0 else "▼"
    print(f"    {row['feature']:<22} {direction} "
          f"{row['coefficient']:.4f}")


# ─────────────────────────────────────────────
# 8. VISUALIZATIONS
# ─────────────────────────────────────────────

print("\n" + "─"*60)
print("  STEP 6: Generating Model Visualizations")
print("─"*60)

COLORS = {
    'gold'     : '#FFD700',
    'no_medal' : '#4A90D9',
    'accent'   : '#E74C3C',
    'positive' : '#27AE60',
    'neutral'  : '#95A5A6',
    'bg'       : '#F8F9FA',
    'text'     : '#2C3E50',
}

plt.rcParams.update({
    'figure.facecolor' : COLORS['bg'],
    'axes.facecolor'   : COLORS['bg'],
    'axes.titlesize'   : 13,
    'axes.titleweight' : 'bold',
    'font.family'      : 'sans-serif',
})

# ── Chart 1: Feature Importance ──────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle(
    "Feature Importance — What Predicts a Medal?",
    fontsize=15, fontweight='bold', color=COLORS['text']
)

# RF importance
colors_imp = [
    COLORS['accent'] if i == 0 else COLORS['no_medal']
    for i in range(len(rf_importance))
]
axes[0].barh(
    rf_importance['feature'][::-1],
    rf_importance['importance'][::-1],
    color=colors_imp[::-1],
    edgecolor='white', linewidth=0.5
)
axes[0].set_title("Random Forest\nFeature Importance")
axes[0].set_xlabel("Importance Score")
for i, (_, row) in enumerate(
    rf_importance.iloc[::-1].iterrows()
):
    axes[0].text(
        row['importance'] + 0.001,
        i,
        f"{row['importance']:.3f}",
        va='center', fontsize=8
    )

# LR coefficients
coef_colors = [
    COLORS['positive'] if c > 0 else COLORS['accent']
    for c in lr_coef['coefficient']
]
axes[1].barh(
    lr_coef['feature'],
    lr_coef['coefficient'],
    color=coef_colors,
    edgecolor='white', linewidth=0.5
)
axes[1].set_title("Logistic Regression\nCoefficients")
axes[1].set_xlabel("Coefficient Value")
axes[1].axvline(x=0, color=COLORS['text'],
                linewidth=1, alpha=0.5)

pos_patch = mpatches.Patch(
    color=COLORS['positive'], label='Increases medal probability'
)
neg_patch = mpatches.Patch(
    color=COLORS['accent'],   label='Decreases medal probability'
)
axes[1].legend(handles=[pos_patch, neg_patch], fontsize=8)

plt.tight_layout()
plt.savefig("outputs/model/01_feature_importance.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 01_feature_importance.png")

# ── Chart 2: ROC Curves ──────────────────────
fig, ax = plt.subplots(figsize=(8, 7))

for name, model, color in [
    ("Random Forest",      rf_model, COLORS['accent']),
    ("Logistic Regression",lr_model, COLORS['no_medal'])
]:
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)
    ax.plot(fpr, tpr, color=color, linewidth=2.5,
            label=f"{name} (AUC = {auc:.3f})")

ax.plot([0, 1], [0, 1], '--', color='gray',
        alpha=0.5, label='Random Classifier')
ax.fill_between([0, 1], [0, 1], alpha=0.05, color='gray')
ax.set_title("ROC Curve — Medal Prediction",
             fontsize=14, fontweight='bold')
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate (Recall)")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/model/02_roc_curve.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 02_roc_curve.png")

# ── Chart 3: Confusion Matrices ──────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(
    "Confusion Matrices — Test Set Performance",
    fontsize=14, fontweight='bold', color=COLORS['text']
)

for ax, (name, model) in zip(
    axes,
    [("Random Forest",      rf_model),
     ("Logistic Regression", lr_model)]
):
    y_pred = model.predict(X_test_scaled)
    cm = confusion_matrix(y_test, y_pred)

    sns.heatmap(
        cm, annot=True, fmt='d',
        cmap='Blues', ax=ax,
        xticklabels=['No Medal', 'Medal'],
        yticklabels=['No Medal', 'Medal'],
        linewidths=1
    )
    ax.set_title(f"{name}")
    ax.set_ylabel("Actual")
    ax.set_xlabel("Predicted")

plt.tight_layout()
plt.savefig("outputs/model/03_confusion_matrices.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 03_confusion_matrices.png")

# ── Chart 4: Medal Probability Distribution ──
fig, ax = plt.subplots(figsize=(10, 6))

rf_probs_medal    = rf_model.predict_proba(
    X_test_scaled
)[:, 1][y_test == 1]
rf_probs_no_medal = rf_model.predict_proba(
    X_test_scaled
)[:, 1][y_test == 0]

ax.hist(
    rf_probs_no_medal, bins=20,
    color=COLORS['no_medal'], alpha=0.7,
    label='No Medal (Actual)', density=True
)
ax.hist(
    rf_probs_medal, bins=10,
    color=COLORS['gold'], alpha=0.8,
    label='Medal (Actual)', density=True
)
ax.axvline(
    x=0.5, color=COLORS['accent'],
    linewidth=2, linestyle='--',
    label='Decision Threshold (0.5)'
)
ax.set_title(
    "Predicted Medal Probability Distribution\n"
    "(Random Forest — Test Set)",
    fontsize=13, fontweight='bold'
)
ax.set_xlabel("Predicted Probability of Medal")
ax.set_ylabel("Density")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/model/04_probability_distribution.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 04_probability_distribution.png")


# ─────────────────────────────────────────────
# 9. INDIA SIMULATION
# What score would India need?
# ─────────────────────────────────────────────

print("\n" + "─"*60)
print("  STEP 7: India Scenario Simulation")
print("─"*60)

def simulate_skater(
    label, total_tss, tes_total, pcs_total,
    tech_dom, sp_rank, momentum, rank_chg,
    tes_pcs, gender, year=2028
):
    """
    Simulate medal probability for a hypothetical skater.
    gender: 1=Men, 0=Women
    """
    input_data = pd.DataFrame([{
        'total_tss'         : total_tss,
        'tes_total'         : tes_total,
        'pcs_total'         : pcs_total,
        'tech_dominance_pct': tech_dom,
        'sp_rank'           : sp_rank,
        'score_momentum'    : momentum,
        'rank_change'       : rank_chg,
        'tes_pcs_ratio'     : tes_pcs,
        'gender_encoded'    : gender,
        'year'              : year,
    }])

    input_scaled = scaler.transform(input_data)
    prob = rf_model.predict_proba(input_scaled)[0][1]
    return prob

print("\n  Men's Scenarios:")
print(f"  {'Scenario':<30} {'Score':>6} "
      f"{'Medal Prob':>12} {'Assessment'}")
print(f"  {'─'*30} {'─'*6} {'─'*12} {'─'*20}")

men_scenarios = [
    # label, tss, tes, pcs, tech_dom, sp_rank,
    # momentum, rank_chg, tes_pcs, gender
    ("India Tier 1 (Just Qualify)",
     150, 80, 70, 0.533, 25, 20, 2, 1.14, 1),
    ("India Tier 2 (Competitive)",
     200, 110, 90, 0.550, 15, 30, 3, 1.22, 1),
    ("India Tier 3 (Near Medal)",
     240, 135, 105, 0.562, 8,  40, 5, 1.29, 1),
    ("India Tier 4 (Medal Contention)",
     275, 155, 120, 0.563, 3,  50, 8, 1.29, 1),
    ("Actual 2026 Gold (Shaidorov)",
     291, 167, 124, 0.573, 1,  105, 4, 1.35, 1),
]

for scenario in men_scenarios:
    label = scenario[0]
    args  = scenario[1:]
    prob  = simulate_skater(label, *args)
    assessment = (
        "🥇 Medal likely"     if prob > 0.70 else
        "🎯 Podium possible"  if prob > 0.40 else
        "📈 Competitive"      if prob > 0.20 else
        "🚀 First milestone"
    )
    print(f"  {label:<30} {scenario[1]:>6.1f} "
          f"  {prob*100:>8.1f}%   {assessment}")

print(f"\n  Women's Scenarios:")
print(f"  {'Scenario':<30} {'Score':>6} "
      f"{'Medal Prob':>12} {'Assessment'}")
print(f"  {'─'*30} {'─'*6} {'─'*12} {'─'*20}")

women_scenarios = [
    ("India Tier 1 (Just Qualify)",
     100, 55, 45, 0.550, 20, 15, 2, 1.22, 0),
    ("India Tier 2 (Competitive)",
     150, 82, 68, 0.547, 12, 25, 3, 1.21, 0),
    ("India Tier 3 (Near Medal)",
     190, 105, 85, 0.553, 7,  35, 5, 1.24, 0),
    ("India Tier 4 (Medal Contention)",
     220, 122, 98, 0.555, 3,  45, 7, 1.24, 0),
    ("Actual 2026 Gold (Women)",
     255, 140, 115, 0.549, 1, 80, 6, 1.22, 0),
]

for scenario in women_scenarios:
    label = scenario[0]
    args  = scenario[1:]
    prob  = simulate_skater(label, *args)
    assessment = (
        "🥇 Medal likely"     if prob > 0.70 else
        "🎯 Podium possible"  if prob > 0.40 else
        "📈 Competitive"      if prob > 0.20 else
        "🚀 First milestone"
    )
    print(f"  {label:<30} {scenario[1]:>6.1f} "
          f"  {prob*100:>8.1f}%   {assessment}")


# ─────────────────────────────────────────────
# 10. SAVE MODELS + ARTIFACTS
# ─────────────────────────────────────────────

print("\n" + "─"*60)
print("  STEP 8: Saving Models and Artifacts")
print("─"*60)

# Save Random Forest (primary model)
joblib.dump(rf_model, "models/rf_medal_predictor.pkl")
print("\n  ✅ Saved: models/rf_medal_predictor.pkl")

# Save Logistic Regression (interpretability)
joblib.dump(lr_model, "models/lr_medal_predictor.pkl")
print("  ✅ Saved: models/lr_medal_predictor.pkl")

# Save scaler (MUST save — needed for dashboard)
joblib.dump(scaler, "models/scaler.pkl")
print("  ✅ Saved: models/scaler.pkl")

# Save feature importance as CSV
rf_importance.to_csv(
    "outputs/model/feature_importance.csv", index=False
)
print("  ✅ Saved: outputs/model/feature_importance.csv")

# Save feature list (dashboard needs exact order)
feature_df = pd.DataFrame({'feature': FEATURES})
feature_df.to_csv("models/feature_list.csv", index=False)
print("  ✅ Saved: models/feature_list.csv")

print("\n" + "="*60)
print("  ✅ MODEL PIPELINE COMPLETE")
print("="*60)
print(f"""
  Summary:
  ─────────────────────────────────────────
  Training rows    : {X_train.shape[0]}
  Test rows        : {X_test.shape[0]}
  Features used    : {len(FEATURES)}
  Models trained   : Random Forest +
                     Logistic Regression
  Imbalance handled: class_weight='balanced'
  
  Saved artifacts:
    models/rf_medal_predictor.pkl
    models/lr_medal_predictor.pkl
    models/scaler.pkl
    models/feature_list.csv
    outputs/model/ (4 charts)
  ─────────────────────────────────────────
""")
