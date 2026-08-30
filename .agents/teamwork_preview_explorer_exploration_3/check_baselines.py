import os
import re

docs_dir = r"/data/quyhv/oil_forecast_tail_risk/docs"
baselines = ["LSTM", "GRU", "BiLSTM-Attention", "XGBoost", "PatchTST", "DLinear", "Persistence Naive"]
output_path = r"/data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_explorer_exploration_3/baselines_mismatch.txt"

mismatches = []

for file_name in os.listdir(docs_dir):
    if not file_name.endswith(".md"):
        continue
    file_path = os.path.join(docs_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines, 1):
        for model in baselines:
            escaped_model = re.escape(model)
            # Match word boundaries but handle special characters like hyphen
            if "-" in model:
                # For BiLSTM-Attention, we check if it is matched case-insensitively but not exactly
                pattern = rf"(?i)\b{escaped_model}\b"
            else:
                pattern = rf"(?i)\b{escaped_model}\b"
            
            matches = re.finditer(pattern, line)
            for m in matches:
                matched_str = m.group(0)
                if matched_str != model:
                    mismatches.append(f"Mismatch in {file_name}:{idx}: Found '{matched_str}', expected '{model}'\nLine: {line.strip()}\n")

with open(output_path, "w", encoding="utf-8") as out:
    if mismatches:
        out.writelines(mismatches)
    else:
        out.write("No mismatches found.")
print(f"Finished. Found {len(mismatches)} mismatches.")
