import zipfile
import xml.etree.ElementTree as ET
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'
file_v6 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

def get_text_elements(docx_path):
    with zipfile.ZipFile(docx_path, 'r') as z:
        root = ET.fromstring(z.read('word/document.xml'))
        paras = []
        for p in root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}p'):
            t = "".join(p.itertext()).strip()
            if t:
                paras.append(t)
        
        # Track changes
        ins_nodes = list(root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}ins'))
        del_nodes = list(root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}del'))
        
        # Tables
        tables = []
        for tbl in root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tbl'):
            rows = []
            for tr in tbl.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tr'):
                cells = ["".join(tc.itertext()).strip() for tc in tr.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tc')]
                if any(cells):
                    rows.append(cells)
            if rows:
                tables.append(rows)
                
        # Media
        media = {n: len(z.read(n)) for n in z.namelist() if n.startswith('word/media/')}
        
        # Comments
        comments = {}
        if 'word/comments.xml' in z.namelist():
            c_tree = ET.fromstring(z.read('word/comments.xml'))
            for c in c_tree.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}comment'):
                cid = c.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}id')
                author = c.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}author', '')
                comments[cid] = (author, "".join(c.itertext()).strip())
                
    return {
        'paras': paras,
        'ins_count': len(ins_nodes),
        'del_count': len(del_nodes),
        'tables': tables,
        'media': media,
        'comments': comments
    }

d4 = get_text_elements(file_v4)
d6 = get_text_elements(file_v6)

print("=== DETAILED COMPARISON REPORT: v4_redline vs v6_final ===")

print("\n1. LANGUAGE & TARGET AUDIENCE:")
print(f"v4_redline Language : Vietnamese (Bản thảo tiếng Việt có Track Changes)")
print(f"v6_final Language   : English (Bản thảo tiếng Anh chuẩn gửi bài Tạp chí quốc tế / IEEE)")

print("\n2. TITLE:")
print(f"v4_redline : {d4['paras'][0] if d4['paras'] else 'N/A'}")
print(f"v6_final   : {d6['paras'][0] if d6['paras'] else 'N/A'}")

print("\n3. TRACKED CHANGES (REVISIONS):")
print(f"v4_redline : {d4['ins_count']} insertions, {d4['del_count']} deletions (Chế độ Redline với tác giả 'Claude')")
print(f"v6_final   : {d6['ins_count']} insertions, {d6['del_count']} deletions (Đã được chấp nhận/tích hợp sạch sẽ, clean manuscript)")

print("\n4. COMMENTS (PHẢN HỒI PHẢN BIỆN):")
print(f"v4_redline comments count: {len(d4['comments'])}")
for cid, (author, ctext) in sorted(d4['comments'].items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0])):
    print(f"  - [{cid}] ({author}): {ctext[:60]}...")
print(f"v6_final comments count: {len(d6['comments'])}")
for cid, (author, ctext) in sorted(d6['comments'].items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0])):
    print(f"  - [{cid}] ({author}): {ctext[:60]}...")

print("\n5. IMAGES & FIGURES:")
print(f"v4_redline media: {d4['media']}")
print(f"v6_final media  : {d6['media']}")

print("\n6. SECTIONS STRUCTURE:")
print("v4_redline Headings:")
for p in d4['paras'][:30]:
    if any(p.startswith(k) for k in ['1.', '2.', '3.', '4.', '5.', '6.', 'TÀI LIỆU', 'I.', 'II.', 'III.', 'IV.', 'V.', 'VI.']):
        print(f"  {p}")

print("\nv6_final Headings:")
for p in d6['paras'][:30]:
    if any(p.startswith(k) for k in ['I.', 'II.', 'III.', 'IV.', 'V.', 'VI.', 'REFERENCES', 'Data and Code']):
        print(f"  {p}")
