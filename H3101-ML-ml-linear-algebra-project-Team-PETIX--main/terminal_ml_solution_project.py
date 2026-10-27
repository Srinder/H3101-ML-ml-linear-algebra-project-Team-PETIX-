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
from pathlib import Path

print("Pandas version:", pd.__version__)
print("Setup successful.")

# Locate the FinMark project folders
project_folder = Path.cwd()

# This handles whether the notebook starts from the project or notebooks folder
if project_folder.name == "notebooks":
    project_folder = project_folder.parent

raw_data_folder = project_folder / "data_raw"
cleaned_data_folder = project_folder / "data_cleaned"

print("Project folder:", project_folder)
print("Raw data folder exists:", raw_data_folder.exists())
print("Cleaned data folder exists:", cleaned_data_folder.exists())

print("\nFiles found:")
for file in raw_data_folder.glob("*.xlsx"):
    print("-", file.name)

# Load the three original datasets
demographics_df = pd.read_excel(
    raw_data_folder / "customer_demographics_contaminated.xlsx"
)

transactions_df = pd.read_excel(
    raw_data_folder / "customer_transactions_contaminated.xlsx"
)

social_media_df = pd.read_excel(
    raw_data_folder / "social_media_interactions_contaminated.xlsx"
)

print("Datasets loaded successfully.")
print("Customer demographics:", demographics_df.shape)
print("Customer transactions:", transactions_df.shape)
print("Social media interactions:", social_media_df.shape)

# Preview the first five records of each dataset

print("CUSTOMER DEMOGRAPHICS")
display(demographics_df.head())

print("CUSTOMER TRANSACTIONS")
display(transactions_df.head())

print("SOCIAL MEDIA INTERACTIONS")
display(social_media_df.head())

# Store the datasets in a dictionary for easier inspection
datasets = {
    "Customer Demographics": demographics_df,
    "Customer Transactions": transactions_df,
    "Social Media Interactions": social_media_df
}

# Create an overall data-quality summary
summary_records = []

for dataset_name, df in datasets.items():
    summary_records.append({
        "Dataset": dataset_name,
        "Rows": df.shape[0],
        "Columns": df.shape[1],
        "Exact Duplicate Rows": df.duplicated().sum(),
        "Total Missing Values": df.isna().sum().sum()
    })

quality_summary = pd.DataFrame(summary_records)
display(quality_summary)

# Check missing values in each column
for dataset_name, df in datasets.items():
    print(f"\n{dataset_name}")
    print(df.isnull().sum())

# Check the current data type of every column
for dataset_name, df in datasets.items():
    print(f"\n{dataset_name}")
    print(df.dtypes)

# Convert Age temporarily to identify invalid entries
age_numeric = pd.to_numeric(
    demographics_df["Age"],
    errors="coerce"
)

# Find non-missing Age entries that cannot be converted into numbers
invalid_age_entries = demographics_df.loc[
    demographics_df["Age"].notna() & age_numeric.isna(),
    "Age"
].value_counts()

print("Invalid non-numeric Age values:")
print(invalid_age_entries)

print("\nNumeric Age range:")
print("Minimum:", age_numeric.min())
print("Maximum:", age_numeric.max())

print("\nSuspicious Age values:")
print(
    age_numeric[
        (age_numeric < 18) | (age_numeric > 100)
    ].value_counts().sort_index()
)

print("\nGender values:")
print(demographics_df["Gender"].value_counts(dropna=False))

print("\nIncome level values:")
print(demographics_df["IncomeLevel"].value_counts(dropna=False))

    # Create working copies to protect the original datasets
demographics_clean = demographics_df.copy()
transactions_clean = transactions_df.copy()
social_media_clean = social_media_df.copy()

print("Rows before removing exact duplicates:")
print("Demographics:", len(demographics_clean))
print("Transactions:", len(transactions_clean))
print("Social media:", len(social_media_clean))

# Remove rows where every column is identical
demographics_clean = demographics_clean.drop_duplicates().copy()
transactions_clean = transactions_clean.drop_duplicates().copy()
social_media_clean = social_media_clean.drop_duplicates().copy()

print("\nRows after removing exact duplicates:")
print("Demographics:", len(demographics_clean))
print("Transactions:", len(transactions_clean))
print("Social media:", len(social_media_clean))

