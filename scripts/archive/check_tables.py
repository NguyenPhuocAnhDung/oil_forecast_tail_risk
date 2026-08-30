import docx
doc = docx.Document('docs/Bản_thảo_GUMNET_v2.docx')
for i, table in enumerate(doc.tables):
    if len(table.rows) > 0:
        first_row = [cell.text.strip() for cell in table.rows[0].cells]
        print(f"Table {i}: {len(table.rows)} rows, first row: {first_row}")
