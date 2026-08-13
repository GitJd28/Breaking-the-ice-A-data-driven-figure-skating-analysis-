import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────

# Create folder to save all EDA charts
os.makedirs("outputs/eda", exist_ok=True)

# Color palette — consistent throughout
COLORS = {
    'gold'       : '#FFD700',
    'silver'     : '#C0C0C0',
    'bronze'     : '#CD7F32',
    'no_medal'   : '#4A90D9',
    'accent'     : '#E74C3C',
    'background' : '#F8F9FA',
    'text'       : '#2C3E50',
    'pre_quad'   : '#95A5A6',
    'post_quad'  : '#E74C3C',
    'kaz'        : '#27AE60',
}

plt.rcParams.update({
    'figure.facecolor'  : COLORS['background'],
    'axes.facecolor'    : COLORS['background'],
    'axes.titlesize'    : 14,
    'axes.titleweight'  : 'bold',
    'axes.labelsize'    : 11,
    'xtick.labelsize'   : 9,
    'ytick.labelsize'   : 9,
    'font.family'       : 'sans-serif',
})

# ─────────────────────────────────────────────
# LOAD CLEANED DATA
# ─────────────────────────────────────────────

df_agg  = pd.read_csv("data/processed/agg_clean.csv")
df_long = pd.read_csv("data/processed/long_clean.csv")
df_wc   = pd.read_csv("data/processed/wc_clean.csv")

# Medal label mapping
medal_labels = {0: 'No Medal', 1: 'Gold', 2: 'Silver', 3: 'Bronze'}
df_agg['medal_label'] = df_agg['medal'].map(medal_labels)

print("✅ Data loaded successfully")
print(f"   Aggregate : {df_agg.shape}")
print(f"   Long      : {df_long.shape}")
print(f"   World Champ: {df_wc.shape}")


# ─────────────────────────────────────────────
# EDA 1: NATION DOMINANCE
# Who dominates Olympic figure skating?
# ─────────────────────────────────────────────

print("\n📊 EDA 1: Nation Dominance...")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle(
    "Nation Dominance in Olympic Figure Skating (2006–2026)",
    fontsize=16, fontweight='bold', color=COLORS['text'], y=1.02
)

# --- Chart 1A: Total appearances by top 15 nations ---
nation_counts = (
    df_agg['nation']
    .value_counts()
    .head(15)
    .reset_index()
)
nation_counts.columns = ['nation', 'appearances']

bar_colors = [COLORS['accent'] if n == 'KAZ'
              else COLORS['no_medal']
              for n in nation_counts['nation']]

axes[0].barh(
    nation_counts['nation'][::-1],
    nation_counts['appearances'][::-1],
    color=bar_colors[::-1],
    edgecolor='white', linewidth=0.5
)
axes[0].set_title("Olympic Appearances (Top 15 Nations)")
axes[0].set_xlabel("Number of Athletes")
axes[0].axvline(x=0, color=COLORS['text'], linewidth=0.5)

# Annotate Kazakhstan
for i, (nation, count) in enumerate(
    zip(nation_counts['nation'][::-1],
        nation_counts['appearances'][::-1])
):
    axes[0].text(
        count + 0.2,
        i,
        str(count),
        va='center',
        fontsize=8,
        color=COLORS['text']
    )

# --- Chart 1B: Medal count by top 10 nations ---
medal_df = df_agg[df_agg['medal'] > 0].copy()
medal_pivot = (
    medal_df.groupby(['nation', 'medal_label'])
    .size()
    .unstack(fill_value=0)
)

# Ensure all columns exist
for col in ['Gold', 'Silver', 'Bronze']:
    if col not in medal_pivot.columns:
        medal_pivot[col] = 0

medal_pivot['total'] = medal_pivot.sum(axis=1)
medal_pivot = medal_pivot.nlargest(10, 'total')
medal_pivot = medal_pivot.drop(columns='total')

