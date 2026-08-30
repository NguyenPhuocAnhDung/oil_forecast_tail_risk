import docx
import sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('conference-template-a4_transitional.docx')

print("=== CHECKING STYLE DEFINITIONS IN TEMPLATE ===")
styles_to_check = ['Heading 1', 'Heading 2', 'Heading 3', 'figure caption', 'table head', 'references', 'paper title', 'Author', 'Abstract', 'Keywords', 'Body Text']

for s_name in styles_to_check:
    try:
        s = doc.styles[s_name]
        pPr = s._element.xpath('./w:pPr')
        numPr = pPr[0].xpath('./w:numPr') if pPr else []
        print(f"Style '{s_name}': numPr={len(numPr) > 0}")
    except KeyError:
        print(f"Style '{s_name}': NOT FOUND")
