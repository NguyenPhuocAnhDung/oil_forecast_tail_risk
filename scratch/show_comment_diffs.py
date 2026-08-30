import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup_orig.docx'
final_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

def get_text(node):
    txts = []
    for t in node.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            txts.append(t.text)
    return ''.join(txts)

def extract_paras_with_comments(docx_path):
    results = {}
    with zipfile.ZipFile(docx_path, 'r') as z:
        tree = ET.fromstring(z.read('word/document.xml'))
        for p in tree.iter():
            tag = p.tag.split('}')[-1]
            if tag in ['p', 'tbl']:
                xml_str = ET.tostring(p, encoding='utf-8').decode('utf-8')
                for cid in ['0', '1', '4', '8', '12', '20', '29']:
                    if f'w:id="{cid}"' in xml_str or f'w:name="eq_{cid}"' in xml_str:
                        if cid not in results:
                            results[cid] = get_text(p).strip()
    return results

before = extract_paras_with_comments(backup_file)
after = extract_paras_with_comments(final_file)

print("==================== COMPARISON OF ALL 7 COMMENTS ====================")
for cid in ['0', '1', '4', '8', '12', '20', '29']:
    print(f"\n=======================================================")
    print(f"COMMENT ID [{cid}]:")
    print(f"--- TRƯỚC KHI SỬA (Trong backup_orig): ---")
    print(before.get(cid, "N/A"))
    print(f"\n--- ĐÃ SỬA XONG (Trong GUMNETHet_FAIRv6_final.docx): ---")
    print(after.get(cid, "N/A"))
