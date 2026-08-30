import zipfile
import xml.etree.ElementTree as ET
import os

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    rels_xml = z.read('word/_rels/document.xml.rels')
    rels_root = ET.fromstring(rels_xml)
    rel_map = {}
    for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        rel_map[r.attrib['Id']] = r.attrib['Target']
    print("Document Relationships:")
    for rid, target in rel_map.items():
        if 'image' in target:
            print(f"  {rid} -> {target}")

    doc_xml = z.read('word/document.xml')
    doc_root = ET.fromstring(doc_xml)
    
    print("\nDrawings in document:")
    ns = {
        'w': 'http://purl.oclc.org/ooxml/wordprocessingml/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://purl.oclc.org/ooxml/officeDocument/relationships',
        'wp': 'http://schemas.openxmlformats.org/drawingml/wordprocessingDrawing'
    }
    
    # search for blip elements
    p_idx = 0
    for p in doc_root.iter():
        tag = p.tag.split('}')[-1]
        if tag == 'p':
            p_idx += 1
            p_text = ''.join([t.text for t in p.iter() if (t.tag.endswith('}t') or t.tag == 't') and t.text])
            for blip in p.iter():
                btag = blip.tag.split('}')[-1]
                if btag == 'blip':
                    embed_id = None
                    for k, v in blip.attrib.items():
                        if k.endswith('embed'):
                            embed_id = v
                    target_file = rel_map.get(embed_id, 'unknown')
                    print(f"P#{p_idx} has image: embed={embed_id} -> {target_file} (Caption / Next text: {p_text[:80]})")

    # Extract all images from zip to scratch for inspection
    os.makedirs('scratch/extracted_media', exist_ok=True)
    for name in z.namelist():
        if 'word/media/' in name:
            z.extract(name, 'scratch/extracted_media')
            print(f"Extracted {name} (size: {len(z.read(name))} bytes)")
