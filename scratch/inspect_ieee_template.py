import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('conference-template-a4_transitional.docx')
print('=== SECTIONS IN IEEE TEMPLATE ===')
for i, s in enumerate(doc.sections):
    sectPr = s._sectPr
    cols = sectPr.xpath('./w:cols')
    col_str = 'no cols element'
    if cols:
        col_str = f'num={cols[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num")}, space={cols[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}space")}'
    print(f'Section {i}: start_type={s.start_type}, w={s.page_width.pt:.1f}, h={s.page_height.pt:.1f}, top={s.top_margin.pt:.1f}, bottom={s.bottom_margin.pt:.1f}, left={s.left_margin.pt:.1f}, right={s.right_margin.pt:.1f} | cols: {col_str}')

print('\n=== ALL PARAGRAPH STYLES IN IEEE TEMPLATE ===')
for s in doc.styles:
    if s.type == docx.enum.style.WD_STYLE_TYPE.PARAGRAPH:
        print(f' - Paragraph Style: {s.name}')

print('\n=== TEMPLATE PARAGRAPHS & STYLES (FIRST 40) ===')
for i, p in enumerate(doc.paragraphs[:40]):
    print(f'P{i:02d} [style={p.style.name:15s}]: {repr(p.text[:60])}')
