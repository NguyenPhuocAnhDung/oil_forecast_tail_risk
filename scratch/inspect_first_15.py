import docx

doc = docx.Document('conference-template-a4_transitional.docx')
for i in range(15):
    p = doc.paragraphs[i]
    print(f'P{i:02d} [style={p.style.name:15s}]: text={repr(p.text)}')
