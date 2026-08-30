import os
import sys
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config import SEEDS

def run_experiment(args):
    target, model, h, protocol, seed, step, total_steps = args
    # Check if results.json already exists to avoid redundant runs
    from config import RESULTS_DIR
    output_dir = os.path.join(RESULTS_DIR, protocol, model, f'{target}_H{h}_seed{seed}')
    if os.path.exists(os.path.join(output_dir, 'results.json')):
        print(f"[Step {step}/{total_steps}] Seed {seed}, Horizon {h} already completed. Skipping.")
        return
        
    print(f"[Step {step}/{total_steps}] Starting Seed {seed}, Horizon {h}...")
    cmd = [
        sys.executable, 'scripts/train_unified.py',
        '--type', target,
        '--model', model,
        '--horizon', str(h),
        '--protocol', protocol,
        '--seed', str(seed)
    ]
    # Explicitly remove GUMNET_TEST_MODE to guarantee full-scale training
    env = os.environ.copy()
    env.pop('GUMNET_TEST_MODE', None)
    subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
    print(f"[Step {step}/{total_steps}] Finished Seed {seed}, Horizon {h}!")

def main():
    horizons = [1, 3, 5, 7]
    target = 'XANG'
    model = 'GUMNet'
    protocol = 'walkforward'
    
    print(f"Executing GUM-Net multi-seed walk-forward experiments on Gasoline ({target}) in parallel...")
    total_steps = len(SEEDS) * len(horizons)
    
    tasks = []
    step = 0
    for seed in SEEDS:
        for h in horizons:
            step += 1
            tasks.append((target, model, h, protocol, seed, step, total_steps))
            
    # Run with 5 parallel workers
    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_experiment, task) for task in tasks]
        for future in as_completed(futures):
            future.result()
            
    print("All GUM-Net Gasoline walk-forward multi-seed experiments completed!")

if __name__ == '__main__':
    main()
