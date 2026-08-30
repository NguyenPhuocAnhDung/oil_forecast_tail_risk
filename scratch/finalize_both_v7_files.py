import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

src_redline = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'
out_v7_final = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'
out_v7_redline = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_redline.docx'
vertical_fig1 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\paper_figures\fig1_gumnethet_vertical.png'

official_title = "Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts"

# ==================== 1. BUILD V7 REDLINE ====================
with zipfile.ZipFile(src_redline, 'r') as z:
    redline_entries = {name: z.read(name) for name in z.namelist()}

redline_xml = redline_entries['word/document.xml'].decode('utf-8')
# resolve action note in redline
redline_xml = redline_xml.replace('【HÀNH ĐỘNG: bổ sung trích dẫn cho BiMamba】', '[15]')
# update title to official title if needed
redline_xml = re.sub(
    r'(<w:p\b[^>]*>.*?<w:pStyle\s+w:val="Title"[^>]*>.*?<w:t>).*?(</w:t>.*?</w:p>)',
    rf'\g<1>{official_title}\g<2>',
    redline_xml,
    flags=re.DOTALL
)
redline_entries['word/document.xml'] = redline_xml.encode('utf-8')
with open(vertical_fig1, 'rb') as f:
    redline_entries['word/media/image1.png'] = f.read()

with zipfile.ZipFile(out_v7_redline, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in redline_entries.items():
        z.writestr(filename, data)
print(f"✓ Successfully generated {out_v7_redline}!")

# ==================== 2. BUILD V7 FINAL (CLEAN) ====================
final_xml = redline_xml
# Accept all tracked changes
final_xml = re.sub(r'<w:del\b[^>]*>.*?</w:del>', '', final_xml, flags=re.DOTALL)
final_xml = re.sub(r'<w:ins\b[^>]*>(.*?)</w:ins>', r'\1', final_xml, flags=re.DOTALL)

# Ensure equation table spacing
final_xml = re.sub(r'<w:spacing\s+w:before="2pt"\s+w:after="2pt"\s+w:line="12\.60pt"\s+w:lineRule="auto"/>',
                   r'<w:spacing w:before="3pt" w:after="3pt"/>', final_xml)
final_xml = final_xml.replace('<w:gridCol w:w="4400"/><w:gridCol w:w="640"/>',
                              '<w:gridCol w:w="4560"/><w:gridCol w:w="480"/>')
final_xml = final_xml.replace('<w:tcW w:w="220pt" w:type="dxa"/>', '<w:tcW w:w="228pt" w:type="dxa"/>')
final_xml = final_xml.replace('<w:tcW w:w="32pt" w:type="dxa"/>', '<w:tcW w:w="24pt" w:type="dxa"/>')

# Check title in final
final_xml = re.sub(
    r'(<w:p\b[^>]*>.*?<w:pStyle\s+w:val="Title"[^>]*>.*?<w:t>).*?(</w:t>.*?</w:p>)',
    rf'\g<1>{official_title}\g<2>',
    final_xml,
    flags=re.DOTALL
)

final_entries = dict(redline_entries)
final_entries['word/document.xml'] = final_xml.encode('utf-8')

with zipfile.ZipFile(out_v7_final, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in final_entries.items():
        z.writestr(filename, data)
print(f"✓ Successfully generated clean {out_v7_final}!")