print("\nRows removed:")
print("Demographics:", len(demographics_df) - len(demographics_clean))
print("Transactions:", len(transactions_df) - len(transactions_clean))
print("Social media:", len(social_media_df) - len(social_media_clean))

# Check whether the main identifier of each dataset is still duplicated
id_checks = {
    "Customer Demographics": (demographics_clean, "CustomerID"),
    "Customer Transactions": (transactions_clean, "TransactionID"),
    "Social Media Interactions": (social_media_clean, "InteractionID")
}

id_summary = []

for dataset_name, (df, id_column) in id_checks.items():
    duplicated_mask = df.duplicated(subset=id_column, keep=False)

    id_summary.append({
        "Dataset": dataset_name,
        "ID Column": id_column,
        "Rows with Duplicated ID": duplicated_mask.sum(),
        "Number of Duplicated IDs": df.loc[
            duplicated_mask, id_column
        ].nunique()
    })

display(pd.DataFrame(id_summary))

# Display records whose primary identifiers occur more than once
duplicate_demographics = demographics_clean[
    demographics_clean.duplicated(
        subset="CustomerID",
        keep=False
    )
].sort_values("CustomerID")

duplicate_transactions = transactions_clean[
    transactions_clean.duplicated(
        subset="TransactionID",
        keep=False
    )
].sort_values("TransactionID")

duplicate_social_media = social_media_clean[
    social_media_clean.duplicated(
        subset="InteractionID",
        keep=False
    )
].sort_values("InteractionID")

print("Sample duplicated CustomerID records:")
display(duplicate_demographics.head(10))

print("Sample duplicated TransactionID records:")
display(duplicate_transactions.head(10))

print("Sample duplicated InteractionID records:")
display(duplicate_social_media.head(10))

# Preserve conflicting records for review instead of choosing the first
# Rebuild from raw data so this cell is safe to rerun
demographics_clean = demographics_df.drop_duplicates().copy()
transactions_clean = transactions_df.drop_duplicates().copy()
social_media_clean = social_media_df.drop_duplicates().copy()

conflict_records = {}
conflict_summary = []

checks = {
    "Demographics": (demographics_clean, "CustomerID"),
    "Transactions": (transactions_clean, "TransactionID"),
    "Social media": (social_media_clean, "InteractionID")
}

for name, (df, id_column) in checks.items():
    conflict_mask = df.duplicated(subset=id_column, keep=False)

    # Keep original values and row positions as review evidence
    records = df.loc[conflict_mask].copy()
    records.insert(0, "SourceExcelRow", records.index + 2)
    conflict_records[name] = records.sort_values(id_column)

    df["IDConflict"] = conflict_mask

    conflict_summary.append({
        "Dataset": name,
        "Rows retained": len(df),
        "Conflict rows": int(conflict_mask.sum()),
        "Conflicting IDs": records[id_column].nunique()
    })

display(pd.DataFrame(conflict_summary))

# Store the cleaned working datasets for another quality check
clean_datasets = {
    "Customer Demographics": demographics_clean,
    "Customer Transactions": transactions_clean,
    "Social Media Interactions": social_media_clean
}

# Display the remaining missing values after duplicate removal
for dataset_name, df in clean_datasets.items():
    print(f"\n{dataset_name}")
    print(df.isna().sum())

# Save original conflicting records for review
audit_folder = project_folder / "data_audit"
audit_folder.mkdir(parents=True, exist_ok=True)

audit_files = {
    "Demographics": "demographics_id_conflicts.csv",
    "Transactions": "transactions_id_conflicts.csv",
    "Social media": "social_media_id_conflicts.csv"
}

for name, filename in audit_files.items():
    conflict_records[name].to_csv(
        audit_folder / filename, index=False
    )

print("Conflict evidence saved to:", audit_folder)

# Convert Age and Amount temporarily for inspection
age_check = pd.to_numeric(
    demographics_clean["Age"],
    errors="coerce"
)

amount_check = pd.to_numeric(
    transactions_clean["Amount"],
    errors="coerce"
)

# Identify invalid text values
invalid_age_text = demographics_clean.loc[
    demographics_clean["Age"].notna() & age_check.isna(),
    "Age"
].value_counts()

invalid_amount_text = transactions_clean.loc[
    transactions_clean["Amount"].notna() & amount_check.isna(),
    "Amount"
].value_counts()

