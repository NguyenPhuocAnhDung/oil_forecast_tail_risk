import zipfile
import xml.etree.ElementTree as ET

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with open(r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\scratch\comments_dump.txt', 'w', encoding='utf-8') as out_f:
    with zipfile.ZipFile(docx_path, 'r') as z:
        xml_data = z.read('word/comments.xml')
        root = ET.fromstring(xml_data)
        
        doc_xml = z.read('word/document.xml')
        doc_root = ET.fromstring(doc_xml)
        
        comments_dict = {}
        for elem in root.iter():
            if elem.tag.endswith('}comment') or elem.tag == 'comment':
                c_id = None
                author = None
                date = None
                for k, v in elem.attrib.items():
                    if k.endswith('id'):
                        c_id = v
                    elif k.endswith('author'):
                        author = v
                    elif k.endswith('date'):
                        date = v
                texts = []
                for t in elem.iter():
                    if t.tag.endswith('}t') or t.tag == 't':
                        if t.text:
                            texts.append(t.text)
                comment_text = ''.join(texts)
                comments_dict[c_id] = {
                    'id': c_id,
                    'author': author,
                    'date': date,
                    'text': comment_text
                }
                
        out_f.write(f"Total comments found in comments.xml: {len(comments_dict)}\n\n")
        for cid, cinfo in sorted(comments_dict.items(), key=lambda x: int(x[0]) if x[0] and x[0].isdigit() else 9999):
            out_f.write(f"==================================================\n")
            out_f.write(f"COMMENT ID: {cinfo['id']} | Author: {cinfo['author']} | Date: {cinfo['date']}\n")
            out_f.write(f"COMMENT TEXT:\n{cinfo['text']}\n")
            out_f.write(f"==================================================\n\n")

        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        out_f.write("\n--- ANCHORED PARAGRAPHS IN DOCUMENT ---\n")
        p_idx = 0
        for p in doc_root.findall('.//w:p', ns):
            p_idx += 1
            p_text = ''.join([t.text for t in p.findall('.//w:t', ns) if t.text])
            starts = [elem.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id') for elem in p.findall('.//w:commentRangeStart', ns)]
            ends = [elem.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id') for elem in p.findall('.//w:commentRangeEnd', ns)]
            refs = [elem.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id') for elem in p.findall('.//w:commentReference', ns)]
            if starts or ends or refs:
                out_f.write(f"[P#{p_idx}] Comment IDs: starts={starts}, ends={ends}, refs={refs}\n")
                out_f.write(f"Paragraph snippet: {p_text}\n\n")

print("Finished dumping comments to scratch/comments_dump.txt")
