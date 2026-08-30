import ast

naive_maes = {
    'DAU': {1: 1.130, 3: 1.458, 5: 1.904, 10: 2.704, 60: 5.387},
    'XANG': {1: 0.811, 3: 1.155, 5: 1.363, 10: 1.753, 60: 5.895}
}

naive_results = {
    'DAU': {
        1: ['DAU', 'Persistence', '1.130', '1.470', '1.30', '0.9237'],
        3: ['DAU', 'Persistence', '1.458', '1.858', '1.68', '0.8777'],
        5: ['DAU', 'Persistence', '1.904', '2.486', '2.20', '0.7817'],
        10: ['DAU', 'Persistence', '2.704', '3.326', '3.13', '0.4575'],
        60: ['DAU', 'Persistence', '5.387', '6.595', '6.07', '0.3075']
    },
    'XANG': {
        1: ['XANG', 'Persistence', '0.811', '1.090', '1.06', '0.9130'],
        3: ['XANG', 'Persistence', '1.155', '1.542', '1.51', '0.8251'],
        5: ['XANG', 'Persistence', '1.363', '1.866', '1.78', '0.7452'],
        10: ['XANG', 'Persistence', '1.753', '2.403', '2.26', '0.5256'],
        60: ['XANG', 'Persistence', '5.895', '7.195', '7.11', '0.3053']
    }
}

with open('tables_dump.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('Table '):
        parts = line.split(': ', 1)
        if len(parts) == 2:
            table_idx = int(parts[0].replace('Table ', ''))
            table_data = ast.literal_eval(parts[1].strip())
            
            # Tables 7 to 11 are H1, H3, H5, H10, H60
            horizons = {7: 1, 8: 3, 9: 5, 10: 10, 11: 60}
            if table_idx in horizons:
                h = horizons[table_idx]
                
                # Add MASE column to header
                new_table = []
                header = table_data[0]
                if 'MASE' not in header:
                    header.insert(5, 'MASE')
                new_table.append(header)
                
                # We also need to insert Persistence rows. We'll insert them after DAU block and XANG block.
                # Actually, let's just append them to the end of DAU and XANG blocks, then sort or just insert them.
                
                # Process existing models
                for row in table_data[1:]:
                    target = row[0]
                    mae = float(row[2])
                    mase = mae / naive_maes[target][h]
                    
                    if len(row) == 6:
                        row.insert(5, f"{mase:.3f}")
                    new_table.append(row)
                
                # Append Persistence DAU
                persist_dau = naive_results['DAU'][h]
                if len(persist_dau) == 6:
                    persist_dau.insert(5, "1.000")
                new_table.append(persist_dau)
                
                # Append Persistence XANG
                persist_xang = naive_results['XANG'][h]
                if len(persist_xang) == 6:
                    persist_xang.insert(5, "1.000")
                new_table.append(persist_xang)
                
                # Sort rows so DAU and XANG are grouped, and Persistence is at the top of the group
                def sort_key(x):
                    if x[0] == 'Mục tiêu': return (0, 0)
                    target_val = 1 if x[0] == 'DAU' else 2
                    model_val = 0 if x[1] == 'Persistence' else 1
                    return (target_val, model_val)
                
                new_table_sorted = sorted(new_table[1:], key=sort_key)
                new_table = [new_table[0]] + new_table_sorted
                
                new_lines.append(f"{parts[0]}: {new_table}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open('tables_dump.txt', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
