import os
import re

docs_dir = r"/data/quyhv/oil_forecast_tail_risk/docs"
baseline_patterns = {
    "iTransformer": re.compile(r"\b(itransformer|i-transformer)\b", re.IGNORECASE),
    "TimesNet": re.compile(r"\b(timesnet|times-net)\b", re.IGNORECASE),
    "TimeMixer": re.compile(r"\b(timemixer|time-mixer)\b", re.IGNORECASE),
    "TFT": re.compile(r"\b(tft)\b", re.IGNORECASE),
    "N-HiTS": re.compile(r"\b(nhits|n-hits|n-hit|nhit)\b", re.IGNORECASE),
    "PatchTST": re.compile(r"\b(patchtst|patch-tst)\b", re.IGNORECASE),
    "DLinear": re.compile(r"\b(dlinear|d-linear)\b", re.IGNORECASE),
    "N-BEATS": re.compile(r"\b(nbeats|n-beats)\b", re.IGNORECASE),
    "FedFormer": re.compile(r"\b(fedformer|fed-former)\b", re.IGNORECASE),
    "Autoformer": re.compile(r"\b(autoformer|auto-former)\b", re.IGNORECASE),
    "LSTM": re.compile(r"\b(lstm)\b", re.IGNORECASE),
    "GRU": re.compile(r"\b(gru)\b", re.IGNORECASE),
    "BiLSTM-Attention": re.compile(r"\b(bilstm-attention|bilstm_attention|bilstm\s+attention)\b", re.IGNORECASE),
    "XGBoost": re.compile(r"\b(xgboost|xg-boost)\b", re.IGNORECASE),
    "Persistence Naive": re.compile(r"\b(persistence\s+naive|persistence-naive)\b", re.IGNORECASE)
}

files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]

for filename in files:
    filepath = os.path.join(docs_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        line_num = idx + 1
        for correct_name, pattern in baseline_patterns.items():
            matches = pattern.finditer(line)
            for m in matches:
                matched_text = m.group(0)
                # Check if it exactly matches the correct casing
                # For Persistence Naive, check case-insensitive match but we want exact case
                if matched_text != correct_name:
                    # Ignore the citation itself, e.g., iTransformer in bibliography is ok,
                    # but check for casing anomalies.
                    # Print match info
                    print(f"File: {filename}, Line {line_num}: Matched '{matched_text}' for expected '{correct_name}'")
