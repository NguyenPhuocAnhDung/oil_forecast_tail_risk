import os
import re

files_to_check = [
    r"/data/quyhv/oil_forecast_tail_risk/docs/research_os/stage2_conceptual_gaps.md",
    r"/data/quyhv/oil_forecast_tail_risk/docs/research_os/stage5_hypothesis_design.md",
    r"/data/quyhv/oil_forecast_tail_risk/docs/research_os/stage7_baseline_taxonomy.md",
    r"/data/quyhv/oil_forecast_tail_risk/docs/research_os/stage9_failure_diagnostics.md",
    r"/data/quyhv/oil_forecast_tail_risk/docs/research_os/stage10_econometric_validation.md"
]

def check_latex_balance(filepath):
    print(f"Checking {os.path.basename(filepath)}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check $$ blocks (display math)
    display_math_blocks = re.findall(r'\$\$(.*?)\$\$', content, re.DOTALL)
    print(f"  Found {len(display_math_blocks)} display math blocks ($$).")
    
    # Count occurrence of $$ to check if any are unclosed
    double_dollar_count = content.count('$$')
    if double_dollar_count % 2 != 0:
        print(f"  [ERROR] Unbalanced '$$' in {filepath} (total count: {double_dollar_count})")
        return False
        
    # Check $ blocks (inline math)
    # Be careful to exclude $$ from $ checks
    content_no_double = content.replace('$$', '')
    single_dollar_count = content_no_double.count('$')
    if single_dollar_count % 2 != 0:
        print(f"  [ERROR] Unbalanced '$' in {filepath} (total count: {single_dollar_count})")
        return False
        
    print(f"  {os.path.basename(filepath)} is balanced and valid.")
    return True

all_valid = True
for fp in files_to_check:
    if os.path.exists(fp):
        if not check_latex_balance(fp):
            all_valid = False
    else:
        print(f"[ERROR] File does not exist: {fp}")
        all_valid = False

if all_valid:
    print("SUCCESS: All files have balanced LaTeX blocks.")
else:
    print("FAILED: Math syntax errors detected.")