medal_pivot[['Gold', 'Silver', 'Bronze']].plot(
    kind='barh',
    ax=axes[1],
    color=[COLORS['gold'], COLORS['silver'], COLORS['bronze']],
    edgecolor='white',
    linewidth=0.5
)
axes[1].set_title("Medal Count by Nation (Top 10)")
axes[1].set_xlabel("Number of Medals")
axes[1].legend(title="Medal", loc='lower right')
axes[1].invert_yaxis()

plt.tight_layout()
plt.savefig("outputs/eda/01_nation_dominance.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 01_nation_dominance.png")


# ─────────────────────────────────────────────
# EDA 2: SCORE DISTRIBUTIONS
# How different are medalists vs non-medalists?
# ─────────────────────────────────────────────

print("\n📊 EDA 2: Score Distributions...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(
    "Score Distributions: Medalists vs Non-Medalists",
    fontsize=16, fontweight='bold', color=COLORS['text']
)

score_cols = [
    ('total_tss', 'Total Score (TSS)'),
    ('tes_total', 'Technical Score (TES)'),
    ('pcs_total', 'Program Components (PCS)'),
    ('tech_dominance_pct', 'TES Dominance Ratio'),
]

medal_color_map = {
    'No Medal' : COLORS['no_medal'],
    'Gold'     : COLORS['gold'],
    'Silver'   : COLORS['silver'],
    'Bronze'   : COLORS['bronze'],
}

for ax, (col, title) in zip(axes.flat, score_cols):
    for medal_type, color in medal_color_map.items():
        subset = df_agg[df_agg['medal_label'] == medal_type][col]
        if len(subset) > 0:
            subset.plot.kde(
                ax=ax,
                label=medal_type,
                color=color,
                linewidth=2.5 if medal_type != 'No Medal' else 1.5,
                alpha=0.9 if medal_type != 'No Medal' else 0.6
            )
    ax.set_title(title)
    ax.set_xlabel(col)
    ax.set_ylabel("Density")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/eda/02_score_distributions.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 02_score_distributions.png")


# ─────────────────────────────────────────────
# EDA 3: TES vs PCS SCATTER
# Technical vs Artistic — what wins medals?
# ─────────────────────────────────────────────

print("\n📊 EDA 3: TES vs PCS Scatter...")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle(
    "Technical (TES) vs Artistic (PCS) Scores",
    fontsize=16, fontweight='bold', color=COLORS['text']
)

for ax, gender in zip(axes, ['M', 'W']):
    gender_label = "Men" if gender == 'M' else "Women"
    subset = df_agg[df_agg['gender'] == gender]

    for medal_type, color in medal_color_map.items():
        ms = subset[subset['medal_label'] == medal_type]
        size = 120 if medal_type != 'No Medal' else 40
        alpha = 0.9 if medal_type != 'No Medal' else 0.4
        marker = '*' if medal_type == 'Gold' else 'o'
        ax.scatter(
            ms['tes_total'],
            ms['pcs_total'],
            c=color,
            s=size,
            alpha=alpha,
            label=medal_type,
            marker=marker,
            edgecolors='white' if medal_type != 'No Medal' else 'none',
            linewidths=0.5,
            zorder=3 if medal_type != 'No Medal' else 1
        )

    # Diagonal line (TES = PCS balance)
    min_val = min(subset['tes_total'].min(), subset['pcs_total'].min())
    max_val = max(subset['tes_total'].max(), subset['pcs_total'].max())
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        '--', color='gray', alpha=0.4, linewidth=1,
        label='TES = PCS'
    )

    ax.set_title(f"{gender_label}'s Singles")
    ax.set_xlabel("Technical Score (TES)")
    ax.set_ylabel("Program Component Score (PCS)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/eda/03_tes_vs_pcs_scatter.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 03_tes_vs_pcs_scatter.png")


