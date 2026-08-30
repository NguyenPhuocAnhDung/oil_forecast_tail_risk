import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s).strip()

pos_wf = doc_xml.find('To prevent look-ahead bias')
print("Position:", pos_wf)
if pos_wf != -1:
    surround = doc_xml[pos_wf-500:pos_wf+4000]
    matches = re.findall(r'<(?:w:p|w:tbl)[^>]*>.*?</(?:w:p|w:tbl)>', surround, re.DOTALL)
    for m in matches:
        txt = strip_tags(m)
        if txt:
            print(f"\n--- BLOCK ---:\n{txt}")
