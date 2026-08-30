import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'

with zipfile.ZipFile(file_v4, 'r') as z:
    v4_xml = z.read('word/document.xml').decode('utf-8')

# Search for color occurrences
matches = re.finditer(r'<w:color[^>]*w:val="([^"]+)"[^>]*>', v4_xml)
for m in matches:
    pos = m.start()
    snippet = v4_xml[max(0, pos-100):min(len(v4_xml), pos+300)]
    print(f"\nColor val: {m.group(1)}")
    print(f"Snippet: {snippet}")
