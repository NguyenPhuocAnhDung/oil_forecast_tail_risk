import pandas as pd
import numpy as np
import os
import argparse
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_raw_data(input_path, output_path):
    print(f"📥 Đang đọc dữ liệu thô từ: {input_path}")
    
    try:
        if input_path.lower().endswith('.xlsx') or input_path.lower().endswith('.xls'):
            df = pd.read_excel(input_path)
        else:
            df = pd.read_csv(input_path)
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return
    
    # 1. Loại bỏ các dòng rác chứa tiêu đề phụ hoặc không có Ngày
    df = df.dropna(subset=['Ngày'])
    df = df[df['Ngày'].astype(str).str.lower() != 'ngày']
    
    if 'MG97' in df.columns:
        df = df[df['MG97'].astype(str).str.lower() != 'đơn vị tính']
    
    # 2. Xử lý cột thời gian (ĐÃ CẬP NHẬT ĐỂ CHẠY NHANH VÀ KHÔNG BÁO LỖI)
    # LƯU Ý: Nếu dữ liệu của bạn lưu kiểu Năm-Tháng-Ngày, hãy đổi '%d/%m/%Y' thành '%Y-%m-%d'
    df['Ngày'] = pd.to_datetime(df['Ngày'], errors='coerce')
    
    df = df.dropna(subset=['Ngày']).sort_values('Ngày').reset_index(drop=True)
    
    # 3. Lọc bỏ các cột rác (cột rỗng do Excel sinh ra)
    cols_to_keep = [c for c in df.columns if not str(c).startswith('Unnamed')]
    df = df[cols_to_keep]
    
    # 4. Ép kiểu số cho toàn bộ các cột giá (trừ cột Ngày)
    numeric_cols = [c for c in df.columns if c != 'Ngày']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # [ĐÃ SỬA - TASK 5] Bỏ interpolate tuyến tính để ngăn Data Leakage từ tương lai.
    # Chỉ dùng ffill() để kéo dài giá quá khứ sang các ngày nghỉ lễ (Duy trì tính nhân quả).
    df[numeric_cols] = df[numeric_cols].ffill() 
    df.dropna(subset=numeric_cols, inplace=True)
    
    # 6. Lưu ra file sạch
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Đã dọn dẹp xong! Giữ lại {len(df)} dòng.")
    print(f"💾 File sạch được lưu tại: {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Lùi 1 cấp vì file preprocess.py đang nằm trong thư mục src/
    project_root = os.path.dirname(current_dir) 
    
    default_input = os.path.join(project_root, 'data', 'raw', 'price_petroleum.xlsx')
    default_output = os.path.join(project_root, 'data', 'processed', 'clean_data.csv')

    parser = argparse.ArgumentParser(description="Tiền xử lý dữ liệu xăng dầu thô (Production Grade)")
    parser.add_argument('--input', type=str, default=default_input, help='Đường dẫn file dữ liệu thô đầu vào')
    parser.add_argument('--output', type=str, default=default_output, help='Đường dẫn xuất file sạch')
    
    args = parser.parse_args()
    clean_raw_data(args.input, args.output)