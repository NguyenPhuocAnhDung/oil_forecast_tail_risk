import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'

with zipfile.ZipFile(file_path, 'r') as z:
    namelist = z.namelist()
    print("Files inside docx:", namelist[:15])
    
    # 1. Comments
    comments = {}
    if 'word/comments.xml' in namelist:
        tree = ET.fromstring(z.read('word/comments.xml'))
        for c in tree.iter():
            if c.tag.split('}')[-1] == 'comment':
                cid = None
                for k, v in c.attrib.items():
                    if k.endswith('id'):
                        cid = v
                author = c.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', '') or c.attrib.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}author', '') or c.attrib.get('author', '')
                date = c.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '') or c.attrib.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}date', '') or c.attrib.get('date', '')
                text = "".join(c.itertext()).strip()
                comments[cid] = {'author': author, 'date': date, 'text': text}
                
    # 2. Document XML
    doc_tree = ET.fromstring(z.read('word/document.xml'))
    
    # Tracked changes
    del_nodes = []
    ins_nodes = []
    for node in doc_tree.iter():
        tag = node.tag.split('}')[-1]
        if tag == 'del':
            t = "".join(node.itertext()).strip()
            author = node.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', '') or node.attrib.get('author', '')
            date = node.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '') or node.attrib.get('date', '')
            if t:
                del_nodes.append({'author': author, 'date': date, 'text': t})
        elif tag == 'ins':
            t = "".join(node.itertext()).strip()
            author = node.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', '') or node.attrib.get('author', '')
            date = node.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '') or node.attrib.get('date', '')
            if t:
                ins_nodes.append({'author': author, 'date': date, 'text': t})

print(f"\n==================== 1. COMMENTS ({len(comments)}) ====================")
for cid, info in sorted(comments.items(), key=lambda x: int(x[0]) if x[0] and x[0].isdigit() else str(x[0])):
    print(f"[{cid}] (Author: {info['author']}, Date: {info['date']}): {info['text']}")

print(f"\n==================== 2. TRACKED CHANGES ({len(del_nodes)} deletions, {len(ins_nodes)} insertions) ====================")
for i in range(max(len(del_nodes), len(ins_nodes))):
    d_txt = del_nodes[i]['text'] if i < len(del_nodes) else ''
    i_txt = ins_nodes[i]['text'] if i < len(ins_nodes) else ''
    author = ins_nodes[i]['author'] if i < len(ins_nodes) else (del_nodes[i]['author'] if i < len(del_nodes) else '')
    print(f"\n--- Change #{i+1} by {author} ---")
    if d_txt:
        print(f"  ❌ Deleted : {d_txt}")
    if i_txt:
        print(f"  ✅ Inserted: {i_txt}")
