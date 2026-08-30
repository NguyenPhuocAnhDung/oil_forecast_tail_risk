import docx

doc = docx.Document('conference-template-a4_transitional.docx')
for i, s in enumerate(doc.sections):
    print(f'Section {i}: start_type={s.start_type}')

# Find where section breaks are in document.xml
p_list = doc.paragraphs
for i, p in enumerate(p_list):
    sectPr = p._p.xpath('./w:pPr/w:sectPr')
    if sectPr:
        print(f'Paragraph {i:02d} has sectPr! Text: {repr(p.text[:40])}')
