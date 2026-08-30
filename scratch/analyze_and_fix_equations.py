import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_orig = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(backup_orig, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

# Find all tables that have equations
tables = re.findall(r'<w:tbl.*?</w:tbl>', doc_xml, flags=re.DOTALL)
print(f"Total tables found: {len(tables)}")

for i, tbl in enumerate(tables):
    if any(f'({k})' in tbl for k in range(1, 15)):
        print(f"\n--- Equation Table {i+1} ---")
        # Extract math text
        math_matches = re.findall(r'<m:oMath.*?</m:oMath>', tbl, flags=re.DOTALL)
        for m in math_matches:
            # strip xml tags to see math text
            txt = re.sub(r'<[^>]+>', '', m)
            print(f"Math: {txt}")