# ─────────────────────────────────────────────
# EDA 4: SHORT PROGRAM RANK vs FINAL RANK
# Does leading after SP guarantee the gold?
# ─────────────────────────────────────────────

print("\n📊 EDA 4: SP Rank vs Final Rank...")

completed = df_agg[
    df_agg['skater_status'] == 'COMPLETED'
].copy()
completed['final_rank_num'] = pd.to_numeric(
    completed['final_rank_num'], errors='coerce'
)
completed = completed.dropna(subset=['final_rank_num'])

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle(
    "Short Program Rank vs Final Rank — Does SP Performance Predict Gold?",
    fontsize=16, fontweight='bold', color=COLORS['text']
)

for ax, gender in zip(axes, ['M', 'W']):
    gender_label = "Men" if gender == 'M' else "Women"
    subset = completed[completed['gender'] == gender]

    for medal_type, color in medal_color_map.items():
        ms = subset[subset['medal_label'] == medal_type]
        size = 150 if medal_type != 'No Medal' else 40
        alpha = 0.9 if medal_type != 'No Medal' else 0.3
        marker = '*' if medal_type == 'Gold' else 'o'
        ax.scatter(
            ms['sp_rank'],
            ms['final_rank_num'],
            c=color, s=size, alpha=alpha,
            label=medal_type, marker=marker,
            edgecolors='white' if medal_type != 'No Medal' else 'none',
            linewidths=0.5,
            zorder=3 if medal_type != 'No Medal' else 1
        )

    # Perfect diagonal (SP rank = Final rank)
    max_rank = int(subset['sp_rank'].max())
    ax.plot(
        [1, max_rank], [1, max_rank],
        '--', color='gray', alpha=0.5,
        linewidth=1, label='SP = Final'
    )

    ax.set_title(f"{gender_label}'s Singles")
    ax.set_xlabel("Short Program Rank")
    ax.set_ylabel("Final Rank")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.invert_xaxis()
    ax.invert_yaxis()

plt.tight_layout()
plt.savefig("outputs/eda/04_sp_vs_final_rank.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 04_sp_vs_final_rank.png")


# ─────────────────────────────────────────────
# EDA 5: SCORE TRENDS OVER TIME
# How have scores evolved across Olympics?
# ─────────────────────────────────────────────

print("\n📊 EDA 5: Score Trends Over Time...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(
    "Score Trends Across Olympic Games (2006–2026)",
    fontsize=16, fontweight='bold', color=COLORS['text']
)

metrics = [
    ('total_tss', 'Average Total Score (TSS)'),
    ('tes_total', 'Average Technical Score (TES)'),
    ('pcs_total', 'Average Program Components (PCS)'),
    ('tech_dominance_pct', 'Average TES Dominance Ratio'),
]

for ax, (col, title) in zip(axes.flat, metrics):
    for gender in ['M', 'W']:
        gender_label = "Men" if gender == 'M' else "Women"
        color = COLORS['accent'] if gender == 'M' else COLORS['no_medal']

        # All skaters trend
        trend = (
            df_agg[df_agg['gender'] == gender]
            .groupby('year')[col]
            .mean()
            .reset_index()
        )
        ax.plot(
            trend['year'], trend[col],
            color=color, linewidth=2,
            marker='o', markersize=5,
            label=f"{gender_label} (All)",
            alpha=0.7
        )

        # Medalists only trend
        medalists = df_agg[
            (df_agg['gender'] == gender) &
            (df_agg['medal'] > 0)
        ]
        med_trend = (
            medalists.groupby('year')[col]
            .mean()
            .reset_index()
        )
        ax.plot(
            med_trend['year'], med_trend[col],
            color=color, linewidth=2.5,
            marker='*', markersize=10,
            label=f"{gender_label} (Medalists)",
            linestyle='--'
        )

    ax.set_title(title)
    ax.set_xlabel("Olympic Year")
    ax.set_ylabel(col)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(df_agg['year'].unique())

