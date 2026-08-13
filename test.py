# Add to eda.py or run separately
import pandas as pd

df_agg = pd.read_csv("data/processed/agg_clean.csv")


# Find zero or near-zero scores
zero_rows = df_agg[df_agg['total_tss'] <= 10]

print(f"Rows with total_tss <= 10: {len(zero_rows)}")
print()
print(zero_rows[['year', 'gender', 'skater', 
                  'nation', 'total_tss', 
                  'skater_status', 'final_rank']].to_string())

print("SCORE RANGES BY GENDER")
print("="*60)
for gender in ['M', 'W']:
    label = "Men" if gender == 'M' else "Women"
    subset = df_agg[df_agg['gender'] == gender]
    medalists = subset[subset['medal'] > 0]
    non_medal = subset[subset['medal'] == 0]

    print(f"\n  {label}:")
    print(f"    Overall avg score    : "
          f"{subset['total_tss'].mean():.2f}")
    print(f"    Medalist avg score   : "
          f"{medalists['total_tss'].mean():.2f}")
    print(f"    Non-medalist avg     : "
          f"{non_medal['total_tss'].mean():.2f}")
    print(f"    Min score to compete : "
          f"{subset['total_tss'].min():.2f}")
    print(f"    Max score recorded   : "
          f"{subset['total_tss'].max():.2f}")

    