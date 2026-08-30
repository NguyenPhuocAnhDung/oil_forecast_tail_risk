import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import sys
import re
import zipfile
from copy import deepcopy

def sanitize_equation_table(tbl_element):
    """
    Sets table width to exactly 5040 dxa (3.5 inches),
    Col 0 = 4400 dxa (formula), Col 1 = 640 dxa (equation number),
    Removes all borders, sets zero margins.
    """
    tbl = deepcopy(tbl_element)
    
    # 1. Update tblPr
    tblPr = tbl.xpath('./w:tblPr')
    if tblPr:
        tp = tblPr[0]
        # Remove existing tblW, tblBorders, tblCellMar
        for child in list(tp):
            tag = child.tag.split('}')[-1]
            if tag in ['tblW', 'tblBorders', 'tblCellMar']:
                tp.remove(child)
        # Set 5040 dxa width
        tp.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="5040" w:type="dxa"/>'))
        # Borderless
        tp.append(parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                            f'<w:top w:val="none"/>'
                            f'<w:left w:val="none"/>'
                            f'<w:bottom w:val="none"/>'
                            f'<w:right w:val="none"/>'
                            f'<w:insideH w:val="none"/>'
                            f'<w:insideV w:val="none"/>'
                            f'</w:tblBorders>'))
        # Zero cell margins
        tp.append(parse_xml(f'<w:tblCellMar {nsdecls("w")}>'
                            f'<w:top w:w="0" w:type="dxa"/>'
                            f'<w:left w:w="0" w:type="dxa"/>'
                            f'<w:bottom w:w="0" w:type="dxa"/>'
                            f'<w:right w:w="0" w:type="dxa"/>'
                            f'</w:tblCellMar>'))

    # 2. Update tblGrid
    tblGrid = tbl.xpath('./w:tblGrid')
    if tblGrid:
        tg = tblGrid[0]
        for gc in list(tg):
            tg.remove(gc)
        tg.append(parse_xml(f'<w:gridCol {nsdecls("w")} w:w="4400"/>'))
        tg.append(parse_xml(f'<w:gridCol {nsdecls("w")} w:w="640"/>'))

    # 3. Update rows and cells
    for row in tbl.xpath('./w:tr'):
        cells = row.xpath('./w:tc')
        if len(cells) >= 2:
            # Formula cell
            tcPr0 = cells[0].get_or_add_tcPr()
            for child in list(tcPr0):
                if child.tag.split('}')[-1] == 'tcW':
                    tcPr0.remove(child)
            tcPr0.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="4400" w:type="dxa"/>'))
            # Align center
            for p in cells[0].xpath('./w:p'):
                pPr = p.get_or_add_pPr()
                for jc in pPr.xpath('./w:jc'):
                    pPr.remove(jc)
                pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))

            # Equation number cell
            tcPr1 = cells[1].get_or_add_tcPr()
            for child in list(tcPr1):
                if child.tag.split('}')[-1] == 'tcW':
                    tcPr1.remove(child)
            tcPr1.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="640" w:type="dxa"/>'))
            # Align right
            for p in cells[1].xpath('./w:p'):
                pPr = p.get_or_add_pPr()
                for jc in pPr.xpath('./w:jc'):
                    pPr.remove(jc)
                pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="right"/>'))
                
    return tbl

def sanitize_data_table(tbl_element, num_cols):
    """
    Sets table width to exactly 5040 dxa (3.5 inches), distributes column widths evenly,
    applies IEEE formal 3-line borders, sets 7.5pt Times New Roman text, tight cell padding.
    """
    tbl = deepcopy(tbl_element)
    col_w = int(5040 / num_cols)
    remainder = 5040 - (col_w * num_cols)
    col_widths = [col_w + (remainder if i == num_cols-1 else 0) for i in range(num_cols)]

    # 1. tblPr
    tblPr = tbl.xpath('./w:tblPr')
    if tblPr:
        tp = tblPr[0]
        for child in list(tp):
            tag = child.tag.split('}')[-1]
            if tag in ['tblW', 'tblBorders', 'tblCellMar', 'jc']:
                tp.remove(child)
        tp.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="5040" w:type="dxa"/>'))
        tp.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
        # IEEE 3-line borders (Top, Bottom, and Header Bottom)
        tp.append(parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                            f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                            f'<w:left w:val="none"/>'
                            f'<w:right w:val="none"/>'
                            f'<w:insideH w:val="none"/>'
                            f'<w:insideV w:val="none"/>'
                            f'</w:tblBorders>'))
        # Tight padding
        tp.append(parse_xml(f'<w:tblCellMar {nsdecls("w")}>'
                            f'<w:top w:w="40" w:type="dxa"/>'
                            f'<w:left w:w="40" w:type="dxa"/>'
                            f'<w:bottom w:w="40" w:type="dxa"/>'
                            f'<w:right w:w="40" w:type="dxa"/>'
                            f'</w:tblCellMar>'))

    # 2. tblGrid
    tblGrid = tbl.xpath('./w:tblGrid')
    if tblGrid:
        tg = tblGrid[0]
        for gc in list(tg):
            tg.remove(gc)
        for w in col_widths:
            tg.append(parse_xml(f'<w:gridCol {nsdecls("w")} w:w="{w}"/>'))

    # 3. Cells
    rows = tbl.xpath('./w:tr')
    for r_idx, row in enumerate(rows):
        cells = row.xpath('./w:tc')
        for c_idx, cell in enumerate(cells):
            if c_idx < len(col_widths):
                w_val = col_widths[c_idx]
                tcPr = cell.get_or_add_tcPr()
                for child in list(tcPr):
                    if child.tag.split('}')[-1] in ['tcW', 'tcBorders']:
                        tcPr.remove(child)
                tcPr.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{w_val}" w:type="dxa"/>'))
                if r_idx == 0:
                    # Header bottom border
                    tcPr.append(parse_xml(f'<w:tcBorders {nsdecls("w")}><w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders>'))
                
                # Format cell text
                for p in cell.xpath('./w:p'):
                    pPr = p.get_or_add_pPr()
                    for jc in pPr.xpath('./w:jc'):
                        pPr.remove(jc)
                    pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
                    for r in p.xpath('./w:r'):
                        rPr = r.get_or_add_rPr()
                        for rFonts in rPr.xpath('./w:rFonts'):
                            rPr.remove(rFonts)
                        for sz in rPr.xpath('./w:sz'):
                            rPr.remove(sz)
                        rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'))
                        # 7.5pt for 7-column tables, 8pt for 5-column tables
                        sz_val = "15" if num_cols >= 7 else "16"
                        rPr.append(parse_xml(f'<w:sz {nsdecls("w")} w:val="{sz_val}"/>'))
                        if r_idx == 0:
                            rPr.append(parse_xml(f'<w:b {nsdecls("w")}/>'))

    return tbl

print("Sanitization helpers defined.")
