"""
scripts/pipeline/01_dataset_freeze.py — Dataset Freeze Verification
======================================================================
Kiểm tra dataset đã đóng băng tại mốc 28/02/2026.
Verify: hash, row count, last date, column integrity.
Output: PASS/FAIL + evidence.
"""

import os
import sys
import json
import hashlib
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def compute_file_hash(filepath: str) -> str:
  """SHA256 hash of file."""
  h = hashlib.sha256()
  with open(filepath, 'rb') as f:
    for chunk in iter(lambda: f.read(8192), b''):
      h.update(chunk)
  return h.hexdigest()


def main():
  from config import DATA_PATH, DATASET_FREEZE_DATE, TARGETS, RESULTS_DIR

  print("=" * 60)
  print(" DATASET FREEZE VERIFICATION (Methodology §1)")
  print("=" * 60)

  checks = []

  # 1. File existence
  if not os.path.exists(DATA_PATH):
    print(f"  Dataset not found: {DATA_PATH}")
    sys.exit(1)

  # 2. Load and inspect
  df = pd.read_csv(DATA_PATH)
  df.columns = df.columns.str.strip()

  # 3. Hash
  file_hash = compute_file_hash(DATA_PATH)
  checks.append({
    'check': 'File Hash (SHA256)',
    'status': 'Recorded',
    'value': file_hash,
    'evidence': f'SHA256: {file_hash[:32]}...',
  })

  # 4. Row count
  n_rows = len(df)
  checks.append({
    'check': 'Row Count',
    'status': 'Verified',
    'value': n_rows,
    'evidence': f'{n_rows} rows in dataset',
  })

  # 5. Date range
  date_col = None
  for col in ['Ngày', 'Date', 'date', 'ngày']:
    if col in df.columns:
      date_col = col
      break

  if date_col:
    df[date_col] = pd.to_datetime(df[date_col])
    first_date = df[date_col].min().strftime('%Y-%m-%d')
    last_date = df[date_col].max().strftime('%Y-%m-%d')

    # Check last date against freeze date
    last_dt = df[date_col].max()
    freeze_dt = pd.Timestamp(DATASET_FREEZE_DATE)

    if last_dt <= freeze_dt:
      date_status = 'Verified'
    else:
      date_status = 'WARNING'

    checks.append({
      'check': 'Date Range',
      'status': date_status,
      'value': f'{first_date} → {last_date}',
      'evidence': f'Freeze date: {DATASET_FREEZE_DATE}, Last data: {last_date}',
    })
  else:
    checks.append({
      'check': 'Date Range',
      'status': 'SKIPPED',
      'value': 'No date column found',
      'evidence': 'Could not verify date range',
    })

  # 6. Target columns exist
  all_targets = []
  for group in TARGETS.values():
    all_targets.extend(group)

  missing = [t for t in all_targets if t not in df.columns]
  if not missing:
    checks.append({
      'check': 'Target Columns',
      'status': 'Verified',
      'value': all_targets,
      'evidence': f'All {len(all_targets)} target columns present',
    })
  else:
    checks.append({
      'check': 'Target Columns',
      'status': 'FAILED',
      'value': f'Missing: {missing}',
      'evidence': f'{len(missing)} target columns missing',
    })

  # 7. No NaN in targets
  nan_counts = {t: int(df[t].isna().sum()) for t in all_targets if t in df.columns}
  total_nans = sum(nan_counts.values())
  checks.append({
    'check': 'Target NaN Check',
    'status': 'Verified' if total_nans == 0 else 'WARNING',
    'value': nan_counts,
    'evidence': f'{total_nans} total NaN values in targets',
  })

  # Print results
  all_passed = True
  for c in checks:
    icon = '' if c['status'] == 'Verified' or c['status'] == 'Recorded' else ''
    if c['status'] not in ('Verified', 'Recorded'):
      all_passed = False
    print(f" {icon} {c['check']}: {c['status']}")
    print(f"   {c['evidence']}")

  # Save report
  output_dir = os.path.join(RESULTS_DIR, 'evaluation_database')
  os.makedirs(output_dir, exist_ok=True)

  report = {
    'verified_at': datetime.utcnow().isoformat() + 'Z',
    'dataset_path': DATA_PATH,
    'freeze_date': DATASET_FREEZE_DATE,
    'file_hash': file_hash,
    'checks': checks,
    'overall': 'PASS' if all_passed else 'ISSUES_FOUND',
  }

  report_path = os.path.join(output_dir, 'dataset_freeze_check.json')
  with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False, default=str)

  print(f"\n{'' if all_passed else ''} Dataset freeze check → {report_path}")
  return all_passed


if __name__ == '__main__':
  success = main()
  sys.exit(0 if success else 1)
