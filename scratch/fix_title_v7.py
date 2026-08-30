import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

for fpath in [
    r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx',
    r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_redline.docx'
]:
    with zipfile.ZipFile(fpath, 'r') as z:
        entries = {name: z.read(name) for name in z.namelist()}
    
    xml = entries['word/document.xml'].decode('utf-8')
    
    # Replace old title text
    old_title = 'GUMNetHet: A Heterogeneous Gated Mixture Network for Probabilistic Multi-Horizon Forecasting of Refined Petroleum Product Prices'
    new_title = 'Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts'
    
    if old_title in xml:
        xml = xml.replace(old_title, new_title)
        entries['word/document.xml'] = xml.encode('utf-8')
        with zipfile.ZipFile(fpath, 'w', zipfile.ZIP_DEFLATED) as z:
            for filename, data in entries.items():
                z.writestr(filename, data)
        print(f"✓ Updated official title in {fpath}")
    else:
        print(f"Old title not found in {fpath}")