print("Invalid Age text:")
print(invalid_age_text)

print("\nSuspicious numeric ages:")
print(
    age_check[
        (age_check < 18) | (age_check > 100)
    ].value_counts().sort_index()
)

print("\nInvalid Amount text:")
print(invalid_amount_text)

print("\nZero or negative transaction amounts:")
print(
    amount_check[
        amount_check <= 0
    ].value_counts().sort_index()
)

# Inspect the categories, including missing values
category_checks = [
    (demographics_clean, "Gender"),
    (demographics_clean, "IncomeLevel"),
    (transactions_clean, "ProductCategory"),
    (transactions_clean, "PaymentMethod"),
    (social_media_clean, "Platform"),
    (social_media_clean, "InteractionType"),
    (social_media_clean, "Sentiment")
]

for df, column in category_checks:
    print(f"\n{column}:")
    print(df[column].value_counts(dropna=False))

# Preserve original ages so this cell is safe to rerun
if "AgeOriginal" not in demographics_clean.columns:
    demographics_clean["AgeOriginal"] = demographics_clean["Age"].copy()

original_age = demographics_clean["AgeOriginal"]
numeric_age = pd.to_numeric(original_age, errors="coerce")

# Use the existing 18–100 rule as a provisional screening rule
valid_age = (
    numeric_age.between(18, 100)
    & numeric_age.mod(1).eq(0)
)

demographics_clean["AgeStatus"] = "Observed"
demographics_clean.loc[
    original_age.isna(), "AgeStatus"
] = "Missing"
demographics_clean.loc[
    original_age.notna() & numeric_age.isna(), "AgeStatus"
] = "Non-numeric"
demographics_clean.loc[
    numeric_age.notna() & ~valid_age, "AgeStatus"
] = "Outside screening rule"

# Preserve observed ages separately for EDA
demographics_clean["AgeObserved"] = (
    numeric_age.where(valid_age).astype("Int64")
)

# Calculate the median from observed ages without conflicting IDs
median_source = demographics_clean.loc[
    ~demographics_clean["IDConflict"], "AgeObserved"
]
median_age = median_source.median()

# Record which values receive a replacement
demographics_clean["AgeImputed"] = (
    demographics_clean["AgeObserved"].isna()
)

demographics_clean["Age"] = (
    demographics_clean["AgeObserved"]
    .astype("Float64")
    .fillna(median_age)
)

# Standardize text
for column in ["CustomerID", "Gender", "Location", "IncomeLevel"]:
    demographics_clean[column] = (
        demographics_clean[column].astype("string").str.strip()
    )

demographics_clean["IncomeLevel"] = (
    demographics_clean["IncomeLevel"]
    .replace("", pd.NA)
    .fillna("Unknown")
)