plt.tight_layout()
plt.savefig("outputs/eda/05_score_trends.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 05_score_trends.png")


# ─────────────────────────────────────────────
# EDA 6: THE QUAD REVOLUTION
# Did quads change everything?
# ─────────────────────────────────────────────

print("\n📊 EDA 6: The Quad Revolution...")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle(
    "The Quad Revolution — How Quad Jumps Changed Figure Skating",
    fontsize=16, fontweight='bold', color=COLORS['text']
)

# --- Chart 6A: Quads per skater over time ---
quad_trend = (
    df_wc.groupby('year')['total_quads']
    .mean()
    .reset_index()
)
colors_trend = [
    COLORS['pre_quad'] if y < 2014 else COLORS['post_quad']
    for y in quad_trend['year']
]
axes[0].bar(
    quad_trend['year'],
    quad_trend['total_quads'],
    color=colors_trend,
    edgecolor='white', linewidth=0.5
)
axes[0].axvline(
    x=2014, color=COLORS['text'],
    linewidth=2, linestyle='--', alpha=0.7
)
axes[0].text(
    2014.2, quad_trend['total_quads'].max() * 0.9,
    'Quad Era\nBegins',
    fontsize=8, color=COLORS['text']
)
axes[0].set_title("Average Quads Per Skater\n(World Championships)")
axes[0].set_xlabel("Year")
axes[0].set_ylabel("Average Total Quads")

pre  = mpatches.Patch(color=COLORS['pre_quad'],  label='Pre-Quad Era')
post = mpatches.Patch(color=COLORS['post_quad'], label='Quad Era')
axes[0].legend(handles=[pre, post], fontsize=8)

# --- Chart 6B: Quads vs Total Score ---
axes[1].scatter(
    df_wc[df_wc['quad_era'] == 0]['total_quads'],
    df_wc[df_wc['quad_era'] == 0]['total_score'],
    color=COLORS['pre_quad'], alpha=0.6,
    label='Pre-2014', s=40
)
axes[1].scatter(
    df_wc[df_wc['quad_era'] == 1]['total_quads'],
    df_wc[df_wc['quad_era'] == 1]['total_score'],
    color=COLORS['post_quad'], alpha=0.6,
    label='Post-2014', s=40
)

# Correlation annotation
corr = df_wc['total_quads'].corr(df_wc['total_score'])
axes[1].text(
    0.05, 0.95,
    f"Correlation: r = {corr:.3f}",
    transform=axes[1].transAxes,
    fontsize=9, color=COLORS['text'],
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
)
axes[1].set_title("Quads vs Total Score")
axes[1].set_xlabel("Total Quads Attempted")
axes[1].set_ylabel("Total Score")
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.3)

# --- Chart 6C: TES vs PCS over time ---
tes_trend = df_wc.groupby('year')[['tes_total', 'pcs_total']].mean()
axes[2].plot(
    tes_trend.index, tes_trend['tes_total'],
    color=COLORS['accent'], linewidth=2.5,
    marker='o', markersize=5, label='TES (Technical)'
)
axes[2].plot(
    tes_trend.index, tes_trend['pcs_total'],
    color=COLORS['no_medal'], linewidth=2.5,
    marker='s', markersize=5, label='PCS (Artistic)'
)
axes[2].axvline(
    x=2014, color=COLORS['text'],
    linewidth=1.5, linestyle='--', alpha=0.7
)
axes[2].set_title("TES vs PCS Over Time\n(World Championships)")
axes[2].set_xlabel("Year")
axes[2].set_ylabel("Average Score Component")
axes[2].legend(fontsize=8)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/eda/06_quad_revolution.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 06_quad_revolution.png")


# ─────────────────────────────────────────────
# EDA 7: CORRELATION HEATMAP
# What features correlate with medals?
# ─────────────────────────────────────────────

print("\n📊 EDA 7: Correlation Heatmap...")

