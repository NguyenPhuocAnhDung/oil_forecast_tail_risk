import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss
import warnings

# Suppress warnings from KPSS if it hits interpolation limits
warnings.filterwarnings("ignore")

DATA_PATH = "data/processed/unified_data.csv"

def run_tests(series, name):
    # ADF Test
    adf_result = adfuller(series.dropna())
    adf_stat = adf_result[0]
    adf_pvalue = adf_result[1]
    
    # KPSS Test
    kpss_result = kpss(series.dropna(), regression='c')
    kpss_stat = kpss_result[0]
    kpss_pvalue = kpss_result[1]
    
    return {
        'Variable': name,
        'ADF Stat': f"{adf_stat:.4f}",
        'ADF p-value': f"{adf_pvalue:.4e}" if adf_pvalue < 0.001 else f"{adf_pvalue:.4f}",
        'ADF Sig': "***" if adf_pvalue < 0.01 else "**" if adf_pvalue < 0.05 else "*" if adf_pvalue < 0.1 else "",
        'KPSS Stat': f"{kpss_stat:.4f}",
        'KPSS p-value': f"{kpss_pvalue:.4f}",
        'KPSS Sig': "***" if kpss_pvalue < 0.01 else "**" if kpss_pvalue < 0.05 else "*" if kpss_pvalue < 0.1 else ""
    }

def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    df['Ngày'] = pd.to_datetime(df['Ngày'])
    
    start_date = df['Ngày'].min().strftime('%Y-%m-%d')
    end_date = df['Ngày'].max().strftime('%Y-%m-%d')
    num_obs = len(df)
    
    targets = ['MG95', 'MG92', 'DO 0.001%', 'DO 0.05%']
    results = []
    
    for t in targets:
        if t in df.columns:
            res = run_tests(df[t], t)
            results.append(res)
            
    # Markdown output
    print(f"\n### Kết quả kiểm định tính dừng (Stationarity Tests)")
    print(f"**Dữ liệu:** Giá bán lẻ nội địa (VNĐ/lít)")
    print(f"**Giai đoạn:** {start_date} đến {end_date} ({num_obs} quan sát)\n")
    
    print("| Biến số (Mặt hàng) | ADF Statistic | ADF p-value | Ý nghĩa (ADF) | KPSS Statistic | KPSS p-value | Ý nghĩa (KPSS) |")
    print("|:---|---:|---:|:---|---:|---:|:---|")
    for r in results:
        print(f"| {r['Variable']} | {r['ADF Stat']} | {r['ADF p-value']} | {r['ADF Sig']} | {r['KPSS Stat']} | {r['KPSS p-value']} | {r['KPSS Sig']} |")
        
    print("\n*Ghi chú:*")
    print("- **ADF Test (H0):** Chuỗi có nghiệm đơn vị (Unit root - Không dừng). p-value < 0.05 => Bác bỏ H0, chuỗi DỪNG.")
    print("- **KPSS Test (H0):** Chuỗi DỪNG. p-value < 0.05 => Bác bỏ H0, chuỗi KHÔNG DỪNG.")
    print("- Mức ý nghĩa: *** (1%), ** (5%), * (10%)")

if __name__ == '__main__':
    main()
