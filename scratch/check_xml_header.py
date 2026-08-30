import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

orig_docx = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'
v7_docx = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'

with zipfile.ZipFile(orig_docx, 'r') as z:
    orig_xml = z.read('word/document.xml').decode('utf-8')

with zipfile.ZipFile(v7_docx, 'r') as z:
    v7_xml = z.read('word/document.xml').decode('utf-8')

print("=== ORIG ROOT XML (first 300 chars) ===")
print(orig_xml[:300])

print("\n=== V7 ROOT XML (first 300 chars) ===")
print(v7_xml[:300])
