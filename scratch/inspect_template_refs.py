import docx

doc = docx.Document('conference-template-a4_transitional.docx')
for i, p in enumerate(doc.paragraphs):
    if 'reference' in p.style.name.lower() or 'ref' in p.style.name.lower() or 'References' in p.text:
        print(f"P{i:02d} [{p.style.name}]: {repr(p.text)}")
