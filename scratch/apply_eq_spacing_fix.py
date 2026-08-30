import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_orig = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'
target_docx = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(backup_orig, 'r') as z:
    zip_entries = {name: z.read(name) for name in z.namelist()}

doc_xml = zip_entries['word/document.xml'].decode('utf-8')

# 1. Fix line spacing across all equation tables: remove w:line="12.60pt"
# Replace <w:spacing w:before="2pt" w:after="2pt" w:line="12.60pt" w:lineRule="auto"/> with <w:spacing w:before="3pt" w:after="3pt"/>
doc_xml = re.sub(r'<w:spacing\s+w:before="2pt"\s+w:after="2pt"\s+w:line="12\.60pt"\s+w:lineRule="auto"/>',
                 r'<w:spacing w:before="3pt" w:after="3pt"/>', doc_xml)

# 2. Fix Eq (4): Use concise notation TemporalAttn(LN(Proj([out3 || out7 || out15]))) \in R^d
# Let's inspect the math inside Eq 4
old_eq4_math = (
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>f</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>CNN</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve"> = TemporalAttention(LayerNorm(Proj(Concat(</m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>out</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>3</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">, </m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>out</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>7</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">, </m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>out</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>15</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">)))) ∈ </m:t></m:r>'
    '<m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>d</m:t></m:r></m:sup></m:sSup>'
)

new_eq4_math = (
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>f</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>CNN</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve"> = Attn(LN(Proj([</m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>out</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>3</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve"> ‖ </m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>out</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>7</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve"> ‖ </m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>out</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>15</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">]))) ∈ </m:t></m:r>'
    '<m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>d</m:t></m:r></m:sup></m:sSup>'
)
assert old_eq4_math in doc_xml, "Old Eq 4 math not matched!"
doc_xml = doc_xml.replace(old_eq4_math, new_eq4_math, 1)
print("✓ Eq (4) compacted with clean standard notation")

# 3. Fix Eq (7): Use concise notation LN(Proj([ReLU(W_lin x^KAN) || ReLU(W_wav psi(z))])) \in R^d
old_eq7_math = (
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>f</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>KAN</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve"> = LayerNorm(Proj(Concat(ReLU(</m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>lin</m:t></m:r></m:sub></m:sSub>'
    '<m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>x</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>KAN</m:t></m:r></m:sup></m:sSup>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>), ReLU(</m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>wav</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">ψ(z)))) ∈ </m:t></m:r>'
    '<m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>d</m:t></m:r></m:sup></m:sSup>'
)

new_eq7_math = (
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>f</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>KAN</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve"> = LN(Proj([ReLU(</m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>lin</m:t></m:r></m:sub></m:sSub>'
    '<m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>x</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>KAN</m:t></m:r></m:sup></m:sSup>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">) ‖ ReLU(</m:t></m:r>'
    '<m:sSub><m:sSubPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSubPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>W</m:t></m:r></m:e><m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>wav</m:t></m:r></m:sub></m:sSub>'
    '<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">ψ(z))])) ∈ </m:t></m:r>'
    '<m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>d</m:t></m:r></m:sup></m:sSup>'
)
assert old_eq7_math in doc_xml, "Old Eq 7 math not matched!"
doc_xml = doc_xml.replace(old_eq7_math, new_eq7_math, 1)
print("✓ Eq (7) compacted with clean standard notation")

# 4. Expand equation table cell widths across all equation tables:
# Replace <w:tcW w:w="220pt" w:type="dxa"/> with <w:tcW w:w="228pt" w:type="dxa"/>
# and <w:tcW w:w="32pt" w:type="dxa"/> with <w:tcW w:w="24pt" w:type="dxa"/>
# and set <w:gridCol w:w="4560"/><w:gridCol w:w="480"/>
doc_xml = doc_xml.replace('<w:gridCol w:w="4400"/><w:gridCol w:w="640"/>',
                          '<w:gridCol w:w="4560"/><w:gridCol w:w="480"/>')
doc_xml = doc_xml.replace('<w:tcW w:w="220pt" w:type="dxa"/>', '<w:tcW w:w="228pt" w:type="dxa"/>')
doc_xml = doc_xml.replace('<w:tcW w:w="32pt" w:type="dxa"/>', '<w:tcW w:w="24pt" w:type="dxa"/>')

# 5. Remove zero-margin clipping: change tcMar start/end from 4pt to 1pt
doc_xml = doc_xml.replace(
    '<w:tcMar><w:top w:w="4pt" w:type="dxa"/><w:start w:w="4pt" w:type="dxa"/><w:bottom w:w="4pt" w:type="dxa"/><w:end w:w="4pt" w:type="dxa"/></w:tcMar>',
    '<w:tcMar><w:top w:w="2pt" w:type="dxa"/><w:start w:w="1pt" w:type="dxa"/><w:bottom w:w="2pt" w:type="dxa"/><w:end w:w="1pt" w:type="dxa"/></w:tcMar>'
)

# Write back into zip
zip_entries['word/document.xml'] = doc_xml.encode('utf-8')

with zipfile.ZipFile(target_docx, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in zip_entries.items():
        z.writestr(filename, data)

print(f"\n🎉 Successfully updated all equations in {target_docx} to prevent wrapping and clipping!")
