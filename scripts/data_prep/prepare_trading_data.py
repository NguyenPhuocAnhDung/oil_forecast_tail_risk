import pandas as pd
import numpy as np
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def prepare_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, 'data', 'processed', 'clean_data_exo_ver1.csv')
    output_path = os.path.join(current_dir, 'data', 'processed', 'trading_data_business_days.csv')
    
    print(f"🔄 Đang chuẩn hóa dữ liệu sang hệ quy chiếu Business Days (Singapore)...")
    
    if not os.path.exists(input_path):
        print(f"❌ Không tìm thấy file: {input_path}")
        return

    df = pd.read_csv(input_path)
    df['Ngày'] = pd.to_datetime(df['Ngày'])
    
    # 1. LỌC BỎ THỨ 7, CHỦ NHẬT (Chỉ lấy Business Days theo thị trường Singapore)
    df['DayOfWeek'] = df['Ngày'].dt.dayofweek
    df = df[df['DayOfWeek'] <= 4].copy() 
    
    # 2. MÃ HÓA CHU KỲ (CYCLICAL ENCODING) CHO TUẦN GIAO DỊCH 5 NGÀY
    df['Day_sin'] = np.sin(2 * np.pi * df['DayOfWeek'] / 5.0)
    df['Day_cos'] = np.cos(2 * np.pi * df['DayOfWeek'] / 5.0)
    
    # 3. LOẠI BỎ CÁC DÒNG CÓ GIÁ TRỊ TRỐNG
    df = df.dropna().reset_index(drop=True)
    
    # 4. LƯU FILE MỚI
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Đã tạo xong dữ liệu Trading!")
    print(f"📊 Số dòng hiện tại: {len(df)} (Đã xóa các ngày nghỉ)")
    print(f"💾 File mới lưu tại: {output_path}")

if __name__ == "__main__":
    prepare_data()