import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

src_doc = docx.Document('GUMNETHet_FAIRv3.docx')
t4 = src_doc.tables[4] # Table 4 (Eq 6 & 7)

print("=== TABLE 4 XML ===")
print(t4._tbl.xml[:1000])

for row_idx, r in enumerate(t4.rows):
    for c_idx, c in enumerate(r.cells):
        tcW = c._tc.tcPr.xpath('./w:tcW')
        w_val = tcW[0].get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w') if tcW else 'None'
        print(f"Row {row_idx}, Col {c_idx}: tcW={w_val}, text={repr(c.text)}")
