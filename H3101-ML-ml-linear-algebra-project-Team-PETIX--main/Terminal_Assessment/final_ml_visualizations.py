# Python export of the accompanying notebook; run from any directory.
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parent)
import matplotlib
matplotlib.use("Agg")
# Console equivalent of notebook display().
def display(value):
    print(value.to_string() if hasattr(value, "to_string") else value)

# Install dependencies first: python -m pip install -r requirements.txt


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set a consistent style for our charts
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

print("All libraries imported successfully!")
print("Current folder:", Path.cwd())

# Locate the analysis datasets
data_folder = Path.cwd() / "data_eda"

if not data_folder.is_dir():
    raise FileNotFoundError(
        f"Cannot find data_eda in {Path.cwd()}. Check the project folder."
    )

# Load the MS1 analysis datasets
demographics = pd.read_csv(
    data_folder / "customer_demographics_eda.csv"
)
transactions = pd.read_csv(
    data_folder / "customer_transactions_eda.csv"
)
amount_data = pd.read_csv(
    data_folder / "customer_transactions_amount_eda.csv"
)
social_media = pd.read_csv(
    data_folder / "social_media_interactions_eda.csv"
)

# Group the loaded datasets
datasets = {
    "Demographics": demographics,
    "Transactions": transactions,
    "Valid transaction amounts": amount_data,
    "Social media": social_media,
}

# Inspect dataset sizes, column names, and data types
for name, df in datasets.items():
    print(f"\n{name} — {len(df):,} rows")
    print(df.dtypes.to_string())

# Use observed ages and the separate valid-amount dataset
ages = demographics["AgeObserved"].dropna().to_numpy()
amounts = amount_data["Amount"].dropna().to_numpy()

print("Observed ages:", len(ages))
print("Valid amounts:", len(amounts))
print("Social media records:", len(social_media))

print("Ages outside 18–100:", np.sum((ages < 18) | (ages > 100)))
print("Negative amounts:", np.sum(amounts < 0))
print("Zero amounts retained:", np.sum(amounts == 0))

# Numerical summaries using NumPy
def numerical_summary(values):
    q1, q3 = np.percentile(values, [25, 75])

    return {
        "Count": len(values),
        "Mean": np.mean(values),
        "Median": np.median(values),
        "Standard deviation (sample)": np.std(values, ddof=1),
        "Variance (sample)": np.var(values, ddof=1),
        "Minimum": np.min(values),
        "Maximum": np.max(values),
        "Range": np.ptp(values),
        "25th percentile (Q1)": q1,
        "75th percentile (Q3)": q3,
        "Interquartile range (IQR)": q3 - q1,
    }

numerical_stats = pd.DataFrame({
    "Observed Age": numerical_summary(ages),
    "Valid Amount": numerical_summary(amounts),
})

display(numerical_stats.round(2))

# Create a folder for exported charts
figures_folder = Path.cwd() / "figures"
figures_folder.mkdir(exist_ok=True)

# Plot observed ages only
fig, ax = plt.subplots(figsize=(10, 6))

sns.histplot(
    x=ages,
    bins=np.arange(17.5, 73, 5),
    color="steelblue",
    edgecolor="white",
    ax=ax
)

ax.axvline(
    np.mean(ages),
    color="darkorange",
    linestyle="--",
    label=f"Mean: {np.mean(ages):.2f}"
)

ax.set_title(f"Distribution of Observed Customer Ages (n={len(ages):,})")
ax.set_xlabel("Age (years)")
ax.set_ylabel("Number of customers")
ax.legend()

