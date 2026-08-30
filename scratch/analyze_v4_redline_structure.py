import zipfile
import xml.etree.ElementTree as ET
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'
file_v6 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(file_v4, 'r') as z:
    v4_xml = z.read('word/document.xml').decode('utf-8')

with zipfile.ZipFile(file_v6, 'r') as z:
    v6_xml = z.read('word/document.xml').decode('utf-8')

print(f"Length of document.xml v4: {len(v4_xml)} chars")
print(f"Length of document.xml v6: {len(v6_xml)} chars")

# Check for highlight or colored text (redline)
red_runs_v4 = re.findall(r'<w:color[^>]*w:val="([0-9a-fA-F]+)"[^>]*>', v4_xml)
print(f"Colors in v4: {set(red_runs_v4)}")

highlight_runs_v4 = re.findall(r'<w:highlight[^>]*w:val="([^"]+)"[^>]*>', v4_xml)
print(f"Highlights in v4: {set(highlight_runs_v4)}")

strike_runs_v4 = re.findall(r'<w:strike[^>]*/>', v4_xml)
print(f"Strike-through in v4: {len(strike_runs_v4)}")

# Check media files in v4 vs v6
with zipfile.ZipFile(file_v4, 'r') as z4, zipfile.ZipFile(file_v6, 'r') as z6:
    media_v4 = [n for n in z4.namelist() if n.startswith('word/media/')]
    media_v6 = [n for n in z6.namelist() if n.startswith('word/media/')]
    print(f"Media in v4: {media_v4}")
    print(f"Media in v6: {media_v6}")
    for m in media_v4:
        print(f"v4 {m} size: {len(z4.read(m))} bytes")
    for m in media_v6:
        print(f"v6 {m} size: {len(z6.read(m))} bytes")
