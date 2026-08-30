import zipfile
import xml.etree.ElementTree as ET
import difflib
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'
file_v6 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

def parse_docx(path):
    with zipfile.ZipFile(path, 'r') as z:
        tree = ET.fromstring(z.read('word/document.xml'))
        paras = []
        for p in tree.iter():
            if p.tag.split('}')[-1] == 'p':
                txt = "".join(p.itertext()).strip()
                if txt:
                    paras.append(txt)
        
        # Track changes
        ins_nodes = [t for t in tree.iter() if t.tag.split('}')[-1] == 'ins']
        del_nodes = [t for t in tree.iter() if t.tag.split('}')[-1] == 'del']
        
        # Check comments
        comments = {}
        if 'word/comments.xml' in z.namelist():
            ctree = ET.fromstring(z.read('word/comments.xml'))
            for c in ctree.iter():
                if c.tag.split('}')[-1] == 'comment':
                    cid = c.attrib.get(list(c.attrib.keys())[0]) if c.attrib else '?'
                    # find id
                    for k, v in c.attrib.items():
                        if k.endswith('id'):
                            cid = v
                    author = c.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', '') or c.attrib.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}author', '') or c.attrib.get('author', '')
                    comments[cid] = (author, "".join(c.itertext()).strip())
                    
        # Media
        media = {n: len(z.read(n)) for n in z.namelist() if n.startswith('word/media/')}
        
        return {
            'paras': paras,
            'ins_count': len(ins_nodes),
            'del_count': len(del_nodes),
            'comments': comments,
            'media': media
        }

p4 = parse_docx(file_v4)
p6 = parse_docx(file_v6)

print("==================== SUMMARY COMPARISON ====================")
print(f"v4 Redline: {len(p4['paras'])} paragraphs, {p4['ins_count']} insertions, {p4['del_count']} deletions, {len(p4['comments'])} comments, media: {list(p4['media'].keys())}")
print(f"v6 Final  : {len(p6['paras'])} paragraphs, {p6['ins_count']} insertions, {p6['del_count']} deletions, {len(p6['comments'])} comments, media: {list(p6['media'].keys())}")

print("\n==================== TITLE COMPARISON ====================")
print(f"v4 Title: {p4['paras'][0] if p4['paras'] else 'N/A'}")
print(f"v6 Title: {p6['paras'][0] if p6['paras'] else 'N/A'}")

print("\n==================== ABSTRACT COMPARISON ====================")
print(f"v4 Abstract: {p4['paras'][1] if len(p4['paras']) > 1 else 'N/A'}")
print(f"\nv6 Abstract: {p6['paras'][1] if len(p6['paras']) > 1 else 'N/A'}")

print("\n==================== v4 REDLINE TRACK CHANGES (First 10) ====================")
with zipfile.ZipFile(file_v4, 'r') as z:
    t = ET.fromstring(z.read('word/document.xml'))
    del_runs = [("".join(n.itertext()).strip(), n.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', '')) for n in t.iter() if n.tag.split('}')[-1] == 'del']
    ins_runs = [("".join(n.itertext()).strip(), n.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', '')) for n in t.iter() if n.tag.split('}')[-1] == 'ins']
    print(f"Total deleted text runs: {len(del_runs)}")
    for d, a in del_runs[:10]:
        print(f"  [DEL by {a}]: {d}")
    print(f"Total inserted text runs: {len(ins_runs)}")
    for ins, a in ins_runs[:10]:
        print(f"  [INS by {a}]: {ins}")
