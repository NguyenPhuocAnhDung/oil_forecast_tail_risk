import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml')
    root = ET.fromstring(doc_xml)

def get_node_text(elem):
    texts = []
    for t in elem.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            texts.append(t.text)
    return ''.join(texts)

print("=== LOCATING PARAGRAPHS WITH TREE TRAVERSAL ===")
for p_idx, p in enumerate(root.iter()):
    tag = p.tag.split('}')[-1]
    if tag == 'p':
        text = get_node_text(p)
        if text.startswith('Abstract'):
            print(f"P[{p_idx}] is Abstract! Elements inside:")
            for child in p:
                print("  ", child.tag.split('}')[-1], get_node_text(child))
        elif 'The proposed GUMNetHet model resolves this bottleneck' in text:
            print(f"P[{p_idx}] is Contributions! Elements inside:")
            for child in p:
                print("  ", child.tag.split('}')[-1], get_node_text(child))
        elif 'To prevent look-ahead bias' in text:
            print(f"P[{p_idx}] is Walk-Forward! Elements inside:")
            for child in p:
                print("  ", child.tag.split('}')[-1], get_node_text(child))
        elif 'Expanding walk-forward experiments on MG95' in text:
            print(f"P[{p_idx}] is Conclusion! Elements inside:")
            for child in p:
                print("  ", child.tag.split('}')[-1], get_node_text(child))
