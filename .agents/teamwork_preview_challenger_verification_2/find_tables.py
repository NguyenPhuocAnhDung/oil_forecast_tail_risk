import os
import re
import sys

# Reconfigure stdout to use utf-8 to avoid encoding issues in Windows console
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
                    tables.append(current_table)
                current_table = []
    if current_table:
        has_separator = False
        for idx, row in current_table:
            if re.match(r'^\s*\|(?:\s*:?-+:?\s*\|)+\s*$', row.strip()):
                has_separator = True
                break
        if has_separator:
            tables.append(current_table)
            
    return tables

for file_name in os.listdir(docs_dir):
    if file_name.endswith('.md'):
        file_path = os.path.join(docs_dir, file_name)
        tables = parse_tables_from_markdown(file_path)
        if tables:
            print(f"File: {file_name} has {len(tables)} tables")
            for t_idx, table in enumerate(tables):
                headers = [c.strip() for c in table[0][1].split('|') if c.strip()]
                print(f"  Table {t_idx+1} at line {table[0][0]}: Headers: {headers}")
