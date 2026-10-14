# Week 7 – ML Solution Data Visualizations
## FinMark Corporation | Team PETIX

This folder contains our Week 7 visualization homework supporting
Milestone 2. It builds on the cleaned datasets and exploratory data
analysis completed in Milestone 1.

## Main Notebook

[finmark_visualization_workflow.ipynb](finmark_visualization_workflow.ipynb)

The notebook uses Pandas, NumPy, Matplotlib, and Seaborn to calculate
numerical summaries, create seven visualizations, and explain the
findings and their relevance to future machine learning.

## Supporting Files

- `data_eda/` – Analysis datasets excluding unresolved primary-ID conflicts.
- `data_raw/` – Original datasets used for source verification.
- `data_cleaned/` – Supporting cleaned datasets from Milestone 1.
- `data_audit/` – Supporting records of unresolved ID conflicts.
- `figures/` – Seven exported visualization PNG files.

## Analysis Subsets

- Customer demographics: 2,977 records.
- Customer transactions: 2,985 records.
- Social media interactions: 2,980 records.
- Age statistics and histogram: 2,615 observed ages, excluding imputed ages.
- Amount analysis: 2,642 nonmissing, nonnegative amounts, including 28 zeros.
- Age–amount relationship: 2,299 transactions from 1,510 matched customers
  with observed ages and valid amounts.

## Visualizations

1. Observed customer age distribution.
2. Transaction amount distribution.
3. Transaction counts by product category.
4. Transaction amount distributions by product category.
5. Monthly recorded transaction counts.
6. Sentiment percentages within each platform.
7. Observed customer age versus transaction amount.

Each chart includes an interpretation in the notebook.

## Running the Notebook

1. Download or clone the repository.
2. Open this Week 7 folder as the working folder in VS Code or Jupyter.
3. Install the required libraries:

   pip install pandas numpy matplotlib seaborn openpyxl

4. Open `finmark_visualization_workflow.ipynb`.
5. Select a Python kernel and run all cells in order.

Keep `data_eda/` and `data_raw/` beside the notebook.
Running the notebook saves the charts to `figures/`.

## Interpretation Limits

The findings describe the available analysis records. Unknown categories
are retained as unavailable information. Uneven date coverage limits
conclusions about business growth, decline, or seasonality.

No transaction amounts were flagged by the within-category 1.5 × IQR
outlier rule; this does not guarantee that all records are accurate.

The visualizations do not establish causation or demonstrate predictive
model performance.
