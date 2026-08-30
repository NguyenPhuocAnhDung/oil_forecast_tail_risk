# ML Best Practices Skill (Local Copy)

## Introduction
CRITICAL RULE: You MUST use this skill whenever the task involves any machine learning tasks or data analysis.
Use this skill if the user's prompt or requirements mention any of the following:
* Clustering
* Classification
* Regression
* Time series forecasting
* Statistical testing
* Model comparison
* ML
* Data analysis

## Time Series Forecasting & Comparing ML Models
Guidelines from the skill:
- Understand the schema and field descriptions.
- Visualize the target feature over time at a reasonable granularity.
- Always perform a chronological split on the data to create training, validation, and test sets.
- Test for stationarity.
- Evaluate the validation performance with error metrics.
- Retrain the selected model on the test and validation sets.
- Establish baselines: define a naive baseline (majority class/mean) and a simple ML baseline (e.g., Logistic/Linear Regression).
- Ensure rigorous validation: use identical, fixed data splits for all models.
- If data is temporal, use chronological splits for validation.
- Select and report metrics beyond accuracy (e.g., F1-Score, PR-AUC, MAE, RMSE) that reflect business impact.
- Use bootstrapping to calculate 95% confidence intervals for key metrics to determine statistical significance.
- Perform slice-based error analysis.
- Inspect and compare confusion matrices, residual plots, and calibration curves.
- Evaluate operational trade-offs.
- Assess interpretability using tools like SHAP or LIME where transparency is required.

## Essential ML Practices
- **Strict Featurization Ordering**: ALWAYS split the dataset into training and test data BEFORE fitting preprocessing pipelines.
- **Handling Missing or NULL Values**: ALWAYS check for and handle missing and NULL values.