numeric_cols = [
    'total_tss', 'tes_total', 'pcs_total',
    'tech_dominance_pct', 'tss_sp', 'tes_sp', 'pcs_sp',
    'tss_fs', 'tes_fs', 'pcs_fs',
    'sp_rank', 'rank_change', 'score_momentum',
    'tes_pcs_ratio', 'is_medal'
]

corr_matrix = df_agg[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(14, 11))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    fmt='.2f',
    cmap='RdYlGn',
    center=0,
    vmin=-1, vmax=1,
    ax=ax,
    linewidths=0.5,
    annot_kws={'size': 8}
)
ax.set_title(
    "Feature Correlation Matrix\n(What correlates with winning medals?)",
    fontsize=14, fontweight='bold', pad=20
)
plt.tight_layout()
plt.savefig("outputs/eda/07_correlation_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 07_correlation_heatmap.png")


# ─────────────────────────────────────────────
# EDA 8: EMERGING NATIONS SPOTLIGHT
# Kazakhstan's breakthrough — the template
# ─────────────────────────────────────────────

print("\n📊 EDA 8: Emerging Nations Spotlight...")

# Define emerging nations (non-traditional powers)
traditional = ['USA', 'JPN', 'CAN', 'RUS', 'FRA',
               'ITA', 'CHN', 'GER', 'UKR', 'SUI']
df_agg['nation_type'] = df_agg['nation'].apply(
    lambda x: 'Traditional Power' if x in traditional
    else 'Emerging Nation'
)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle(
    "Emerging Nations in Olympic Figure Skating\n"
    "— The Kazakhstan Blueprint",
    fontsize=16, fontweight='bold', color=COLORS['text']
)

# --- Chart 8A: Traditional vs Emerging score comparison ---
score_comp = df_agg.groupby('nation_type')['total_tss'].describe()

bp_data = [
    df_agg[df_agg['nation_type'] == 'Traditional Power']['total_tss'],
    df_agg[df_agg['nation_type'] == 'Emerging Nation']['total_tss'],
]
bp = axes[0].boxplot(
    bp_data,
    tick_labels=['Traditional\nPowers', 'Emerging\nNations'],
    patch_artist=True,
    medianprops=dict(color=COLORS['text'], linewidth=2)
)
bp['boxes'][0].set_facecolor(COLORS['accent'])
bp['boxes'][1].set_facecolor(COLORS['no_medal'])
axes[0].set_title("Score Distribution:\nTraditional vs Emerging")
axes[0].set_ylabel("Total Score (TSS)")
axes[0].grid(True, alpha=0.3, axis='y')

# --- Chart 8B: Kazakhstan journey over time ---
kaz_data = df_agg[df_agg['nation'] == 'KAZ'].sort_values('year')

if len(kaz_data) > 0:
    for gender in ['M', 'W']:
        kaz_gender = kaz_data[kaz_data['gender'] == gender]
        if len(kaz_gender) > 0:
            gender_label = "Men" if gender == 'M' else "Women"
            color = COLORS['accent'] if gender == 'M' \
                    else COLORS['no_medal']
            axes[1].plot(
                kaz_gender['year'],
                kaz_gender['total_tss'],
                marker='o', linewidth=2,
                color=color, label=gender_label,
                alpha=0.8
            )

    # Highlight 2026 gold
    gold_2026 = kaz_data[
        (kaz_data['year'] == 2026) & (kaz_data['medal'] == 1)
    ]
    if len(gold_2026) > 0:
        axes[1].scatter(
            gold_2026['year'],
            gold_2026['total_tss'],
            color=COLORS['gold'], s=300,
            marker='*', zorder=5,
            label='2026 Gold!', edgecolors='black', linewidths=0.5
        )
        axes[1].annotate(
            'GOLD\n(Shaidorov)',
            xy=(gold_2026['year'].values[0],
                gold_2026['total_tss'].values[0]),
            xytext=(2024, gold_2026['total_tss'].values[0] - 15),
            fontsize=8, color=COLORS['text'],
            arrowprops=dict(arrowstyle='->', color=COLORS['text'])
        )

