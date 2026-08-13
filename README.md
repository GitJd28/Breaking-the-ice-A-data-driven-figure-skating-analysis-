# Breaking the Ice: A Data-Driven Figure Skating Analysis

An end-to-end data science project analyzing competitive figure skating using historical Olympic and World Championship data.

The project combines data cleaning, exploratory data analysis, statistical insights, machine learning, and an interactive Streamlit dashboard to understand what drives figure skating performance and medal outcomes.

---

## Project Overview

Figure skating performance is influenced by several factors including technical difficulty, program components, consistency, deductions, and evolving scoring trends.

This project explores these factors using historical figure skating data and answers questions such as:

- Which nations have historically dominated figure skating?
- How have skating scores evolved over time?
- How important are Technical Element Scores (TES) and Program Component Scores (PCS)?
- How has the introduction of quadruple jumps changed competitive performance?
- Which nations are emerging in international figure skating?
- Can medal outcomes be predicted using machine learning?
- What can India learn from successful and emerging figure skating nations?

---

## Project Structure

```text
Breaking-the-ice-A-data-driven-figure-skating-analysis/
│
├── analysis.py                 # Data cleaning and preprocessing
├── eda.py                      # Exploratory data analysis
├── model.py                    # Machine learning model development
├── test.py                     # Model/testing utilities
│
├── dashboard/
│   ├── app.py                  # Streamlit application
│   ├── components/
│   │   ├── charts.py           # Reusable visualization functions
│   │   └── data_loader.py      # Dashboard data loading
│   │
│   └── pages/
│       ├── 1_Overview.py
│       ├── 2_Nation_Analysis.py
│       ├── 3_Performance_DNA.py
│       ├── 4_Quad_Revolution.py
│       ├── 5_Medal_Predictor.py
│       └── 6_India_Roadmap.py
│
├── data/
│   ├── raw/                    # Original datasets
│   └── processed/              # Cleaned datasets
│
├── models/
│   ├── feature_list.csv
│   ├── lr_medal_predictor.pkl
│   ├── rf_medal_predictor.pkl
│   └── scaler.pkl
│
└── outputs/
    ├── eda/                    # EDA visualizations
    └── model/                  # Model evaluation outputs
