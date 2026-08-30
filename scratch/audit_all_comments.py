import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup_orig.docx'
final_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

# Extract all comments from backup
comments_dict = {}
with zipfile.ZipFile(backup_file, 'r') as z:
    if 'word/comments.xml' in z.namelist():
        tree = ET.fromstring(z.read('word/comments.xml'))
        for c in tree.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}comment'):
            cid = c.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}id')
            author = c.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}author', '')
            text = "".join(c.itertext()).strip()
            comments_dict[cid] = {'author': author, 'text': text}

print(f"Total comments found in backup_orig: {len(comments_dict)}")
for cid, info in sorted(comments_dict.items(), key=lambda x: int(x[0])):
    print(f"\n--- Comment ID [{cid}] (Author: {info['author']}) ---")
    print(f"Comment Text: {info['text']}")
