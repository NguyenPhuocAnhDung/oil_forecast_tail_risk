import zipfile
import xml.etree.ElementTree as ET
import difflib
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'
file_v6 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

def get_doc_info(docx_path):
    info = {'namelist': [], 'comments': {}, 'tracked_changes': 0, 'paragraphs': [], 'tables': []}
    with zipfile.ZipFile(docx_path, 'r') as z:
        info['namelist'] = z.namelist()
        if 'word/comments.xml' in z.namelist():
            tree = ET.fromstring(z.read('word/comments.xml'))
            for c in tree.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}comment'):
                cid = c.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}id')
                author = c.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}author', '')
                text = "".join(c.itertext()).strip()
                info['comments'][cid] = {'author': author, 'text': text}
        
        doc_xml = z.read('word/document.xml')
        root = ET.fromstring(doc_xml)
        
        # Check track changes: w:ins, w:del
        ins_count = len(list(root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}ins')))
        del_count = len(list(root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}del')))
        info['tracked_changes'] = {'ins': ins_count, 'del': del_count}
        
        for p in root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}p'):
            t = "".join(p.itertext()).strip()
            if t:
                info['paragraphs'].append(t)
                
        for tbl in root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tbl'):
            rows = []
            for tr in tbl.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tr'):
                cells = ["".join(tc.itertext()).strip() for tc in tr.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tc')]
                if any(cells):
                    rows.append(cells)
            if rows:
                info['tables'].append(rows)
                
    return info

print("Parsing GUMNETHet_FAIRv4_redline.docx...")
info_v4 = get_doc_info(file_v4)
print("Parsing GUMNETHet_FAIRv6_final.docx...")
info_v6 = get_doc_info(file_v6)

print("\n==================== 1. GENERAL COMPARISON ====================")
print(f"v4 Redline - Paragraphs: {len(info_v4['paragraphs'])}, Tables: {len(info_v4['tables'])}, Comments: {len(info_v4['comments'])}, Tracked Changes (Ins/Del): {info_v4['tracked_changes']}")
print(f"v6 Final   - Paragraphs: {len(info_v6['paragraphs'])}, Tables: {len(info_v6['tables'])}, Comments: {len(info_v6['comments'])}, Tracked Changes (Ins/Del): {info_v6['tracked_changes']}")

print("\n==================== 2. COMMENTS IN V4 REDLINE ====================")
for cid, cdata in sorted(info_v4['comments'].items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0])):
    print(f"[{cid}] ({cdata['author']}): {cdata['text']}")

print("\n==================== 3. COMMENTS IN V6 FINAL ====================")
for cid, cdata in sorted(info_v6['comments'].items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0])):
    print(f"[{cid}] ({cdata['author']}): {cdata['text']}")

print("\n==================== 4. TITLE & ABSTRACT COMPARISON ====================")
print(f"[v4 Title]: {info_v4['paragraphs'][0] if info_v4['paragraphs'] else 'N/A'}")
print(f"[v6 Title]: {info_v6['paragraphs'][0] if info_v6['paragraphs'] else 'N/A'}")

# Compare full text with unified diff
v4_text = "\n".join(info_v4['paragraphs'])
v6_text = "\n".join(info_v6['paragraphs'])

diff = list(difflib.unified_diff(
    v4_text.splitlines(),
    v6_text.splitlines(),
    fromfile='GUMNETHet_FAIRv4_redline.docx',
    tofile='GUMNETHet_FAIRv6_final.docx',
    lineterm=''
))

print(f"\n==================== 5. UNIFIED DIFF OVERVIEW (Total diff lines: {len(diff)}) ====================")
for l in diff[:80]:
    print(l)
if len(diff) > 80:
    print(f"... and {len(diff) - 80} more diff lines.")
