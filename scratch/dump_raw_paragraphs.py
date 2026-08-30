import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/raw_paragraphs_dump.txt', 'w', encoding='utf-8') as out_f:
    with zipfile.ZipFile('GUMNETHet_FAIRv6_final.backup_orig.docx', 'r') as z:
        doc_xml = z.read('word/document.xml').decode('utf-8')
        
        # 1. Abstract
        pos_abs = doc_xml.find('Abstract—')
        p_start = doc_xml.rfind('<w:p ', 0, pos_abs)
        p_end = doc_xml.find('</w:p>', pos_abs) + 6
        out_f.write("=== 1. ABSTRACT PARAGRAPH ===\n")
        out_f.write(doc_xml[p_start:p_end] + "\n\n")

        # 2. Contributions
        pos_c = doc_xml.find('The proposed GUMNetHet model resolves this bottleneck')
        p_start = doc_xml.rfind('<w:p ', 0, pos_c)
        p_end = doc_xml.find('</w:p>', pos_c) + 6
        out_f.write("=== 2. CONTRIBUTIONS PARAGRAPH ===\n")
        out_f.write(doc_xml[p_start:p_end] + "\n\n")

        # 3. Eq 2 Table
        pos_eq2 = doc_xml.find('name="eq_2"')
        tbl_start = doc_xml.rfind('<w:tbl', 0, pos_eq2)
        tbl_end = doc_xml.find('</w:tbl>', pos_eq2) + 8
        out_f.write("=== 3. EQ 2 TABLE ===\n")
        out_f.write(doc_xml[tbl_start:tbl_end] + "\n\n")

        # 4. Eq 4 Table
        pos_eq4 = doc_xml.find('name="eq_4"')
        tbl_start = doc_xml.rfind('<w:tbl', 0, pos_eq4)
        tbl_end = doc_xml.find('</w:tbl>', pos_eq4) + 8
        out_f.write("=== 4. EQ 3-4 TABLE ===\n")
        out_f.write(doc_xml[tbl_start:tbl_end] + "\n\n")

        # 5. Eq 7 Table
        pos_eq7 = doc_xml.find('name="eq_7"')
        tbl_start = doc_xml.rfind('<w:tbl', 0, pos_eq7)
        tbl_end = doc_xml.find('</w:tbl>', pos_eq7) + 8
        out_f.write("=== 5. EQ 6-7 TABLE ===\n")
        out_f.write(doc_xml[tbl_start:tbl_end] + "\n\n")

        # 6. Walk-Forward
        pos_wf = doc_xml.find('All test windows fall entirely within a period')
        p_start = doc_xml.rfind('<w:p ', 0, pos_wf)
        p_end = doc_xml.find('</w:p>', pos_wf) + 6
        out_f.write("=== 6. WALK-FORWARD PARAGRAPH ===\n")
        out_f.write(doc_xml[p_start:p_end] + "\n\n")

        # 7. Conclusion
        pos_concl = doc_xml.find('Expanding walk-forward experiments on MG95')
        p_start = doc_xml.rfind('<w:p ', 0, pos_concl)
        p_end = doc_xml.find('</w:p>', pos_concl) + 6
        out_f.write("=== 7. CONCLUSION PARAGRAPH ===\n")
        out_f.write(doc_xml[p_start:p_end] + "\n\n")

        # 8. References heading
        pos_ref = doc_xml.find('<w:t>REFERENCES</w:t>')
        p_start = doc_xml.rfind('<w:p ', 0, pos_ref)
        p_end = doc_xml.find('</w:p>', pos_ref) + 6
        out_f.write("=== 8. REFERENCES HEADING ===\n")
        out_f.write(doc_xml[p_start:p_end] + "\n\n")

print("Dumped all raw target XML paragraphs to scratch/raw_paragraphs_dump.txt")
