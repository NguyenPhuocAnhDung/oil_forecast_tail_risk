import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

orig_docx = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'

with zipfile.ZipFile(orig_docx, 'r') as z:
    xml = z.read('word/document.xml').decode('utf-8')

doc_tag = re.search(r'<w:document[^>]*>', xml).group(0)
print("Original <w:document ...> attributes:")
print(doc_tag)
