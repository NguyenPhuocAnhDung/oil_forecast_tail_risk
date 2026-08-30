import zipfile
import xml.etree.ElementTree as ET

docx_in = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'

with zipfile.ZipFile(docx_in, 'r') as z:
    root = ET.fromstring(z.read('word/document.xml'))

print("Root tag:", root.tag)
for c in root:
    print("Child tag:", c.tag)
