import zipfile
import re
import os

def clean_template_styles(docx_path):
    print(f"Inspecting and cleaning styles in {docx_path}...")
    with zipfile.ZipFile(docx_path, 'r') as z:
        styles_xml = z.read('word/styles.xml').decode('utf-8')
        doc_xml = z.read('word/document.xml').decode('utf-8')
        
    # Check styles with numPr
    styles_with_num = re.findall(r'<w:style [^>]*w:styleId="([^"]+)"[^>]*>.*?<w:numPr>.*?</w:style>', styles_xml, re.DOTALL)
    print(f"Styles with numPr: {styles_with_num}")

clean_template_styles('conference-template-a4_transitional.docx')
