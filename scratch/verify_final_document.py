import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml')
    root = ET.fromstring(doc_xml)
    
    # Check image size
    img1 = z.read('word/media/image1.png')
    print(f"✓ Figure 1 image size: {len(img1)} bytes")

def get_node_text(elem):
    texts = []
    for t in elem.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            texts.append(t.text)
    return ''.join(texts)

print("\n==================== VERIFICATION OF UPDATED DOCUMENT ====================")

for p in root.iter():
    tag = p.tag.split('}')[-1]
    if tag == 'p':
        txt = get_node_text(p).strip()
        if 'Robust Probabilistic Energy Forecasting' in txt:
            print("\n[1. TITLE]:\n", txt)
        elif txt.startswith('Abstract—'):
            print("\n[2. ABSTRACT]:\n", txt)
        elif 'The proposed GUMNetHet model resolves this bottleneck' in txt:
            print("\n[3. CONTRIBUTIONS & GITHUB]:\n", txt)
        elif 'Fig. 1. Neural network architecture' in txt or 'Fig. 1.' in txt:
            print("\n[4. FIG 1 CAPTION]:\n", txt)
        elif 'While the full dataset (2008–2026' in txt or 'To prevent look-ahead bias' in txt:
            print("\n[5. WALK-FORWARD PROTOCOL]:\n", txt[:250] + "...")
        elif 'Data and Code Availability:' in txt:
            print("\n[6. DATA AND CODE AVAILABILITY]:\n", txt)
        elif txt.startswith('Expanding walk-forward experiments on MG95'):
            print("\n[7. CONCLUSION]:\n", txt)

print("\n=== EQUATIONS VERIFICATION ===")
for tbl in root.iter():
    tag = tbl.tag.split('}')[-1]
    if tag == 'tbl':
        txt = get_node_text(tbl).strip()
        if any(f'({k})' in txt for k in [2, 4, 7]):
            print(f"Table Row Content: {txt}")

print("\n==================== VERIFICATION COMPLETE ====================")
