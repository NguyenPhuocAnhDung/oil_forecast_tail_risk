import docx

doc = docx.Document('GUMNETHet_FAIRv3.docx')
print('=== SECTIONS IN GUMNETHet_FAIRv3.docx ===')
for i, s in enumerate(doc.sections):
    sectPr = s._sectPr
    cols = sectPr.xpath('./w:cols')
    col_str = 'no cols'
    if cols:
        col_str = f'num={cols[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num")}, space={cols[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}space")}'
    print(f'Section {i}: start_type={s.start_type}, top={s.top_margin.pt:.1f}pt, bot={s.bottom_margin.pt:.1f}pt, left={s.left_margin.pt:.1f}pt, right={s.right_margin.pt:.1f}pt | cols: {col_str}')
