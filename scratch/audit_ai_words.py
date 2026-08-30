import zipfile
import xml.etree.ElementTree as ET
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    root = ET.fromstring(z.read('word/document.xml'))

def get_text(node):
    txts = []
    for t in node.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            txts.append(t.text)
    return ''.join(txts)

paras = []
for p in root.iter():
    if p.tag.split('}')[-1] == 'p':
        t = get_text(p).strip()
        if t:
            paras.append(t)

print(f"Total paragraphs in document: {len(paras)}")

# Words that sound like AI translation / hype / overly strong
ai_words = [
    'synergize', 'synergizes', 'leverage', 'leverages', 'leveraging',
    'profound', 'distinctive', 'bottleneck', 'dichotomy',
    'catastrophic', 'urgent operational necessity', 'directly serving',
    'surges', 'soars', 'substantiating', 'corroborate', 'corroborating',
    'delve', 'testament', 'pivotal', 'crucial', 'game-changing',
    'flawless', 'superiority', 'indispensable', 'vital', 'imperative',
    'paramount', 'moreover', 'furthermore', 'notably', 'it is worth noting',
    'in essence', 'serves to', 'stands as', 'showcases', 'underpins',
    'robustness', 'grounded in', 'fat-tailed regime shifts', 'massive',
    'uniquely suited', 'drastically', 'exponentially compounding'
]

print("\n=== SCANNING FOR OVERLY STRONG / AI-FLAVORED WORDS ===")
found_counts = {}
for i, p in enumerate(paras):
    for w in ai_words:
        if re.search(rf'\b{re.escape(w)}\b', p, re.IGNORECASE):
            found_counts[w] = found_counts.get(w, 0) + 1
            if found_counts[w] <= 3:
                print(f"\n[Para {i+1}] Word '{w}':")
                print(f"  Text: {p[:200]}...")

print("\nSummary of AI-flavored / Strong word occurrences:")
for w, c in sorted(found_counts.items(), key=lambda x: -x[1]):
    print(f"  - '{w}': {c} times")