axes[1].set_title("Kazakhstan's Score Journey\n(Olympic Games)")
axes[1].set_xlabel("Year")
axes[1].set_ylabel("Total Score (TSS)")
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.3)

# --- Chart 8C: Minimum score to qualify over time ---
# (last place score each year = qualification threshold)
qual_threshold = (
    df_agg[df_agg['skater_status'] == 'COMPLETED']
    .groupby(['year', 'gender'])['total_tss']
    .min()
    .reset_index()
    .rename(columns={'total_tss': 'min_score'})
)
medal_avg = (
    df_agg[df_agg['medal'] > 0]
    .groupby(['year', 'gender'])['total_tss']
    .mean()
    .reset_index()
    .rename(columns={'total_tss': 'medal_avg'})
)

for gender in ['M', 'W']:
    gender_label = "Men" if gender == 'M' else "Women"
    color = COLORS['accent'] if gender == 'M' else COLORS['no_medal']

    qt = qual_threshold[qual_threshold['gender'] == gender]
    ma = medal_avg[medal_avg['gender'] == gender]

    axes[2].plot(
        qt['year'], qt['min_score'],
        color=color, linewidth=2, linestyle='--',
        marker='o', markersize=4,
        label=f'{gender_label} (Min Qualify)',
        alpha=0.7
    )
    axes[2].plot(
        ma['year'], ma['medal_avg'],
        color=color, linewidth=2.5,
        marker='*', markersize=8,
        label=f'{gender_label} (Medal Avg)',
    )

axes[2].set_title("Qualification Threshold vs\nMedal Average Over Time")
axes[2].set_xlabel("Year")
axes[2].set_ylabel("Total Score (TSS)")
axes[2].legend(fontsize=7)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/eda/08_emerging_nations.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 08_emerging_nations.png")


# ─────────────────────────────────────────────
# EDA 9: DEDUCTION ANALYSIS
# Do deductions cost medals?
# ─────────────────────────────────────────────

print("\n📊 EDA 9: Deduction Analysis...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(
    "Deduction Analysis — Do Falls and Errors Cost Medals?",
    fontsize=16, fontweight='bold', color=COLORS['text']
)

# Merge long format with medal info
df_long_medal = df_long.merge(
    df_agg[['year', 'gender', 'skater', 'medal', 'medal_label']],
    on=['year', 'gender', 'skater'],
    how='left'
)
df_long_medal['medal_label'] = (
    df_long_medal['medal_label'].fillna('No Medal')
)

# --- Chart 9A: Deduction frequency by medal status ---
ded_by_medal = (
    df_long_medal.groupby('medal_label')['has_deduction']
    .mean()
    .reindex(['Gold', 'Silver', 'Bronze', 'No Medal'])
    * 100
)
bar_colors_ded = [
    COLORS['gold'], COLORS['silver'],
    COLORS['bronze'], COLORS['no_medal']
]
axes[0].bar(
    ded_by_medal.index,
    ded_by_medal.values,
    color=bar_colors_ded,
    edgecolor='white', linewidth=0.5
)
for i, (idx, val) in enumerate(ded_by_medal.items()):
    axes[0].text(
        i, val + 0.5,
        f'{val:.1f}%',
        ha='center', va='bottom',
        fontsize=9, fontweight='bold'
    )
axes[0].set_title("% of Segments With Deductions\nby Medal Status")
axes[0].set_ylabel("% of Segments With Deductions")
axes[0].set_ylim(0, ded_by_medal.max() * 1.3)
axes[0].grid(True, alpha=0.3, axis='y')

