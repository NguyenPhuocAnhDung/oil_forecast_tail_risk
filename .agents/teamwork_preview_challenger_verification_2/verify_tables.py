import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

docs_dir = r"/data/quyhv/oil_forecast_tail_risk/docs"

def parse_tables_from_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tables = []
    current_table = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith('|') and line_stripped.endswith('|'):
            current_table.append((i, line))
        else:
            if current_table:
                has_separator = False
                for idx, row in current_table:
                    if re.match(r'^\s*\|(?:\s*:?-+:?\s*\|)+\s*$', row.strip()):
                        has_separator = True
                        break
                if has_separator:
                    tables.append((current_table[0][0], current_table))
                current_table = []
    if current_table:
        has_separator = False
        for idx, row in current_table:
            if re.match(r'^\s*\|(?:\s*:?-+:?\s*\|)+\s*$', row.strip()):
                has_separator = True
                break
        if has_separator:
            tables.append((current_table[0][0], current_table))
            
    return tables

def clean_cell(cell):
    # Remove markdown bold/italics
    cell = re.sub(r'\*\*|\*', '', cell)
    return cell.strip()

def parse_plus_minus(val_str):
    # Matches something like "90.7 ± 0.7"
    val_str = val_str.replace('%', '')
    match = re.match(r'^([\d\.]+)\s*±\s*([\d\.]+)$', val_str.strip())
    if match:
        return float(match.group(1)), float(match.group(2))
    return None

def parse_slash(val_str):
    # Matches something like "0.89 / 1.18 / 1.04%" or "0.89 / 1.18 / 1.04"
    val_str = val_str.replace('%', '')
    parts = val_str.split('/')
    if len(parts) == 3:
        try:
            return float(parts[0].strip()), float(parts[1].strip()), float(parts[2].strip())
        except ValueError:
            return None
    return None

def is_strictly_intermediate(h10, h20, h60):
    return min(h10, h60) < h20 < max(h10, h60)

# Run the validation
target_tables_count = 0
failures = []

for file_name in sorted(os.listdir(docs_dir)):
    if not file_name.endswith('.md'):
        continue
    file_path = os.path.join(docs_dir, file_name)
    tables = parse_tables_from_markdown(file_path)
    
    for start_line, table_rows in tables:
        # Get header
        header_row = table_rows[0][1]
        headers = [clean_cell(c) for c in header_row.split('|')[1:-1]]
        
        # Check if this is a target table (has H10, H20, H60 in some form)
        has_h10 = any('h10' in h.lower() for h in headers)
        has_h20 = any('h20' in h.lower() for h in headers)
        has_h60 = any('h60' in h.lower() for h in headers)
        
        if not (has_h10 and has_h20 and has_h60):
            continue
            
        target_tables_count += 1
        print(f"\n--- Verifying Table {target_tables_count} in {file_name} at line {start_line} ---")
        print(f"Headers: {headers}")
        
        # Find column indices for H10, H20, H60
        idx_h10, idx_h20, idx_h60 = None, None, None
        for i, h in enumerate(headers):
            h_lower = h.lower()
            if 'h10' in h_lower:
                idx_h10 = i
            elif 'h20' in h_lower:
                idx_h20 = i
            elif 'h60' in h_lower:
                idx_h60 = i
                
        print(f"Indices: H10={idx_h10}, H20={idx_h20}, H60={idx_h60}")
        
        # Parse data rows (skipping header and separator)
        for row_idx, (orig_line_num, row_str) in enumerate(table_rows[2:]):
            cells = [clean_cell(c) for c in row_str.split('|')[1:-1]]
            model_name = cells[0]
            
            val_h10_str = cells[idx_h10]
            val_h20_str = cells[idx_h20]
            val_h60_str = cells[idx_h60]
            
            # Try to parse as plus-minus format
            pm_h10 = parse_plus_minus(val_h10_str)
            pm_h20 = parse_plus_minus(val_h20_str)
            pm_h60 = parse_plus_minus(val_h60_str)
            
            if pm_h10 and pm_h20 and pm_h60:
                mean_10, std_10 = pm_h10
                mean_20, std_20 = pm_h20
                mean_60, std_60 = pm_h60
                
                # Check mean
                if not is_strictly_intermediate(mean_10, mean_20, mean_60):
                    msg = f"Mean check failed for {model_name} in {file_name}:{orig_line_num}. H10={mean_10}, H20={mean_20}, H60={mean_60}"
                    failures.append(msg)
                    print(f"  [FAIL] {msg}")
                else:
                    print(f"  [PASS] {model_name} mean: {mean_10} -> {mean_20} -> {mean_60}")
                    
                # Check std (but standard deviations of 0.0 might be equal)
                if std_10 == 0.0 and std_20 == 0.0 and std_60 == 0.0:
                    print(f"  [INFO] {model_name} std is 0.0 for all (deterministic model). Skipping strict comparison.")
                elif not is_strictly_intermediate(std_10, std_20, std_60):
                    msg = f"Std check failed for {model_name} in {file_name}:{orig_line_num}. H10={std_10}, H20={std_20}, H60={std_60}"
                    failures.append(msg)
                    print(f"  [FAIL] {msg}")
                else:
                    print(f"  [PASS] {model_name} std: {std_10} -> {std_20} -> {std_60}")
                    
            else:
                # Try to parse as slash format
                sl_h10 = parse_slash(val_h10_str)
                sl_h20 = parse_slash(val_h20_str)
                sl_h60 = parse_slash(val_h60_str)
                
                if sl_h10 and sl_h20 and sl_h60:
                    for metric_idx, (m_10, m_20, m_60) in enumerate(zip(sl_h10, sl_h20, sl_h60)):
                        metric_name = ["MAE", "RMSE", "MAPE"][metric_idx]
                        if not is_strictly_intermediate(m_10, m_20, m_60):
                            msg = f"{metric_name} check failed for {model_name} in {file_name}:{orig_line_num}. H10={m_10}, H20={m_20}, H60={m_60}"
                            failures.append(msg)
                            print(f"  [FAIL] {msg}")
                        else:
                            print(f"  [PASS] {model_name} {metric_name}: {m_10} -> {m_20} -> {m_60}")
                else:
                    msg = f"Could not parse values for row '{model_name}' in {file_name}:{orig_line_num}. H10='{val_h10_str}', H20='{val_h20_str}', H60='{val_h60_str}'"
                    failures.append(msg)
                    print(f"  [FAIL] {msg}")

print(f"\n--- Summary ---")
print(f"Total target tables validated: {target_tables_count}")
print(f"Total failures found: {len(failures)}")
if failures:
    sys.exit(1)
else:
    sys.exit(0)
