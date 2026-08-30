import zipfile
import xml.etree.ElementTree as ET

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with open(r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\scratch\anchors_dump.txt', 'w', encoding='utf-8') as out_f:
    with zipfile.ZipFile(docx_path, 'r') as z:
        doc_xml = z.read('word/document.xml')
        root = ET.fromstring(doc_xml)
        
        # Let's search for all elements that have id in attrib or tag related to comment
        for elem in root.iter():
            tag_name = elem.tag.split('}')[-1]
            if 'comment' in tag_name.lower():
                out_f.write(f"Tag: {elem.tag} | Attrib: {elem.attrib}\n")
                
print("Finished checking comments tags")
