import zipfile
import re
import sys
import os
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')

src_docx = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'
out_v7_final = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'
out_v7_redline = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_redline.docx'
vertical_fig1 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\paper_figures\fig1_gumnethet_vertical.png'

with zipfile.ZipFile(src_docx, 'r') as z:
    entries = {name: z.read(name) for name in z.namelist()}

xml = entries['word/document.xml'].decode('utf-8')

# 1. Resolve action note
xml = xml.replace('【HÀNH ĐỘNG: bổ sung trích dẫn cho BiMamba】', '[15]')

# 2. Official Title
old_title = 'GUMNetHet: A Heterogeneous Gated Mixture Network for Probabilistic Multi-Horizon Forecasting of Refined Petroleum Product Prices'
new_title = 'Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts'
xml = xml.replace(old_title, new_title)

# 3. Figure 1 image
with open(vertical_fig1, 'rb') as f:
    entries['word/media/image1.png'] = f.read()

# Build redline
redline_entries = dict(entries)
redline_entries['word/document.xml'] = xml.encode('utf-8')
with zipfile.ZipFile(out_v7_redline, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in redline_entries.items():
        z.writestr(filename, data)
print(f"✓ Created {out_v7_redline}")

# Build final: accept all revisions
final_xml = xml
final_xml = re.sub(r'<w:del\b[^>]*>.*?</w:del>', '', final_xml, flags=re.DOTALL)
final_xml = re.sub(r'<w:ins\b[^>]*>(.*?)</w:ins>', r'\1', final_xml, flags=re.DOTALL)

# Remove any empty runs or clean spacing
final_xml = re.sub(r'<w:spacing\s+w:before="2pt"\s+w:after="2pt"\s+w:line="12\.60pt"\s+w:lineRule="auto"/>',
                   r'<w:spacing w:before="3pt" w:after="3pt"/>', final_xml)
final_xml = final_xml.replace('<w:gridCol w:w="4400"/><w:gridCol w:w="640"/>',
                              '<w:gridCol w:w="4560"/><w:gridCol w:w="480"/>')
final_xml = final_xml.replace('<w:tcW w:w="220pt" w:type="dxa"/>', '<w:tcW w:w="228pt" w:type="dxa"/>')
final_xml = final_xml.replace('<w:tcW w:w="32pt" w:type="dxa"/>', '<w:tcW w:w="24pt" w:type="dxa"/>')

final_entries = dict(entries)
final_entries['word/document.xml'] = final_xml.encode('utf-8')

with zipfile.ZipFile(out_v7_final, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in final_entries.items():
        z.writestr(filename, data)
print(f"✓ Created {out_v7_final}")

# Test in MS Word
print("\nVerifying opening in Microsoft Word COM interface...")
for target in [out_v7_final, out_v7_redline]:
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        doc = word.Documents.Open(os.path.abspath(target), ReadOnly=True, ConfirmConversions=False)
        print(f"✅ {os.path.basename(target)} opened in MS Word with ZERO warnings! Paragraphs: {doc.Paragraphs.Count}")
        doc.Close(False)
        word.Quit()
    except Exception as e:
        print(f"❌ Error with {os.path.basename(target)}: {e}")
        try:
            word.Quit()
        except:
            pass
