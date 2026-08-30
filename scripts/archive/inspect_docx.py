import docx
import os

docs_dir = 'docs'
files = os.listdir(docs_dir)
v1_file = [f for f in files if f.startswith('bản thảo GUMNET_v1') and f.endswith('.docx')][0]
path = os.path.join(docs_dir, v1_file)

doc = docx.Document(path)
with open('doc1_paras.txt', 'w', encoding='utf-8') as f:
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if text:
            f.write(f'{i}: {text[:100]}\n')
