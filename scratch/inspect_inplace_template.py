import docx
import sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('conference-template-a4_transitional.docx')

for i in range(15):
    p = doc.paragraphs[i]
    sectPr = p._p.xpath('./w:pPr/w:sectPr')
    s_tag = ' [SECTPR]' if sectPr else ''
    print(f'P{i:02d} [{p.style.name:15s}]{s_tag}: {repr(p.text)}')
