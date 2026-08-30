# ML Best Practices

I want to read a story about the data, not just run code. Ensure every code cell
is followed by a markdown cell analyzing the results. End the notebook with a
summary comprehensively answering the prompt.

...
[Content identical to C:\Users\anhdu\.gemini\config\skills\ml-best-practices\SKILL.md]
- **Strict Featurization Ordering**: For supervised learning **ALWAYS** split the dataset into training and test data **BEFORE** fitting preprocessing pipelines (e.g. scaling, encoding). Fit the pipelines on the training data and test data independently.
- **Handling Missing or NULL Values**: **ALWAYS** check for and handle missing and NULL values. First, analyze their frequency. Then, decide whether to keep them, drop them or impute them with a contextually appropriate value, and explain your reasoning.
