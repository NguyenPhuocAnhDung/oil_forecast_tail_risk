import zipfile
import xml.etree.ElementTree as ET

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml')
    root = ET.fromstring(doc_xml)

ns = {
    'w': 'http://purl.oclc.org/ooxml/wordprocessingml/main',
    'm': 'http://purl.oclc.org/ooxml/officeDocument/math'
}

print("=== CHECKING KEY PARAGRAPHS & TABLES ===")

# 1. Title
for p in root.findall('.//w:p', ns):
    text = ''.join([t.text for t in p.findall('.//w:t', ns) if t.text])
    if 'Heterogeneous Mixture-of-Experts for Probabilistic' in text:
        print("FOUND TITLE:", text)

# 2. Abstract
for p in root.findall('.//w:p', ns):
    text = ''.join([t.text for t in p.findall('.//w:t', ns) if t.text])
    if text.startswith('Abstract—'):
        print("FOUND ABSTRACT (len = %d):" % len(text), text[:120])

# 3. Intro Contributions
for p in root.findall('.//w:p', ns):
    text = ''.join([t.text for t in p.findall('.//w:t', ns) if t.text])
    if 'The principal contributions of this paper are fourfold' in text:
        print("FOUND CONTRIBUTIONS:", text[:120])

# 4. Equation 2 Table
for tbl in root.findall('.//w:tbl', ns):
    text = ''.join([t.text for t in tbl.findall('.//w:t', ns) if t.text])
    if '(2)' in text and 'exp' in text:
        print("FOUND EQ 2 TBL:", text)

# 5. Fig 1 Caption
for p in root.findall('.//w:p', ns):
    text = ''.join([t.text for t in p.findall('.//w:t', ns) if t.text])
    if 'Fig. 1.' in text:
        print("FOUND FIG 1 CAPTION:", text)

# 6. Equation 4 & 7 Tables
for tbl in root.findall('.//w:tbl', ns):
    text = ''.join([t.text for t in tbl.findall('.//w:t', ns) if t.text])
    if '(4)' in text:
        print("FOUND EQ 3-4 TBL:", text)
    if '(7)' in text:
        print("FOUND EQ 6-7 TBL:", text)

# 7. Walk-forward text
for p in root.findall('.//w:p', ns):
    text = ''.join([t.text for t in p.findall('.//w:t', ns) if t.text])
    if 'To prevent look-ahead bias' in text:
        print("FOUND WALK-FORWARD TEXT:", text[:120])

# 8. Conclusion
for p in root.findall('.//w:p', ns):
    text = ''.join([t.text for t in p.findall('.//w:t', ns) if t.text])
    if 'Expanding walk-forward experiments on MG95' in text:
        print("FOUND CONCLUSION:", text[:120])

# 9. References Heading
for p in root.findall('.//w:p', ns):
    text = ''.join([t.text for t in p.findall('.//w:t', ns) if t.text])
    if text == 'REFERENCES':
        print("FOUND REFERENCES HEADING")
