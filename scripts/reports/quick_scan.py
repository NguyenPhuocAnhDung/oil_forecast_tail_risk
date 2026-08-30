import os, glob
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
print(f'=== QUÉT TIẾN ĐỘ ĐỊNH KỲ ({now.strftime("%H:%M:%S UTC %d/%m/%Y")}) ===')

results_dir = 'results_v4/walkforward'
if not os.path.exists(results_dir):
    print("No results directory found.")
    exit(0)

models = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]

xang_counts = {h: {s: 0 for s in [42, 123, 777, 2025, 9999]} for h in ['H1','H3','H5','H7','H10','H20','H60']}
dau_counts = {h: {s: 0 for s in [42, 123, 777, 2025, 9999]} for h in ['H1','H3','H5','H7','H10','H20','H60']}

for m in models:
    m_dir = os.path.join(results_dir, m)
    for run in os.listdir(m_dir):
        if not os.path.isfile(os.path.join(m_dir, run, 'results.json')):
            continue
        parts = run.split('_')
        if len(parts) >= 3:
            target = parts[0]
            horizon = parts[1]
            seed_str = parts[2]
            if seed_str.startswith('seed'):
                try:
                    s = int(seed_str[4:])
                    if target == 'XANG' and horizon in xang_counts and s in xang_counts[horizon]:
                        xang_counts[horizon][s] += 1
                    elif target == 'DAU' and horizon in dau_counts and s in dau_counts[horizon]:
                        dau_counts[horizon][s] += 1
                except ValueError:
                    pass

print('\n--- TIẾN ĐỘ XĂNG (5 SEEDS) ---')
tot_xang = 0
for h in ['H1','H3','H5','H7','H10','H20','H60']:
    c = xang_counts[h]
    s_tot = sum(c.values())
    tot_xang += s_tot
    print(f'  {h:3s}: {s_tot:3d}/235 ({(s_tot/235)*100:5.1f}%) | {c}')
print(f'-> Tổng XĂNG: {tot_xang}/1645 ({(tot_xang/1645)*100:.2f}%)')

print('\n--- TIẾN ĐỘ DẦU (5 SEEDS) ---')
tot_dau = 0
for h in ['H1','H3','H5','H7','H10','H20','H60']:
    c = dau_counts[h]
    s_tot = sum(c.values())
    tot_dau += s_tot
    print(f'  {h:3s}: {tot:3d}/235 ({(tot_dau/235)*100:5.1f}%) | {c}')
print(f'-> Tổng DẦU: {tot_dau}/1645 ({(tot_dau/1645)*100:.2f}%)')

grand = tot_xang + tot_dau
print(f'\n-> TOÀN BỘ DỰ ÁN: {grand}/3290 ({(grand/3290)*100:.2f}%)')
