import os
import sys
import subprocess
import argparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config import SEEDS, ALL_HORIZONS

SOTA_MODELS = ['TimesNet', 'iTransformer', 'TimeMixer', 'TFT', 'NHits']

def run_sota_baselines():
    parser = argparse.ArgumentParser(description="Run SOTA Baselines Multi-seed Benchmark")
    parser.add_argument('--type', type=str, choices=['XANG', 'DAU', 'all'], default='all', help="Target type")
    parser.add_argument('--horizon', type=int, default=0, help="Horizon (0 = all, or 1,3,5,7,10,60)")
    parser.add_argument('--protocol', type=str, default='walkforward', help="Protocol name")
    parser.add_argument('--seeds', type=str, default='all', help="Comma-separated seed list or 'all'")
    args = parser.parse_args()
    
    targets = ['XANG', 'DAU'] if args.type == 'all' else [args.type]
    horizons = ALL_HORIZONS if args.horizon == 0 else [args.horizon]
    
    if args.seeds == 'all':
        seeds = SEEDS
    else:
        seeds = [int(s.strip()) for s in args.seeds.split(',')]
        
    print(f"Starting SOTA Baselines walkforward benchmark...")
    print(f"Models: {SOTA_MODELS}")
    print(f"Targets: {targets}")
    print(f"Horizons: {horizons}")
    print(f"Seeds: {seeds}")
    
    for seed in seeds:
        for model in SOTA_MODELS:
            for target in targets:
                for h in horizons:
                    cmd = [
                        sys.executable, 'scripts/train_unified.py',
                        '--type', target,
                        '--model', model,
                        '--horizon', str(h),
                        '--protocol', args.protocol,
                        '--seed', str(seed)
                    ]
                    print(f"\nExecuting SOTA training: {' '.join(cmd)}")
                    subprocess.run(cmd, cwd=PROJECT_ROOT)

if __name__ == '__main__':
    run_sota_baselines()
