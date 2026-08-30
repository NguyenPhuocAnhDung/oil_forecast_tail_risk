import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup_orig.docx'
final_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(backup_file, 'r') as z:
    xml_backup = z.read('word/document.xml').decode('utf-8')

with zipfile.ZipFile(final_file, 'r') as z:
    xml_final = z.read('word/document.xml').decode('utf-8')

def strip_xml(x):
    return re.sub(r'<[^>]+>', '', x).strip()

def get_surrounding_para(xml_str, cid):
    pattern = rf'<w:commentRangeStart[^>]*w:id="{cid}"'
    m = re.search(pattern, xml_str)
    if not m:
        return "Not found"
    pos = m.start()
    p_start = xml_str.rfind('<w:p ', 0, pos)
    if p_start == -1:
        p_start = xml_str.rfind('<w:p>', 0, pos)
    p_end = xml_str.find('</w:p>', pos) + 6
    return strip_xml(xml_str[p_start:p_end])

comments_dict = {
    '0': ("Abstract", "Các con số này có chuẩn xác không, thể hiện chỗ nào trong bài, rà soát lại để chỉnh nếu cần?"),
    '1': ("Contributions", "Cần có giải thích hoặc số liệu minh chứng cho ý này"),
    '4': ("Equation (2)", "Sửa lại ký hiệu P mũ trong công thức này cho rõ ràng"),
    '8': ("Equation (4)", "Công thức này bị thiếu phía sau?"),
    '12': ("Equation (7)", "Công thức này cũng bị thiếu phía sau?"),
    '20': ("Walk-forward Setup", "Ý này có chuẩn ko? Mình có thực hiện test trên tất cả các giai đoạn biến động chính trị nói trên hay chỉ test trong giai đoạn Mỹ - Iran? Cần làm rõ và sửa lại đoạn này nếu chưa chuẩn"),
    '29': ("Conclusion", "Kiểm tra các con số này")
}

print("==================== DETAILED AUDIT OF ALL 7 COMMENTS ====================")
for cid in ['0', '1', '4', '8', '12', '20', '29']:
    section, text_comment = comments_dict[cid]
    print(f"\n=======================================================================")
    print(f"📌 COMMENT ID [{cid}] — Vị trí: {section}")
    print(f"💬 Nội dung Comment: \"{text_comment}\"")
    print(f"\n--- [1] NỘI DUNG GỐC TRƯỚC SỬA (Trong backup_orig): ---")
    print(get_surrounding_para(xml_backup, cid))
    print(f"\n--- [2] NỘI DUNG ĐÃ SỬA CHUẨN XÁC (Trong GUMNETHet_FAIRv6_final.docx): ---")
    print(get_surrounding_para(xml_final, cid))