demographics_clean["SignupDate"] = pd.to_datetime(
    demographics_clean["SignupDate"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

print("Original age status:")
print(demographics_clean["AgeStatus"].value_counts())

print("\nMedian used:", median_age)
print("Ages imputed:", demographics_clean["AgeImputed"].sum())
print("Missing ages after imputation:", demographics_clean["Age"].isna().sum())
print("Missing or unparseable signup dates:",
      demographics_clean["SignupDate"].isna().sum())

# Preserve original amounts so this cell is safe to rerun
if "AmountOriginal" not in transactions_clean.columns:
    transactions_clean["AmountOriginal"] = transactions_clean["Amount"].copy()

original = transactions_clean["AmountOriginal"]
numeric = pd.to_numeric(original, errors="coerce")

# Record why an amount needs review
transactions_clean["AmountStatus"] = "Numeric"
transactions_clean.loc[original.isna(), "AmountStatus"] = "Missing"
transactions_clean.loc[
    original.notna() & numeric.isna(), "AmountStatus"
] = "Non-numeric: review"
transactions_clean.loc[numeric.eq(0), "AmountStatus"] = "Zero: retained"
transactions_clean.loc[
    numeric.lt(0), "AmountStatus"
] = "Negative: review"

# Keep zero and negative numeric values; leave text amounts missing
# Do not impute amounts during this EDA revision
transactions_clean["Amount"] = numeric.round(2)

# Clean categories and identifiers
for column in [
    "ProductCategory", "PaymentMethod", "CustomerID", "TransactionID"
]:
    transactions_clean[column] = (
        transactions_clean[column].astype("string").str.strip()
    )

transactions_clean["ProductCategory"] = (
    transactions_clean["ProductCategory"]
    .replace("", pd.NA)
    .fillna("Unknown")
)

# Convert dates
transactions_clean["TransactionDate"] = pd.to_datetime(
    transactions_clean["TransactionDate"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

print("Amount handling:")
print(transactions_clean["AmountStatus"].value_counts())

print("\nMissing numeric amounts:")
print(transactions_clean["Amount"].isna().sum())

print("\nUnparseable or missing transaction dates:")
print(transactions_clean["TransactionDate"].isna().sum())

# Preserve original values before cleaning
if "PlatformOriginal" not in social_media_clean.columns:
    social_media_clean["PlatformOriginal"] = social_media_clean["Platform"].copy()

if "SentimentOriginal" not in social_media_clean.columns:
    social_media_clean["SentimentOriginal"] = social_media_clean["Sentiment"].copy()

# Clean categories and label missing or blank values
for column in ["Platform", "Sentiment"]:
    social_media_clean[column] = (
        social_media_clean[f"{column}Original"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Unknown")
    )

# Create a separate grouping while retaining sentiment intensity
social_media_clean["SentimentGrouped"] = (
    social_media_clean["Sentiment"]
    .replace({
        "Very Positive": "Positive",
        "Very Negative": "Negative"
    })
)

# Standardize other text columns
for column in ["CustomerID", "InteractionID", "InteractionType"]:
    social_media_clean[column] = (
        social_media_clean[column]
        .astype("string")
        .str.strip()
    )

# Convert dates; any failed conversions remain visible as missing
social_media_clean["InteractionDate"] = pd.to_datetime(
    social_media_clean["InteractionDate"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

print("Missing values after cleaning:")
print(social_media_clean.isna().sum())

print("\nPlatform counts:")
print(social_media_clean["Platform"].value_counts())

print("\nSentiment counts—original categories:")
print(social_media_clean["Sentiment"].value_counts())

print("\nSentiment counts—grouped categories:")
print(social_media_clean["SentimentGrouped"].value_counts())

print("\nRows flagged for conflicting interaction IDs:")
print(social_media_clean["IDConflict"].sum())

# Validate retained datasets, including records flagged for review
clean_datasets = {
    "Customer Demographics": demographics_clean,
    "Customer Transactions": transactions_clean,
    "Social Media Interactions": social_media_clean
}

dataset_settings = {
    "Customer Demographics": ("CustomerID", "SignupDate"),
    "Customer Transactions": ("TransactionID", "TransactionDate"),
    "Social Media Interactions": ("InteractionID", "InteractionDate")
}

validation_summary = []

for dataset_name, df in clean_datasets.items():
    id_column, date_column = dataset_settings[dataset_name]

    repeated_id_rows = df.duplicated(id_column, keep=False)
    missing_id = df[id_column].isna() | df[id_column].eq("").fillna(False)

    validation_summary.append({
        "Dataset": dataset_name,
        "Rows retained": len(df),
        "Columns": len(df.columns),
        "Exact duplicates": int(df.duplicated().sum()),
        "Missing/blank primary IDs": int(missing_id.sum()),
        "Repeated-ID rows": int(repeated_id_rows.sum()),
        "Flagged conflict rows": int(df["IDConflict"].sum()),
        "Conflict flags match repeated IDs": bool(
            df["IDConflict"].eq(repeated_id_rows).all()
        ),
        "Missing dates": int(df[date_column].isna().sum()),
        "Date dtype valid": bool(
            pd.api.types.is_datetime64_any_dtype(df[date_column])
        )
    })

display(pd.DataFrame(validation_summary))

# Create EDA views that exclude unresolved primary-ID conflicts.
# All flagged records remain in the retained datasets and audit files.
demographics_eda = demographics_clean.loc[
    ~demographics_clean["IDConflict"]
].copy()

transactions_eda = transactions_clean.loc[
    ~transactions_clean["IDConflict"]
].copy()

social_media_eda = social_media_clean.loc[
    ~social_media_clean["IDConflict"]
].copy()

eda_datasets = {
    "Customer Demographics": demographics_eda,
    "Customer Transactions": transactions_eda,
    "Social Media Interactions": social_media_eda
}

eda_summary = []

for dataset_name, df in eda_datasets.items():
    id_column, _ = dataset_settings[dataset_name]

    eda_summary.append({
        "Dataset": dataset_name,
        "Retained rows": len(clean_datasets[dataset_name]),
        "Excluded conflict rows": int(
            clean_datasets[dataset_name]["IDConflict"].sum()
        ),
        "EDA rows": len(df),
        "Repeated primary IDs in EDA": int(
            df[id_column].duplicated().sum()
        )
    })

print("EDA row reconciliation:")
display(pd.DataFrame(eda_summary))

# Keep missing observed ages separate from imputed ages
observed_age = demographics_eda["AgeObserved"].dropna()

print("\nAge checks in the EDA view:")
print("Observed ages available:", len(observed_age))
print(
    "Observed ages meet the provisional 18–100 screening rule:",
    bool(
        (
            observed_age.between(18, 100)
            & observed_age.mod(1).eq(0)
        ).all()
    )
)
print(
    "Rows with imputed ages:",
    int(demographics_eda["AgeImputed"].sum())
)

# Zero amounts are retained; missing and negative values remain visible
print("\nAmount status in the EDA view:")
print(transactions_eda["AmountStatus"].value_counts(dropna=False))

print(
    "Missing numeric amounts:",
    int(transactions_eda["Amount"].isna().sum())
)
print(
    "Zero amounts retained:",
    int(transactions_eda["Amount"].eq(0).sum())
)
print(
    "Negative amounts requiring review:",
    int(transactions_eda["Amount"].lt(0).sum())
)

# Separate view for nonnegative purchase-amount statistics.
# This is an analysis filter, not deletion from the retained data.
transactions_amount_eda = transactions_eda.loc[
    transactions_eda["Amount"].notna()
    & transactions_eda["Amount"].ge(0)
].copy()

print(
    "Rows available for nonnegative amount statistics:",
    len(transactions_amount_eda)
)
print(
    "Rows excluded from amount statistics:",
    len(transactions_eda) - len(transactions_amount_eda)
)

# Check CustomerID links against all retained demographic records
demographic_customer_ids = demographics_clean["CustomerID"].dropna()

print("\nCustomerID connection checks—retained datasets:")
for name, df in {
    "Transactions": transactions_clean,
    "Social media": social_media_clean
}.items():
    missing_customer = (
        df["CustomerID"].isna()
        | df["CustomerID"].eq("").fillna(False)
    )
    unmatched_customer = (
        ~missing_customer
        & ~df["CustomerID"].isin(demographic_customer_ids)
    )

    print(
        f"{name}: "
        f"{int(missing_customer.sum())} missing/blank CustomerIDs; "
        f"{int(unmatched_customer.sum())} rows with unmatched CustomerIDs"
    )

print(
    "\nUnresolved ID conflicts and amount issues remain documented. "
    "These checks do not establish that the data is fully ready for ML."
)

# Create output folders
cleaned_data_folder.mkdir(parents=True, exist_ok=True)

eda_folder = project_folder / "data_eda"
eda_folder.mkdir(parents=True, exist_ok=True)

# Retained datasets include unresolved records and review flags
retained_exports = {
    "customer_demographics_cleaned.csv": demographics_clean,
    "customer_transactions_cleaned.csv": transactions_clean,
    "social_media_interactions_cleaned.csv": social_media_clean
}

# EDA datasets exclude unresolved primary-ID conflicts
eda_exports = {
    "customer_demographics_eda.csv": demographics_eda,
    "customer_transactions_eda.csv": transactions_eda,
    "social_media_interactions_eda.csv": social_media_eda,
    "customer_transactions_amount_eda.csv": transactions_amount_eda
}

export_summary = []

for folder, exports in [
    (cleaned_data_folder, retained_exports),
    (eda_folder, eda_exports)
]:
    for filename, df in exports.items():
        output_path = folder / filename

        df.to_csv(
            output_path,
            index=False,
            date_format="%Y-%m-%d"
        )

        # Verify that the saved file has the expected dimensions
        saved_df = pd.read_csv(output_path)
        assert saved_df.shape == df.shape, (
            f"Export dimensions do not match: {filename}"
        )

        export_summary.append({
            "Folder": folder.name,
            "File": filename,
            "Rows": len(saved_df),
            "Columns": len(saved_df.columns)
        })

print("Exports saved and dimensions verified:")
display(pd.DataFrame(export_summary))

print("\nRetained dataset folder:", cleaned_data_folder)
print("EDA dataset folder:", eda_folder)

# EDA: Compare observed ages with ages after median imputation
df_demo = pd.read_csv(
    eda_folder / "customer_demographics_eda.csv"
)

observed_age = pd.to_numeric(
    df_demo["AgeObserved"], errors="coerce"
).dropna()

age_after_imputation = pd.to_numeric(
    df_demo["Age"], errors="coerce"
).dropna()

age_summary = []

for label, ages in {
    "Observed ages only": observed_age,
    "After median imputation": age_after_imputation
}.items():
    age_summary.append({
        "Age data": label,
        "Count": len(ages),
        "Mean": ages.mean(),
        "Median": ages.median(),
        "Mode(s)": ages.mode().tolist()
    })

print("Age statistics—unresolved ID conflicts excluded:")
display(pd.DataFrame(age_summary).round(2))

print(
    "\nAges filled by imputation:",
    int(df_demo["AgeObserved"].isna().sum())
)

print(
    "\nUse observed ages for the main age-distribution findings. "
    "Imputation can increase the frequency of the median age, "
    "so the imputed mode should not be interpreted as the "
    "most common observed customer age."
)

# EDA: Age spread before and after median imputation
df_demo = pd.read_csv(
    eda_folder / "customer_demographics_eda.csv"
)

age_spread_summary = []

for label, column in {
    "Observed ages only": "AgeObserved",
    "After median imputation": "Age"
}.items():
    ages = pd.to_numeric(
        df_demo[column], errors="coerce"
    ).dropna()

    age_spread_summary.append({
        "Age data": label,
        "Count": len(ages),
        "Standard deviation": ages.std(),
        "Variance": ages.var(),
        "Minimum": ages.min(),
        "Maximum": ages.max(),
        "Range": ages.max() - ages.min(),
        "Q1": ages.quantile(0.25),
        "Q3": ages.quantile(0.75),
        "IQR": ages.quantile(0.75) - ages.quantile(0.25)
    })

print("Age spread—unresolved ID conflicts excluded:")
display(pd.DataFrame(age_spread_summary).round(2))

print(
    "\nStandard deviation and variance use the sample formulas "
    "(ddof=1). Use the observed-age row for the main findings; "
    "median imputation can reduce the measured spread."
)

# EDA: Category frequencies and transaction amount distribution
df_demo = pd.read_csv(
    eda_folder / "customer_demographics_eda.csv"
)
df_trans = pd.read_csv(
    eda_folder / "customer_transactions_eda.csv"
)
df_social = pd.read_csv(
    eda_folder / "social_media_interactions_eda.csv"
)
df_amount = pd.read_csv(
    eda_folder / "customer_transactions_amount_eda.csv"
)

# Display category counts and percentages, including missing values
def show_frequencies(df, columns):
    for column in columns:
        counts = df[column].value_counts(dropna=False)

        frequency_table = pd.DataFrame({
            "Count": counts,
            "Percent": counts / len(df) * 100
        })

        print(f"\n{column} — denominator: {len(df)} rows")
        print(
            "Distinct nonmissing categories:",
            df[column].nunique(dropna=True)
        )

        # Limit the display for high-cardinality columns such as Location
        display(frequency_table.head(15).round(2))

        if len(frequency_table) > 15:
            print(
                f"Showing the 15 most frequent categories "
                f"out of {len(frequency_table)} categories."
            )

        assert int(counts.sum()) == len(df), (
            f"Category counts do not reconcile for {column}"
        )

print("DEMOGRAPHICS — unresolved ID conflicts excluded")
show_frequencies(
    df_demo,
    ["Gender", "Location", "IncomeLevel"]
)

print("\nTRANSACTIONS — unresolved ID conflicts excluded")
show_frequencies(
    df_trans,
    ["PaymentMethod", "ProductCategory"]
)

# Amount statistics exclude missing, nonnumeric, and negative amounts
amounts = pd.to_numeric(df_amount["Amount"], errors="coerce")

assert amounts.notna().all() and amounts.ge(0).all(), (
    "The amount subset contains missing or negative values."
)

amount_summary = pd.DataFrame([{
    "Count": len(amounts),
    "Mean": amounts.mean(),
    "Median": amounts.median(),
    "Standard deviation": amounts.std(),
    "Minimum": amounts.min(),
    "Q1": amounts.quantile(0.25),
    "Q3": amounts.quantile(0.75),
    "Maximum": amounts.max(),
    "IQR": amounts.quantile(0.75) - amounts.quantile(0.25),
    "Skewness": amounts.skew(),
    "Zero amounts": int(amounts.eq(0).sum())
}])

print("\nNONNEGATIVE TRANSACTION AMOUNT STATISTICS")
display(amount_summary.round(2))

print(
    "Transaction rows excluded from amount statistics:",
    len(df_trans) - len(df_amount)
)

# Numeric bins provide additional distribution evidence
amount_bins = pd.cut(amounts, bins=10, include_lowest=True)
bin_counts = amount_bins.value_counts(sort=False)

print("\nAmount distribution — 10 equal-width bins:")
display(pd.DataFrame({
    "Count": bin_counts,
    "Percent": bin_counts / len(amounts) * 100
}).round(2))

print("\nSOCIAL MEDIA — unresolved ID conflicts excluded")
show_frequencies(
    df_social,
    ["Platform", "InteractionType", "Sentiment", "SentimentGrouped"]
)

print(
    "\nUnknown identifies undetermined categories. "
    "SentimentGrouped combines intensity levels for analysis; "
    "Sentiment retains those levels."
)

print(
    "\nThese results describe the selected EDA subsets. "
    "Mean/median similarity alone does not establish uniformity "
    "or absence of bias."
)

# EDA: Relationships and remaining data-quality limitations
df_demo = pd.read_csv(
    eda_folder / "customer_demographics_eda.csv"
)
df_trans = pd.read_csv(
    eda_folder / "customer_transactions_eda.csv"
)
df_social = pd.read_csv(
    eda_folder / "social_media_interactions_eda.csv"
)

# Report missing values and Unknown separately
for name, df in {
    "Demographics": df_demo,
    "Transactions": df_trans,
    "Social media": df_social
}.items():
    print(f"\n{name}: {len(df)} rows, {len(df.columns)} columns")

    quality_table = pd.DataFrame({
        "Missing": df.isna().sum(),
        "Unknown": df.eq("Unknown").sum()
    })

    display(
        quality_table.loc[
            quality_table.sum(axis=1).gt(0)
        ]
    )

print(
    "\nMissing values in Original columns preserve source evidence. "
    "Missing AgeObserved values identify ages unavailable under "
    "the provisional screening rule."
)

# Cross-tabulation includes Unknown as a separate category
relationship_data = df_trans[
    ["PaymentMethod", "ProductCategory"]
].copy()

relationship_data = relationship_data.fillna("Missing")

cross_tab = pd.crosstab(
    relationship_data["PaymentMethod"],
    relationship_data["ProductCategory"]
)

print("\nPaymentMethod vs ProductCategory — counts:")
display(cross_tab)

assert int(cross_tab.to_numpy().sum()) == len(df_trans)

print("\nProductCategory percentages within each PaymentMethod:")
display(
    cross_tab.div(cross_tab.sum(axis=1), axis=0)
    .mul(100)
    .round(2)
)

# Descriptive association measure: Cramer's V
# Expected counts under independence are calculated from the margins.
n = cross_tab.to_numpy().sum()
row_totals = cross_tab.sum(axis=1).to_numpy()
column_totals = cross_tab.sum(axis=0).to_numpy()

expected = (
    row_totals[:, None] * column_totals[None, :] / n
)

chi_square = (
    (cross_tab.to_numpy() - expected) ** 2 / expected
).sum()

dimension = min(
    cross_tab.shape[0] - 1,
    cross_tab.shape[1] - 1
)

cramers_v = (
    (chi_square / (n * dimension)) ** 0.5
    if dimension > 0 else float("nan")
)

print("\nDescriptive association:")
print(f"Rows included: {n}")
print(f"Cramer's V: {cramers_v:.4f}")

print(
    "\nCramer's V describes association in this selected subset: "
    "values nearer 0 indicate weaker association. "
    "It does not prove independence or establish that model "
    "features are free from collinearity."
)

print(
    "\nFuture ML validation still requires a defined target, "
    "appropriate train/test splitting, training-only fitting of "
    "imputation and encoding, and checks for leakage and bias. "
    "Unresolved conflicts and amount issues require further review."
)


