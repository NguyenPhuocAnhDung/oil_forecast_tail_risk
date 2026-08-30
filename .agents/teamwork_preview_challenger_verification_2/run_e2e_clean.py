import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

project_root = r"/data/quyhv/oil_forecast_tail_risk"
target_dir = os.path.join(project_root, "results_v4", "walkforward", "GUMNet", "XANG_H3_seed42")
backup_dir = os.path.join(project_root, "results_v4", "walkforward", "GUMNet", "XANG_H3_seed42_backup")

# Step 1: Backup if exists
has_backup = False
if os.path.exists(target_dir):
    print(f"Renaming {target_dir} -> {backup_dir} for clean testing...")
    shutil.move(target_dir, backup_dir)
    has_backup = True
else:
    print(f"No existing results folder found at {target_dir}")

try:
    # Step 2: Run e2e test
    print("Running: python scripts/e2e_test.py")
    result = subprocess.run(
        [sys.executable, "scripts/e2e_test.py"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    print("\n--- stdout ---")
    print(result.stdout)
    print("--- stderr ---")
    print(result.stderr)
    print(f"Exit code: {result.returncode}")
    
    if result.returncode == 0 and "completed without errors!" in result.stdout:
        print("\nEnd-to-End run succeeded and actually executed training!")
    else:
        print("\nEnd-to-End run failed or did not execute as expected.")
        
finally:
    # Step 3: Cleanup test outputs and restore backup
    if os.path.exists(target_dir):
        print(f"Removing generated test directory {target_dir}...")
        shutil.rmtree(target_dir)
        
    if has_backup:
        print(f"Restoring {backup_dir} -> {target_dir}...")
        shutil.move(backup_dir, target_dir)
        print("Restore complete.")
