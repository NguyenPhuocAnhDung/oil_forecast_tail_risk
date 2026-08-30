import docx

doc = docx.Document('conference-template-a4_transitional.docx')
for i in range(12):
    p = doc.paragraphs[i]
    print(f'=== P{i:02d} (style={p.style.name}) ===')
    print(repr(p.text))
    pPr = p._p.xpath('./w:pPr')
    if pPr:
        print('  pPr XML:', pPr[0].xml[:300].replace('\n', ' '))
