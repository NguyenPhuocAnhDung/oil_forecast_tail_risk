import os
import sys
import subprocess
import argparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

ABLATION_VARIANTS = [
    'coupled',             # Huấn luyện chung 4 mặt hàng
    'bspline_kan',         # Thay Wavelet-KAN bằng B-spline-KAN
    'no_residual',         # Bỏ cơ chế Residual Scaling
    'no_gpr',              # Cắt bỏ đặc trưng GPR
    'equal_gating'         # Trọng số Gating bằng nhau
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', type=str, choices=ABLATION_VARIANTS + ['all'], default='all')
    parser.add_argument('--type', type=str, choices=['XANG', 'DAU', 'all'], default='all')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    
    variants_to_run = ABLATION_VARIANTS if args.variant == 'all' else [args.variant]
    
    # Ablation Table 10: run representative horizons per target
    targets = ['XANG', 'DAU'] if args.type == 'all' else [args.type]
    horizons = [3, 10, 60]  # Short, medium, long — representative

    for variant in variants_to_run:
        print(f"\n{'='*60}\nRUNNING ABLATION: {variant.upper()}\n{'='*60}")
        env = os.environ.copy()
        env['GUMNET_ABLATION'] = variant
        
        # Use unique model name so results don't overwrite main GUMNet results
        # e.g. GUMNet_bspline_kan, GUMNet_no_residual, etc.
        ablation_model_name = f'GUMNet_{variant}'

        for target in targets:
            for h in horizons:
                cmd = [sys.executable, 'scripts/train_unified.py',
                       '--type', target,
                       '--model', ablation_model_name,
                       '--horizon', str(h),
                       '--protocol', 'walkforward',
                       '--seed', str(args.seed)]
                print(f"Executing: {' '.join(cmd)}")
                subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)

if __name__ == '__main__':
    main()
