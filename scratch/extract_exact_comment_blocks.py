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

def get_commented_sections(docx_path):
    with zipfile.ZipFile(docx_path, 'r') as z:
        tree = ET.fromstring(z.read('word/document.xml'))
    
    sections = {}
    for p in tree.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}p'):
        xml_str = ET.tostring(p, encoding='utf-8').decode('utf-8')
        for cid in ['0', '1', '4', '8', '12', '20', '29']:
            if f'w:id="{cid}"' in xml_str:
                sections[cid] = get_text(p).strip()
    return sections

before_secs = get_commented_sections(backup_file)
after_secs = get_commented_sections(final_file)

comments_dict = {
    '0': "Các con số này có chuẩn xác không, thể hiện chỗ nào trong bài, rà soát lại để chỉnh nếu cần?",
    '1': "Cần có giải thích hoặc số liệu minh chứng cho ý này",
    '4': "Sửa lại ký hiệu P mũ trong công thức này cho rõ ràng",
    '8': "Công thức này bị thiếu phía sau?",
    '12': "Công thức này cũng bị thiếu phía sau?",
    '20': "Ý này có chuẩn ko? Mình có thực hiện test trên tất cả các giai đoạn biến động chính trị nói trên hay chỉ test trong giai đoạn Mỹ - Iran? Cần làm rõ và sửa lại đoạn này nếu chưa chuẩn",
    '29': "Kiểm tra các con số này"
}

for cid in ['0', '1', '4', '8', '12', '20', '29']:
    print(f"\n=======================================================")
    print(f"COMMENT ID [{cid}]: \"{comments_dict[cid]}\"")
    print(f"\n[BẢN GỐC - TRƯỚC SỬA]:\n{before_secs.get(cid, 'None')}")
    print(f"\n[BẢN ĐÃ SỬA TRỰC TIẾP]:\n{after_secs.get(cid, 'None')}")
