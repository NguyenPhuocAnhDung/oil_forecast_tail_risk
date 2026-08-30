import docx
import zipfile
import xml.etree.ElementTree as ET

def verify_file(fname):
    print("=" * 65)
    print(f"VERIFYING OMML & HYPERLINKS IN: {fname}")
    print("=" * 65)
    
    with zipfile.ZipFile(fname, 'r') as z:
        tree = ET.fromstring(z.read('word/document.xml'))
        ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
        }
        
        # 1. OMML Equations
        omaths = tree.findall('.//m:oMath', ns)
        print(f"1. Native OMML Math Elements: {len(omaths)} elements found")
        
        # 2. Hyperlinks
        links = tree.findall('.//w:hyperlink', ns)
        anchors = [l.get(f'{{{ns["w"]}}}anchor') for l in links if l.get(f'{{{ns["w"]}}}anchor')]
        
        eq_links = [a for a in anchors if a.startswith('eq_')]
        tbl_links = [a for a in anchors if a.startswith('tbl_')]
        fig_links = [a for a in anchors if a.startswith('fig_')]
        ref_links = [a for a in anchors if a.startswith('ref_')]
        
        print(f"2. Interactive Hyperlinks (Click-to-Jump):")
        print(f"   - Equation Links: {len(eq_links)} -> {sorted(set(eq_links))}")
        print(f"   - Table Links: {len(tbl_links)} -> {sorted(set(tbl_links))}")
        print(f"   - Figure Links: {len(fig_links)} -> {sorted(set(fig_links))}")
        print(f"   - Citation Links: {len(ref_links)} -> {len(set(ref_links))} unique references")
        
        # 3. Bookmarks
        bms = [b.get(f'{{{ns["w"]}}}name') for b in tree.findall('.//w:bookmarkStart', ns) if b.get(f'{{{ns["w"]}}}name')]
        print(f"3. Registered Bookmarks:")
        print(f"   - Table Bookmarks: {[b for b in bms if b.startswith('tbl_')]}")
        print(f"   - Figure Bookmarks: {[b for b in bms if b.startswith('fig_')]}")
        print(f"   - Equation Bookmarks: {[b for b in bms if b.startswith('eq_')]}")
        
        # 4. Table Shading Check
        shds = tree.findall('.//w:shd', ns)
        non_white = [s.get(f'{{{ns["w"]}}}fill') for s in shds if s.get(f'{{{ns["w"]}}}fill') not in ['FFFFFF', 'ffffff', None]]
        print(f"4. Table Shading (Pure White Check):")
        print(f"   - Total cell shading elements: {len(shds)}")
        print(f"   - Non-white shading elements: {len(non_white)} (Expected: 0)")
        
        # 5. Content Checks
        doc = docx.Document(fname)
        full_text = " ".join([p.text for p in doc.paragraphs])
        print(f"5. Key Narrative Verification:")
        print(f"   - Sample size '4.512' count: {full_text.count('4.512')} | '4.517' count: {full_text.count('4.517')}")
        print(f"   - Dung Quất & Nghi Sơn mentioned: {'Dung Quất' in full_text and 'Nghi Sơn' in full_text}")
        print(f"   - Singapore Platts MOPS mentioned: {'Singapore' in full_text and 'MOPS' in full_text}")
        print(f"   - Petrolimex & PVOIL mentioned: {'Petrolimex' in full_text and 'PVOIL' in full_text}")
        print(f"   - Retail BOG / step-function removed: {'Quỹ bình ổn' not in full_text and 'step-function' not in full_text}")

if __name__ == '__main__':
    for f in ['GUMNETHet_FAIRv2_template.docx', 'GUMNETHET_FAIR_v2_TIENG_VIET.docx', 'GUMNETHET_FAIR_v2.docx']:
        verify_file(f)
