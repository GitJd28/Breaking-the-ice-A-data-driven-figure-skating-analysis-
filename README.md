# ⛸️ Break the Ice - What Actually Separates Olympic Figure Skating Champions

**[Live dashboard](https://breaktheice.streamlit.app/)**

I used to skate as a kid, and I've been watching figure skating at every Olympics since, and I always wondered what actually separates the skaters on the podium from the ones just off it. Is it the technical content? The short program? Consistency over a single big jump? So I pulled 20 years of ISU competition data and built a model to find out, rather than go on commentary-booth intuition.

Along the way, the same framework turned out to answer a second question I was curious about: for a country with no Olympic figure skating history at all, what would it actually, numerically take to get from zero to competitive? I use India as the worked example for that  not because the project is about India, but because it's the case I know best and it's a clean test of whether the model's benchmarks hold up for a program starting from scratch.

## What I found

- **The short program matters more than I expected.** SP rank alone accounts for over half of what predicts a final medal outcome in my model. Free skate rarely overturns a bad short program  the margin for a comeback is smaller than the narrative around "the free skate is where champions are made" suggests.
- **The gap between medalists and everyone else isn't subtle.** Medal winners score roughly 90 points higher than non-medalists on average a consistent, structural gap rather than a close-run thing decided by a handful of tenths.
- **The sport has visibly changed since 2014.** Post-quad-era, technical content correlates with final score far more strongly (r = 0.70) than it used to. Artistry hasn't disappeared from scoring, but it's no longer what separates the podium from 4th place the way it once did.
- **Applying this to a country with zero Olympic history actually works.** Once you have real thresholds for "what a top-10 finish requires" vs. "what a medal requires," you can back out a concrete target for any federation building a program from scratch I use India as the test case below.

## The data

| Dataset | Source | Rows | Covers |
|---|---|---|---|
| Olympic Singles (aggregate) | Kaggle / ISU | 357 | 2006–2026, 75 nations |
| Olympic Singles (long format) | Kaggle / ISU | 646 | Segment-level SP/FS detail |
| World Championship Scores (men) | Kaggle / ISU | 453 | 2005–2024, element-level |

357 unique Olympic performances is not a huge dataset, and I don't want to pretend otherwise  that's part of why I pulled in the Worlds data too, both to get more training signal and to sanity-check that patterns from Olympics-only data actually hold at a larger scale.

## From raw data to insights

Cleaning: dropped incomplete performances (withdrawals, disqualifications upto 49 rows), standardized column names across three differently-formatted sources, fixed a few dozen null free-skate ranks from skaters who didn't advance past the short program.

Feature engineering: built out things like technical-score share of total, SP→FS score momentum, rank movement, and a pre/post-2014 "quad era" flag, since the raw scores alone don't tell you much about *why* someone medaled.

Modeling: trained both a Random Forest and a Logistic Regression to predict medal probability, using stratified 5-fold cross-validation (medals are rare about a 9:1 imbalance so I used class weighting rather than just accuracy). Random Forest ended up as the better model (0.983 test ROC-AUC vs. 0.979 CV for logistic regression), and its feature importances are what the "Performance DNA" page in the dashboard is built on.

## Applying it: a development framework, with India as the worked example

The model gives you real thresholds what score gets you to top-10, what gets you to a medal, how that's shifted since the quad era started. Those thresholds are useful to *any* federation building a program, not just one country's. To make that concrete, I applied it to India, which has no Olympic singles history to date, and backed out four realistic development stages: first Olympic qualification → competing both segments credibly → cracking the top 10 → real medal contention, each with a score target and a rough timeline.

I picked India because it's the cleanest test case for "starting from literally zero" but the same four-tier framework applies to any program at a similar stage. Kazakhstan is a useful real-world reference point here too: their first Olympic figure skating gold came in 2026, and their federation's investment trajectory over the prior two decades is a reasonable proxy for what closing this kind of gap actually takes in practice, timeline-wise.

## 🚀 Access the Dashboard

### Live Dashboard (Recommended)

**➡️ [breaktheice.streamlit.app](https://breaktheice.streamlit.app/)**

Zero installation. Just click and explore all 6 interactive pages.

---

### Run Locally (For Developers)


**Prerequisites:** Python 3.11+ · [uv package manager](https://github.com/astral-sh/uv) · Git

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/figure-skating-analytics.git
cd figure-skating-analytics

# Set up environment
uv venv
uv pip install -r requirements.txt

# Reproduce the full pipeline
uv run python analysis.py # Data cleaning
uv run python eda.py # Generate EDA charts
uv run python model.py # Train predictive models

# Launch the dashboard
uv run streamlit run dashboard/app.py
```

Opens at `http://localhost:8501`

## Dashboard pages

1. **Overview** - the global picture: nation dominance, score distributions, the medal gap
2. **Nation Analysis** - pick any two nations and compare their skating profiles head to head
3. **Performance DNA** - what the model says actually predicts a medal
4. **Quad Revolution** - how the sport's scoring priorities shifted post-2014
5. **Medal Predictor** - plug in any skater's scores, get a live medal probability
6. **Development Framework** - the four-tier benchmark model, applied to India as a worked example

## Stack

Python 3.11, pandas/numpy/scipy for the data work, scikit-learn for modeling, Plotly (+ matplotlib/seaborn for static EDA), Streamlit for the dashboard, deployed on Streamlit Community Cloud. `uv` for environment management.

## Project structure

```
figure-skating-project/
├── data/
│ ├── raw/ # original CSVs
│ └── processed/ # cleaned versions
├── models/ # trained model + scaler artifacts
├── outputs/
│ ├── eda/ # EDA charts
│ └── model/ # model evaluation charts
├── dashboard/
│ ├── app.py
│ ├── components/
│ └── pages/
├── analysis.py
├── eda.py
├── model.py
└── requirements.txt
```

## Future Scope

- Extending beyond singles to pairs and ice dance.
- Bringing in real infrastructure data  rink counts, federation funding  rather than relying on Kazakhstan as the only real-world reference point.
- Running the same development-framework model against a few other emerging programs (not just India) to see how well the four-tier benchmarks generalize. 

## Author

**Janhavi Deo**  [GitHub](https://github.com/GitJd28) · [live dashboard](https://breaktheice.streamlit.app/)

Data from the ISU via Kaggle contributors.
