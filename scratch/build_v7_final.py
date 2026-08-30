import zipfile
import xml.etree.ElementTree as ET
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

src_redline = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'
out_v7_final = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'
vertical_fig1 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\paper_figures\fig1_gumnethet_vertical.png'

with zipfile.ZipFile(src_redline, 'r') as z:
    zip_entries = {name: z.read(name) for name in z.namelist()}

doc_xml = zip_entries['word/document.xml'].decode('utf-8')

# 1. Handle action note: replace 【HÀNH ĐỘNG: bổ sung trích dẫn cho BiMamba】 with [15]
doc_xml = doc_xml.replace('【HÀNH ĐỘNG: bổ sung trích dẫn cho BiMamba】', '[15]')

# 2. Accept all tracked changes in XML:
# Remove all <w:del ...> ... </w:del>
# Unwrap all <w:ins ...> ... </w:ins> -> keep the inner content
doc_xml = re.sub(r'<w:del\b[^>]*>.*?</w:del>', '', doc_xml, flags=re.DOTALL)
doc_xml = re.sub(r'<w:ins\b[^>]*>(.*?)</w:ins>', r'\1', doc_xml, flags=re.DOTALL)

# 3. Ensure equation table spacing has auto line height (remove w:line="12.60pt" or fixed height)
doc_xml = re.sub(r'<w:spacing\s+w:before="2pt"\s+w:after="2pt"\s+w:line="12\.60pt"\s+w:lineRule="auto"/>',
                 r'<w:spacing w:before="3pt" w:after="3pt"/>', doc_xml)
doc_xml = doc_xml.replace('<w:gridCol w:w="4400"/><w:gridCol w:w="640"/>',
                          '<w:gridCol w:w="4560"/><w:gridCol w:w="480"/>')
doc_xml = doc_xml.replace('<w:tcW w:w="220pt" w:type="dxa"/>', '<w:tcW w:w="228pt" w:type="dxa"/>')
doc_xml = doc_xml.replace('<w:tcW w:w="32pt" w:type="dxa"/>', '<w:tcW w:w="24pt" w:type="dxa"/>')

# 4. Update image1.png with high-res vertical figure 1
with open(vertical_fig1, 'rb') as f:
    zip_entries['word/media/image1.png'] = f.read()

# Update document.xml
zip_entries['word/document.xml'] = doc_xml.encode('utf-8')

# Write output to GUMNETHet_FAIRv7_final.docx
with zipfile.ZipFile(out_v7_final, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in zip_entries.items():
        z.writestr(filename, data)

print(f"✓ Successfully generated clean {out_v7_final}!")
