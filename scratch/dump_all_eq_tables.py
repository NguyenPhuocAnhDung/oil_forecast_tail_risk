import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_orig = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(backup_orig, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

tables = re.findall(r'<w:tbl.*?</w:tbl>', doc_xml, flags=re.DOTALL)

with open('scratch/all_eq_tables_dump.txt', 'w', encoding='utf-8') as f:
    for i, tbl in enumerate(tables):
        if any(f'({k})' in tbl for k in range(1, 15)):
            f.write(f"==================== EQUATION TABLE {i+1} ====================\n")
            f.write(tbl + "\n\n")

print("Dumped all equation tables to scratch/all_eq_tables_dump.txt")