fig.tight_layout()
fig.savefig(
    figures_folder / "01_observed_age_distribution.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Count observations in the same intervals used in the histogram
age_bins = np.arange(17.5, 73, 5)
counts, edges = np.histogram(ages, bins=age_bins)

age_frequency = pd.DataFrame({
    "Age interval": [
        f"{int(left + 0.5)}–{int(right - 0.5)}"
        for left, right in zip(edges[:-1], edges[1:])
    ],
    "Count": counts,
    "Percentage": np.round(counts / len(ages) * 100, 2)
})

display(age_frequency)

# Distribution of valid transaction amounts, including zeros
fig, ax = plt.subplots(figsize=(10, 6))

sns.histplot(
    x=amounts,
    bins=20,
    color="teal",
    edgecolor="white",
    ax=ax
)

ax.axvline(
    np.mean(amounts),
    color="darkorange",
    linestyle="--",
    label=f"Mean: {np.mean(amounts):.2f}"
)

ax.set_title(f"Distribution of Valid Transaction Amounts (n={len(amounts):,})")
ax.set_xlabel("Transaction amount (dataset units)")
ax.set_ylabel("Number of transactions")
ax.legend()

fig.tight_layout()
fig.savefig(
    figures_folder / "02_transaction_amount_distribution.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Count transactions per product category
category_counts = (
    transactions["ProductCategory"]
    .fillna("Unknown")
    .value_counts()
)

display(pd.DataFrame({
    "Count": category_counts,
    "Percentage": (category_counts / len(transactions) * 100).round(2)
}))

# Create a horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 6))

ax.barh(
    category_counts.index,
    category_counts.values,
    color="steelblue"
)
ax.invert_yaxis()

ax.bar_label(ax.containers[0], padding=4)
ax.set_xlim(0, category_counts.max() * 1.15)
ax.set_title(f"Transaction Counts by Product Category (n={len(transactions):,})")
ax.set_xlabel("Number of transactions")
ax.set_ylabel("Product category")

fig.tight_layout()
fig.savefig(
    figures_folder / "03_product_category_counts.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Use only records with valid amounts
plot_data = amount_data.copy()
plot_data["ProductCategory"] = (
    plot_data["ProductCategory"].fillna("Unknown")
)

# Show the supporting counts and statistics
category_summary = (
    plot_data.groupby("ProductCategory")["Amount"]
    .agg(["count", "median", "mean"])
    .sort_values("median", ascending=False)
)

display(category_summary.round(2))

# Compare amount distributions
fig, ax = plt.subplots(figsize=(10, 6))

sns.boxplot(
    data=plot_data,
    x="Amount",
    y="ProductCategory",
    order=category_summary.index,
    color="lightblue",
    whis=1.5,
    ax=ax
)

ax.set_title(
    f"Transaction Amounts by Product Category (n={len(plot_data):,})"
)
ax.set_xlabel("Transaction amount (dataset units)")
ax.set_ylabel("Product category")

fig.tight_layout()
fig.savefig(
    figures_folder / "04_amount_by_product_category.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Check potential outliers within each product category
outlier_results = []

for category, group in plot_data.groupby("ProductCategory"):
    values = group["Amount"].to_numpy()
    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    flagged = (values < lower) | (values > upper)

    outlier_results.append({
        "Product category": category,
        "Lower fence": lower,
        "Upper fence": upper,
        "Potential outliers": np.sum(flagged)
    })

display(pd.DataFrame(outlier_results).round(2))

# Convert exported date strings back into dates
transactions["TransactionDate"] = pd.to_datetime(
    transactions["TransactionDate"],
    errors="coerce"
)

print("Total transaction records:", len(transactions))
print("Missing or unparseable dates:",
      transactions["TransactionDate"].isna().sum())
print("Earliest date:", transactions["TransactionDate"].min())
print("Latest date:", transactions["TransactionDate"].max())

# Count records by month
monthly_counts = (
    transactions.dropna(subset=["TransactionDate"])
    .groupby(transactions["TransactionDate"].dt.to_period("M"))
    .size()
)

display(monthly_counts.rename("Transaction count").to_frame())

# Inspect dates outside the main concentration of records
outside_main_period = transactions.loc[
    (transactions["TransactionDate"] < "2022-07-01")
    | (transactions["TransactionDate"] >= "2024-07-01"),
    ["TransactionID", "TransactionDate"]
].sort_values("TransactionDate")

display(outside_main_period)
print("Records outside the main period:", len(outside_main_period))

# Compare the flagged records with their original Excel dates
raw_transactions = pd.read_excel(
    Path.cwd() / "data_raw"
    / "customer_transactions_contaminated.xlsx"
)

raw_date_check = raw_transactions[
    ["TransactionID", "TransactionDate"]
].rename(columns={"TransactionDate": "OriginalDate"})

date_comparison = outside_main_period.merge(
    raw_date_check,
    on="TransactionID",
    how="left"
)

# Display original values as text for inspection
date_comparison["OriginalDate"] = (
    date_comparison["OriginalDate"].astype(str)
)

display(date_comparison.drop_duplicates())

# Include every month, even those with no recorded transactions
all_months = pd.period_range(
    transactions["TransactionDate"].min().to_period("M"),
    transactions["TransactionDate"].max().to_period("M"),
    freq="M"
)

monthly_counts = monthly_counts.reindex(all_months, fill_value=0)

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    monthly_counts.index.to_timestamp(),
    monthly_counts.values,
    marker="o",
    markersize=4,
    color="steelblue"
)

ax.set_title(
    f"Recorded Transactions by Month (n={monthly_counts.sum():,})"
)
ax.set_xlabel("Month")
ax.set_ylabel("Number of recorded transactions")
ax.set_ylim(bottom=0)

fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(
    figures_folder / "05_monthly_transaction_counts.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# Inspect social media fields
print("Social media columns:")
print(social_media.columns.tolist())

# Inspect platform and grouped sentiment counts
for column in ["Platform", "SentimentGrouped"]:
    print(f"\n{column}:")
    display(
        social_media[column]
        .fillna("Unknown")
        .value_counts()
        .rename("Count")
        .to_frame()
    )

# Count sentiment groups within each platform
sentiment_counts = pd.crosstab(
    social_media["Platform"].fillna("Unknown"),
    social_media["SentimentGrouped"].fillna("Unknown")
).reindex(
    index=["Instagram", "Twitter", "Facebook", "Unknown"],
    columns=["Positive", "Neutral", "Negative", "Unknown"],
    fill_value=0
)

# Each platform row totals 100%
sentiment_percent = sentiment_counts.div(
    sentiment_counts.sum(axis=1), axis=0
) * 100

display(sentiment_counts)

fig, ax = plt.subplots(figsize=(10, 6))

sns.heatmap(
    sentiment_percent,
    annot=True,
    fmt=".1f",
    cmap="Blues",
    vmin=0,
    vmax=100,
    linewidths=0.5,
    cbar_kws={"label": "Percentage within platform"},
    ax=ax
)

ax.set_title("Sentiment Composition Within Each Platform (%)")
ax.set_xlabel("Grouped sentiment")
ax.set_ylabel("Platform")

fig.tight_layout()
fig.savefig(
    figures_folder / "06_sentiment_by_platform_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Verify that demographics has one record per customer
print(
    "Duplicate demographic CustomerIDs:",
    demographics["CustomerID"].duplicated().sum()
)

# Link valid amounts to observed customer ages
age_amount = amount_data.merge(
    demographics[["CustomerID", "AgeObserved"]],
    on="CustomerID",
    how="left",
    validate="many_to_one",
    indicator=True
)

print("Valid-amount records:", len(amount_data))
print("Records after linking:", len(age_amount))
print("No matching demographic record:",
      (age_amount["_merge"] == "left_only").sum())
print("Matched but observed age unavailable:",
      ((age_amount["_merge"] == "both")
       & age_amount["AgeObserved"].isna()).sum())

# Keep records with observed ages for the scatter plot
age_amount = age_amount.dropna(subset=["AgeObserved", "Amount"]).copy()
print("Records available for scatter plot:", len(age_amount))

# Calculate the descriptive linear correlation using NumPy
age_amount_r = np.corrcoef(
    age_amount["AgeObserved"].to_numpy(),
    age_amount["Amount"].to_numpy()
)[0, 1]

print(f"Pearson correlation: {age_amount_r:.4f}")
print("Unique customers:", age_amount["CustomerID"].nunique())

# Each point represents one transaction
fig, ax = plt.subplots(figsize=(10, 6))

sns.scatterplot(
    data=age_amount,
    x="AgeObserved",
    y="Amount",
    alpha=0.35,
    s=25,
    linewidth=0,
    color="steelblue",
    ax=ax
)

ax.set_title(
    f"Observed Customer Age vs Transaction Amount "
    f"(n={len(age_amount):,} transactions)"
)
ax.set_xlabel("Observed age (years)")
ax.set_ylabel("Transaction amount (dataset units)")

fig.tight_layout()
fig.savefig(
    figures_folder / "07_age_vs_transaction_amount.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Check exported chart files
chart_files = sorted(figures_folder.glob("*.png"))

print("Exported charts:", len(chart_files))
for file in chart_files:
    print(file.name)
