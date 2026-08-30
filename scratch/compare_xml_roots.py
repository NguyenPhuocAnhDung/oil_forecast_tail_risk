import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

orig_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup_orig.docx'
edited_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(orig_path, 'r') as z_orig:
    orig_doc_xml = z_orig.read('word/document.xml').decode('utf-8')
    print("=== ORIGINAL XML ROOT (First 500 chars) ===")
    print(orig_doc_xml[:500])
    print("\n=== ORIGINAL XML END (Last 300 chars) ===")
    print(orig_doc_xml[-300:])

with zipfile.ZipFile(edited_path, 'r') as z_edit:
    edit_doc_xml = z_edit.read('word/document.xml').decode('utf-8')
    print("\n=== EDITED XML ROOT (First 500 chars) ===")
    print(edit_doc_xml[:500])
