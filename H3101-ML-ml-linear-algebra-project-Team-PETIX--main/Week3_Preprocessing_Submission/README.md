# Week 3 – FinMark Preprocessing and Exploratory Data Analysis

This folder contains the revised preprocessing workflow, data exports, conflict audits, and exploratory data analysis (EDA) for the FinMark Corporation machine-learning project.

## Files and Folders

- `data_raw/`: Original Excel datasets, preserved without modification.
- `data_cleaned/`: Cleaned datasets with original-value fields and quality flags. Records with conflicting primary IDs remain available for review.
- `data_audit/`: Conflicting-ID records with source Excel row numbers and original values.
- `data_eda/`: Analysis datasets excluding all records with unresolved primary-ID conflicts.
- `finmark_preprocessing_workflow.ipynb`: Executed notebook containing preprocessing, validation, exports, and EDA results.

## Dataset Counts

Each raw dataset contains 3,200 rows and 6 columns.

| Dataset | Exact duplicates removed | Cleaned rows | Cleaned columns | Rows flagged for ID conflicts | EDA rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| Customer Demographics | 177 | 3,023 | 11 | 46 | 2,977 |
| Customer Transactions | 185 | 3,015 | 9 | 30 | 2,985 |
| Social Media Interactions | 180 | 3,020 | 10 | 40 | 2,980 |

Cleaned row counts equal raw rows minus exact duplicates. EDA row counts equal cleaned rows minus all rows flagged for primary-ID conflicts.

## Cleaning Decisions

- Remove exact duplicate rows.
- Preserve conflicting primary-ID records and export them for review rather than arbitrarily retaining the first occurrence.
- Strip whitespace and use `Unknown` for missing categorical values.
- Preserve original age values and flag missing, nonnumeric, or out-of-range ages.
- Apply a provisional whole-number age range of 18–100, subject to business confirmation.
- Impute screened or missing ages with a median of 45 and flag imputed values.
- Preserve zero transaction amounts. Do not impute missing or nonnumeric amounts.
- Retain negative amounts with review flags because their business meaning requires confirmation.
- Preserve original sentiment categories and add a separate grouped sentiment column.
- Parse mixed date formats using a day-first assumption, which requires confirmation against source conventions.

## EDA Scope

- Categorical frequency counts include missing or `Unknown` values and reconcile with the relevant EDA dataset size.
- Main age statistics use 2,615 observed ages. A separate comparison includes the 362 imputed ages.
- Amount statistics use 2,642 numeric, nonnegative transactions, including 28 zero-value transactions.
- The amount subset excludes 310 missing or nonnumeric amounts and 33 negative amounts from the 2,985-row transaction EDA dataset.
- PaymentMethod and ProductCategory are examined using cross-tabulation, row percentages, and Cramér's V.

## Limitations and Future ML Work

Primary-ID conflicts remain unresolved. Excluding them from EDA may affect the results.

A small Cramér's V describes weak observed association; it does not prove independence or absence of collinearity. Descriptive statistics do not establish that the data is unbiased or free from leakage.

Before modeling, confirm business rules, review unresolved records, define the prediction target and data split, and validate encoding, imputation, scaling, bias, and leakage. Any learned preprocessing must be fitted using training data only.
