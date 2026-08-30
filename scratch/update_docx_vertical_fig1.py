import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

target_docx = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'
vertical_fig1 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\paper_figures\fig1_gumnethet_vertical.png'

# Read all zip entries
zip_entries = {}
with zipfile.ZipFile(target_docx, 'r') as z:
    for item in z.infolist():
        zip_entries[item.filename] = z.read(item.filename)

# Update image1.png
with open(vertical_fig1, 'rb') as f:
    zip_entries['word/media/image1.png'] = f.read()

# Write back
with zipfile.ZipFile(target_docx, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in zip_entries.items():
        z.writestr(filename, data)

print(f"✓ Successfully updated Figure 1 in {target_docx} to high-res Vertical Architecture ({len(zip_entries['word/media/image1.png'])} bytes)!")
