import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def run_command(cmd, description):
    print(f"\n{'='*70}")
    print(f" {description}")
    print(f"{'='*70}")
    result = subprocess.run([sys.executable] + cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"ERROR: {description} failed.")
        sys.exit(1)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str, choices=['XANG', 'DAU', 'all'], default='all')
    args = parser.parse_args()
    
    print(f"Bắt đầu chạy thực nghiệm cho loại: {args.type}...")
    
    if args.type in ['XANG', 'DAU']:
        run_command(['scripts/run_multi_seed.py', '--type', args.type], f"1. Đào tạo Mô hình & Đánh giá (5 seeds - {args.type})")
        run_command(['scripts/run_ablation.py', '--variant', 'all', '--type', args.type], f"2. Ablation Study ({args.type})")
        print(f"\nHOÀN TẤT THỰC NGHIỆM CHO {args.type}!")
    else:
        # Run all
        run_command(['scripts/run_multi_seed.py'], "1. Đào tạo Mô hình & Đánh giá (5 seeds)")
        run_command(['scripts/run_ablation.py', '--variant', 'all'], "2. Ablation Study")
        run_command(['scripts/compile_results.py'], "3. Tổng hợp Kết quả Thực nghiệm")
        run_command(['scripts/run_advanced_stats.py'], "4. Thống kê Nâng cao (ADF, KPSS, DM-Test)")
        run_command(['scripts/build_final_v7.py'], "5. Trích xuất vào Bản Thảo Word Cuối cùng")
        print("\nHOÀN TẤT TOÀN BỘ QUÁ TRÌNH THỰC NGHIỆM!")

if __name__ == '__main__':
    main()
