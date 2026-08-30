import zipfile
import xml.etree.ElementTree as ET

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with open(r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\scratch\comment_details.txt', 'w', encoding='utf-8') as out_f:
    with zipfile.ZipFile(docx_path, 'r') as z:
        # 1. Parse comments
        comm_xml = z.read('word/comments.xml')
        comm_root = ET.fromstring(comm_xml)
        
        comments_dict = {}
        for elem in comm_root.iter():
            tag = elem.tag.split('}')[-1]
            if tag == 'comment':
                c_id = None
                author = None
                date = None
                for k, v in elem.attrib.items():
                    if k.endswith('id'): c_id = v
                    elif k.endswith('author'): author = v
                    elif k.endswith('date'): date = v
                texts = []
                for t in elem.iter():
                    if t.tag.endswith('}t') or t.tag == 't':
                        if t.text: texts.append(t.text)
                comments_dict[c_id] = {
                    'id': c_id,
                    'author': author,
                    'date': date,
                    'text': ''.join(texts)
                }
                
        # 2. Parse document
        doc_xml = z.read('word/document.xml')
        doc_root = ET.fromstring(doc_xml)
        
        # Traverse paragraphs and tables to find comment locations
        p_idx = 0
        for p in doc_root.iter():
            tag = p.tag.split('}')[-1]
            if tag == 'p':
                p_idx += 1
                p_text = ''.join([t.text for t in p.iter() if (t.tag.endswith('}t') or t.tag == 't') and t.text])
                
                # Check for comment starts/ends
                starts = []
                ends = []
                refs = []
                for child in p.iter():
                    ctag = child.tag.split('}')[-1]
                    if ctag == 'commentRangeStart':
                        for k, v in child.attrib.items():
                            if k.endswith('id'): starts.append(v)
                    elif ctag == 'commentRangeEnd':
                        for k, v in child.attrib.items():
                            if k.endswith('id'): ends.append(v)
                    elif ctag == 'commentReference':
                        for k, v in child.attrib.items():
                            if k.endswith('id'): refs.append(v)
                            
                if starts or ends or refs:
                    all_ids = set(starts + ends + refs)
                    out_f.write(f"================================================================================\n")
                    out_f.write(f"PARAGRAPH #{p_idx} | Relevant Comment IDs: {all_ids}\n")
                    for cid in sorted(all_ids, key=lambda x: int(x) if x.isdigit() else 99):
                        if cid in comments_dict:
                            c = comments_dict[cid]
                            out_f.write(f"  [COMMENT ID {cid}] Author: {c['author']}\n")
                            out_f.write(f"  COMMENT CONTENT: {c['text']}\n")
                    out_f.write(f"--------------------------------------------------------------------------------\n")
                    out_f.write(f"PARAGRAPH TEXT:\n{p_text}\n\n")

print("Done extracting comment details to scratch/comment_details.txt")