# --- Chart 9B: Average deduction by segment and medal ---
ded_seg = (
    df_long_medal.groupby(['segment', 'medal_label'])['ded']
    .mean()
    .unstack()
    .reindex(columns=['Gold', 'Silver', 'Bronze', 'No Medal'])
)
ded_seg.plot(
    kind='bar',
    ax=axes[1],
    color=[COLORS['gold'], COLORS['silver'],
           COLORS['bronze'], COLORS['no_medal']],
    edgecolor='white',
    linewidth=0.5
)
axes[1].set_title("Average Deduction by\nSegment and Medal Status")
axes[1].set_xlabel("Segment")
axes[1].set_ylabel("Average Deduction Points")
axes[1].set_xticklabels(['Free Skate', 'Short Program'],
                         rotation=0)
axes[1].legend(title='Medal', fontsize=8)
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("outputs/eda/09_deduction_analysis.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 09_deduction_analysis.png")


# ─────────────────────────────────────────────
# EDA 10: STATISTICAL SUMMARY
# Key numbers printed to console
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("  📋 KEY STATISTICAL FINDINGS")
print("="*60)

# Finding 1: Score gap
medal_avg  = df_agg[df_agg['medal'] > 0]['total_tss'].mean()
no_med_avg = df_agg[df_agg['medal'] == 0]['total_tss'].mean()
print(f"\n  1. SCORE GAP")
print(f"     Medalist avg score    : {medal_avg:.2f}")
print(f"     Non-medalist avg score: {no_med_avg:.2f}")
print(f"     Gap                   : {medal_avg - no_med_avg:.2f} points")

# Finding 2: SP rank predictability
sp1_wins = df_agg[
    (df_agg['sp_rank'] == 1) &
    (df_agg['skater_status'] == 'COMPLETED')
]
sp1_gold = sp1_wins[sp1_wins['medal'] == 1]
print(f"\n  2. SHORT PROGRAM PREDICTABILITY")
print(f"     Times ranked 1st after SP : {len(sp1_wins)}")
print(f"     Times that led to Gold     : {len(sp1_gold)}")
print(f"     SP→Gold conversion rate    : "
      f"{len(sp1_gold)/len(sp1_wins)*100:.1f}%")

# Finding 3: Quad correlation
corr_quads = df_wc['total_quads'].corr(df_wc['total_score'])
print(f"\n  3. QUAD CORRELATION")
print(f"     Quads vs Total Score (r)  : {corr_quads:.3f}")

# Finding 4: Qualification thresholds
print(f"\n  4. QUALIFICATION THRESHOLDS (Most Recent Olympics)")
last_year = df_agg['year'].max()
for gender in ['M', 'W']:
    gender_label = "Men" if gender == 'M' else "Women"
    completed_last = df_agg[
        (df_agg['year'] == last_year) &
        (df_agg['gender'] == gender) &
        (df_agg['skater_status'] == 'COMPLETED')
    ]
    if len(completed_last) > 0:
        min_score = completed_last['total_tss'].min()
        medal_min = completed_last[
            completed_last['medal'] > 0
        ]['total_tss'].min()
        print(f"\n     {gender_label} ({last_year}):")
        print(f"       Min to compete     : {min_score:.2f}")
        print(f"       Min to medal       : {medal_min:.2f}")
        print(f"       Gap to medal zone  : "
              f"{medal_min - min_score:.2f} points")

# Finding 5: Nation type gap
trad_avg = df_agg[
    df_agg['nation_type'] == 'Traditional Power'
]['total_tss'].mean()
emrg_avg = df_agg[
    df_agg['nation_type'] == 'Emerging Nation'
]['total_tss'].mean()
print(f"\n  5. TRADITIONAL vs EMERGING NATIONS")
print(f"     Traditional power avg : {trad_avg:.2f}")
print(f"     Emerging nation avg   : {emrg_avg:.2f}")
print(f"     Gap                   : {trad_avg - emrg_avg:.2f} points")

print("\n" + "="*60)
print("  ✅ EDA COMPLETE")
print(f"  All charts saved to: outputs/eda/")
print("="*60)