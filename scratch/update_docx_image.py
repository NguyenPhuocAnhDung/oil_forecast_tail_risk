import zipfile
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'
white_reg_fig1_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\paper_figures\fig1_gumnethet_white_regular.png'

# Read docx zip entries
zip_entries = {}
with zipfile.ZipFile(docx_path, 'r') as z_in:
    for item in z_in.infolist():
        zip_entries[item.filename] = z_in.read(item.filename)

# Replace image1.png with the new white regular figure
with open(white_reg_fig1_path, 'rb') as f:
    zip_entries['word/media/image1.png'] = f.read()

# Write back to docx_path
with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
    for filename, data in zip_entries.items():
        z_out.writestr(filename, data)

print(f"✓ Successfully updated Figure 1 in {docx_path} with pure white frame, black text, non-bold image ({len(zip_entries['word/media/image1.png'])} bytes)")
