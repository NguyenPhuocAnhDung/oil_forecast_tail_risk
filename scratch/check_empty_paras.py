import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('GUMNETHet_FAIRv4_final_IEEE.docx')

for i, p in enumerate(doc.paragraphs):
    sectPr = p._p.xpath('./w:pPr/w:sectPr')
    if sectPr:
        print(f"P{i:02d} [{p.style.name}] (contains sectPr): '{p.text[:40]}'")
    elif not p.text.strip():
        print(f"P{i:02d} [{p.style.name}] EMPTY PARAGRAPH")
