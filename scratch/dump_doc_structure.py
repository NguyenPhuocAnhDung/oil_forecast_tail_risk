import zipfile
import xml.etree.ElementTree as ET

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with open(r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\scratch\doc_full_paragraphs.txt', 'w', encoding='utf-8') as out_f:
    with zipfile.ZipFile(docx_path, 'r') as z:
        doc_xml = z.read('word/document.xml')
        root = ET.fromstring(doc_xml)
        
        # Traverse elements in document body
        body = None
        for child in root:
            if child.tag.endswith('body'):
                body = child
                break
                
        if body is None:
            out_f.write("No body found!\n")
            exit()
            
        elem_count = 0
        for elem in body:
            tag = elem.tag.split('}')[-1]
            elem_count += 1
            if tag == 'p':
                # Paragraph
                text = ''.join([t.text for t in elem.iter() if (t.tag.endswith('}t') or t.tag == 't') and t.text])
                
                # Check for math or drawings or comments
                has_math = any('math' in t.tag.lower() or 'omath' in t.tag.lower() for t in elem.iter())
                has_drawing = any('drawing' in t.tag.lower() or 'blip' in t.tag.lower() for t in elem.iter())
                
                comments_in_p = []
                for c in elem.iter():
                    ctag = c.tag.split('}')[-1]
                    if ctag in ['commentRangeStart', 'commentRangeEnd', 'commentReference']:
                        cid = [v for k, v in c.attrib.items() if k.endswith('id')]
                        comments_in_p.append(f"{ctag}({cid})")
                        
                math_note = " [HAS MATH]" if has_math else ""
                drawing_note = " [HAS DRAWING]" if has_drawing else ""
                comment_note = f" [COMMENTS: {', '.join(comments_in_p)}]" if comments_in_p else ""
                
                out_f.write(f"[P#{elem_count}]{math_note}{drawing_note}{comment_note}\n{text}\n\n")
                
            elif tag == 'tbl':
                out_f.write(f"[TBL#{elem_count}]\n")
                # print rows
                for r_idx, row in enumerate(elem.iter()):
                    rtag = row.tag.split('}')[-1]
                    if rtag == 'tr':
                        row_texts = []
                        for cell in row.iter():
                            ctag = cell.tag.split('}')[-1]
                            if ctag == 'tc':
                                c_text = ''.join([t.text for t in cell.iter() if (t.tag.endswith('}t') or t.tag == 't') and t.text])
                                row_texts.append(c_text.strip().replace('\n', ' '))
                        out_f.write(f"  Row: {' | '.join(row_texts[:8])}\n")
                out_f.write("\n")

print("Finished dumping document structure to scratch/doc_full_paragraphs.txt")
