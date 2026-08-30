import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

f = 'GUMNETHet_FAIRv4_final_updated.docx'
doc = docx.Document(f)

print(f"=== FULL ELEMENT AUDIT OF {f} ===")

body_children = list(doc._body._body)
print(f"Total Body XML elements: {len(body_children)}")

table_idx = 0
for idx, elem in enumerate(body_children):
    tag = elem.tag.split('}')[-1]
    if tag == 'p':
        p = docx.text.paragraph.Paragraph(elem, doc)
        txt = p.text.strip()
        st = p.style.name if p.style else 'None'
        if any(h in st for h in ['Heading', 'title', 'head', 'caption', 'Keywords', 'Abstract', 'references']) or len(txt) < 80:
            print(f"Elem {idx:03d} [P - {st:14s}]: {txt[:70]}")
    elif tag == 'tbl':
        t = docx.table.Table(elem, doc)
        print(f"Elem {idx:03d} [TBL #{table_idx:02d} ({len(t.rows)}x{len(t.columns)})]: First cell: {repr(t.cell(0,0).text[:30])}")
        table_idx += 1
    elif tag == 'sectPr':
        print(f"Elem {idx:03d} [SECTPR]")
