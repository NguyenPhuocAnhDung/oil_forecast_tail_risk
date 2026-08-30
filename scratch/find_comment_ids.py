import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup_orig.docx'

with zipfile.ZipFile(backup_file, 'r') as z:
    xml = z.read('word/document.xml').decode('utf-8')

# Search for all comment references
matches = re.findall(r'<w:commentReference[^>]*w:id="(\d+)"', xml)
print("Comment references found in document.xml:", matches)

# Also check for commentRangeStart
starts = re.findall(r'<w:commentRangeStart[^>]*w:id="(\d+)"', xml)
print("Comment range starts found in document.xml:", starts)
