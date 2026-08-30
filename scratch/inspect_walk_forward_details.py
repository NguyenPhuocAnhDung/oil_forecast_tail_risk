import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s).strip()

# Find Section IV text and Table 1 (Table summarizing train/test splits across horizons)
pos_iv = doc_xml.find('EXPERIMENTAL SETUP')
if pos_iv == -1:
    pos_iv = doc_xml.find('IV.')

pos_v = doc_xml.find('EMPIRICAL RESULTS')
if pos_v == -1:
    pos_v = doc_xml.find('V.')

section_iv_xml = doc_xml[pos_iv:pos_v] if pos_iv != -1 and pos_v != -1 else doc_xml[pos_iv:pos_iv+15000]

print("=== SECTION IV TEXT AND TABLES ===")
# extract paragraphs and tables
matches = re.findall(r'<(?:w:p|w:tbl)[^>]*>.*?</(?:w:p|w:tbl)>', section_iv_xml, re.DOTALL)
for m in matches:
    txt = strip_tags(m)
    if txt:
        print(f"\n--- BLOCK ---:\n{txt}")
