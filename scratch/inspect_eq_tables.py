import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

root = ET.fromstring(doc_xml.encode('utf-8'))

print("=== INSPECTING ALL EQUATION TABLES ===")
tbl_count = 0
for tbl in root.iter():
    tag = tbl.tag.split('}')[-1]
    if tag == 'tbl':
        tbl_xml = ET.tostring(tbl, encoding='utf-8').decode('utf-8')
        if any(f'({k})' in tbl_xml for k in range(1, 15)):
            tbl_count += 1
            print(f"\n================ TABLE {tbl_count} ================")
            # print rows and cell widths
            for tr in tbl.iter():
                if tr.tag.split('}')[-1] == 'tr':
                    tr_xml = ET.tostring(tr, encoding='utf-8').decode('utf-8')
                    # check text
                    txts = []
                    for t in tr.iter():
                        if t.tag.split('}')[-1] in ['t', 'mText'] and t.text:
                            txts.append(t.text)
                    print(f"Row: {''.join(txts)}")
                    # print trPr, tcPr
                    for tc in tr.iter():
                        if tc.tag.split('}')[-1] == 'tc':
                            tcPr = tc.find('{http://purl.oclc.org/ooxml/wordprocessingml/main}tcPr')
                            if tcPr is not None:
                                tcW = tcPr.find('{http://purl.oclc.org/ooxml/wordprocessingml/main}tcW')
                                if tcW is not None:
                                    print(f"   Cell width: {tcW.attrib}")
