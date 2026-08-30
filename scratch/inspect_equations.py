import zipfile
import xml.etree.ElementTree as ET

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with open('scratch/equations_inspection.txt', 'w', encoding='utf-8') as out_f:
    with zipfile.ZipFile(docx_path, 'r') as z:
        doc_xml = z.read('word/document.xml')
        root = ET.fromstring(doc_xml)
        
        # Traverse paragraphs and tables
        for idx, elem in enumerate(root.iter()):
            tag = elem.tag.split('}')[-1]
            if tag in ['p', 'tbl']:
                text = ''.join([t.text for t in elem.iter() if (t.tag.endswith('}t') or t.tag == 't') and t.text])
                if any(f'({eq_num})' in text for eq_num in range(1, 16)):
                    out_f.write(f"==================================================\n")
                    out_f.write(f"ELEM #{idx} | TAG: {tag}\n")
                    out_f.write(f"TEXT: {text}\n")
                    out_f.write(f"RAW XML:\n{ET.tostring(elem, encoding='utf-8').decode('utf-8')}\n\n")

print("Finished writing equations inspection to scratch/equations_inspection.txt")
