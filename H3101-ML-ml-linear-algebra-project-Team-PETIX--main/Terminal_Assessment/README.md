# MO-IT162 Terminal Assessment - ML Solution Presentation - H3101 Team PETIX

## Project scope
FinMark data preprocessing, exploratory data analysis, seven visualizations, and a proposed purchase-propensity solution. No predictive model has been trained or evaluated. Proposed targets, classifiers, temporal evaluation and governance controls in the presentation are future work.

## Files and execution order
1. `terminal_ml_solution_project.ipynb` - preprocessing, audit, and EDA.
2. `final_ml_visualizations.ipynb` - seven charts and their interpretations.
3. Matching `.py` files - complete executable exports of the notebook code.
4. `data_raw/` - three unchanged source Excel workbooks.
5. `data_cleaned/` - cleaned records retaining flagged identity conflicts.
6. `data_audit/` - original conflict records and source Excel row references.
7. `data_eda/` - conflict-excluded analysis datasets; separate valid-amount subset.
8. `figures/` - seven regenerated chart PNGs.
9. `presentation/` - supplied 17-slide presentation PDF, unchanged.
10. `validation/` - execution logs, environment, validation findings and review checklist.

## Run
Use Python 3.11 or newer. From this Terminal_Assessment folder:

```bash
python -m pip install -r requirements.txt
python terminal_ml_solution_project.py
python final_ml_visualizations.py
```

Alternatively launch Jupyter Lab from this folder and run the notebooks in the order above. Installation cells have been replaced with comments; install dependencies first. Python exports locate their own folder automatically. Notebooks expect this folder as their working directory. Scripts regenerate CSVs and charts; the raw Excel files remain unchanged. `validation/validated_environment.txt` records the exact versions used for this validation; requirements.txt gives compatible installation ranges.

## Analysis counts and interpretation
- Demographic / transaction / social EDA records: 2,977 / 2,985 / 2,980 (8,942 rows across tables, not unique people).
- Observed ages: 2,615; 362 EDA ages imputed. Age summaries and histogram use observed ages.
- Valid amounts: 2,642 nonmissing, nonnegative values including 28 zeros.
- Age-amount sample: 2,299 transactions, 1,510 customers; Pearson r approximately 0.0315.
- Raw records: 9,600; exact duplicates removed: 542; unresolved conflict rows excluded from EDA: 116.
- Mixed dates are parsed day-first; source date convention and complete capture periods still require confirmation.
- Current outputs are descriptive; no accuracy, deployment, causation, or predictive-performance claim is made.

## Final submission
Complete `validation/TEAM_REVIEW_CHECKLIST.md` using actual team feedback and approval. Upload this whole folder to the existing GitHub repository as `Terminal_Assessment`, preserving the folder structure. Commit message: `Finalized Terminal Assessment project submission`. Confirm the notebook, dataset, chart and PDF links open on GitHub, then paste the repository URL into Camu. Extract the ZIP before uploading; uploading only a ZIP does not expose reviewable repository files.

Earlier Week 3 and Week 7 folders may remain as milestone history. Do not copy duplicate milestone folders into this final folder. No historical repository files were deleted by this package preparation.
