import docx

doc = docx.Document('conference-template-a4_transitional.docx')
for i in range(12):
    p = doc.paragraphs[i]
    print(f'=== P{i:02d} ({p.style.name}) ===')
    for r in p.runs:
        print(f'  run (bold={r.bold}, italic={r.italic}): {repr(r.text)}')
    print('  pPr:', p._p.xpath('./w:pPr')[0].xml.replace('\n', ' ') if p._p.xpath('./w:pPr') else 'None')
