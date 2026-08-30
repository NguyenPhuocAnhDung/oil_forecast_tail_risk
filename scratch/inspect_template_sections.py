import docx

doc = docx.Document('conference-template-a4_transitional.docx')
for i, s in enumerate(doc.sections):
    sectPr = s._sectPr
    cols = sectPr.xpath('./w:cols')
    col_str = 'no cols'
    if cols:
        col_str = f'num={cols[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num")}, space={cols[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}space")}'
    type_elem = sectPr.xpath('./w:type')
    t_val = type_elem[0].get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if type_elem else 'default'
    print(f'Section {i}: type={t_val}, top={s.top_margin.pt:.1f}pt, bot={s.bottom_margin.pt:.1f}pt, left={s.left_margin.pt:.1f}pt, right={s.right_margin.pt:.1f}pt | cols: {col_str}')

for i, p in enumerate(doc.paragraphs[:15]):
    # check if paragraph has sectPr
    sectPr = p._p.xpath('./w:pPr/w:sectPr')
    s_info = ' (HAS sectPr)' if sectPr else ''
    print(f'P{i:02d} [{p.style.name:15s}]{s_info}: {repr(p.text[:60])}')
