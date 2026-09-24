"""
Inject OMML (Word Math) equations into the manuscript for the DA formula.

Converts plain-text notation into proper Word Equation objects (m:oMath).

Run: python3 scripts/inject_omml_equations.py
"""

import docx
from docx.oxml.ns import qn
from lxml import etree
import re, copy

MATH_NS  = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WORD_NS  = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def m(tag): return f'{{{MATH_NS}}}{tag}'
def w(tag): return f'{{{WORD_NS}}}{tag}'
def XML(s): return f'{{http://www.w3.org/XML/1998/namespace}}{s}'

# ── OMML Helpers ─────────────────────────────────────────────────────────────

def make_rpr_math():
    rpr = etree.Element(w('rPr'))
    rf  = etree.SubElement(rpr, w('rFonts'))
    rf.set(w('ascii'),  'Cambria Math')
    rf.set(w('hAnsi'),  'Cambria Math')
    return rpr

def make_ctrl_pr():
    ctrl = etree.Element(m('ctrlPr'))
    ctrl.append(make_rpr_math())
    return ctrl

def math_run(text, italic=True):
    r = etree.Element(m('r'))
    rpr = etree.SubElement(r, w('rPr'))
    rf  = etree.SubElement(rpr, w('rFonts'))
    rf.set(w('ascii'),  'Cambria Math')
    rf.set(w('hAnsi'),  'Cambria Math')
    if not italic:
        i_elem = etree.SubElement(rpr, w('i'))
        i_elem.set(w('val'), '0')
    t = etree.SubElement(r, m('t'))
    t.text = text
    return r

def sub_script(base_e, sub_e):
    ss = etree.Element(m('sSub'))
    pr = etree.SubElement(ss, m('sSubPr'))
    pr.append(make_ctrl_pr())
    e = etree.SubElement(ss, m('e'));   e.append(base_e)
    s = etree.SubElement(ss, m('sub')); s.append(sub_e)
    return ss

def nary_sum(sub_e, sup_e, arg_e):
    n  = etree.Element(m('nary'))
    pr = etree.SubElement(n, m('naryPr'))
    ch = etree.SubElement(pr, m('chr')); ch.set(m('val'), '\u2211')
    ll = etree.SubElement(pr, m('limLoc')); ll.set(m('val'), 'undOvr')
    pr.append(make_ctrl_pr())
    sub = etree.SubElement(n, m('sub')); sub.append(sub_e)
    sup = etree.SubElement(n, m('sup')); sup.append(sup_e)
    e   = etree.SubElement(n, m('e'));   e.append(arg_e)
    return n

def frac(num_e, den_e):
    f  = etree.Element(m('f'))
    pr = etree.SubElement(f, m('fPr'))
    pr.append(make_ctrl_pr())
    num = etree.SubElement(f, m('num')); num.append(num_e)
    den = etree.SubElement(f, m('den')); den.append(den_e)
    return f

def hat_acc(base_e):
    acc = etree.Element(m('acc'))
    pr  = etree.SubElement(acc, m('accPr'))
    ch  = etree.SubElement(pr, m('chr')); ch.set(m('val'), '\u0302')
    pr.append(make_ctrl_pr())
    e = etree.SubElement(acc, m('e')); e.append(base_e)
    return acc

def omath(*elems):
    om = etree.Element(m('oMath'))
    for e in elems: om.append(e)
    return om

def word_run(text):
    r = etree.Element(w('r'))
    t = etree.SubElement(r, w('t'))
    t.set(XML('space'), 'preserve')
    t.text = text
    return r

# ── Symbols ──────────────────────────────────────────────────────────────────

def P_hat_th():  # P̂_{t+h}
    return omath(sub_script(hat_acc(math_run('P')), math_run('t+h')))

def P_t():       # P_t
    return omath(sub_script(math_run('P'), math_run('t')))

def P_th():      # P_{t+h}
    return omath(sub_script(math_run('P'), math_run('t+h')))

def DA_h():      # DA_h
    return omath(sub_script(math_run('DA', italic=False), math_run('h')))

def q_hat_05():  # q̂_{0.5}
    return omath(sub_script(hat_acc(math_run('q')), math_run('0.5')))

def sum_t1_M():  # ∑_{t=1}^{M}
    return omath(nary_sum(
        sub_script(math_run('t'), math_run('=1')),
        math_run('M'),
        math_run(''),
    ))

def frac_1_M():  # 1/M as fraction
    return omath(frac(math_run('1'), math_run('M')))

# ── Main ─────────────────────────────────────────────────────────────────────

doc = docx.Document('GUMNETHet_FAIRv8.docx')
p42  = doc.paragraphs[42]
p_elem = p42._p

# Read Run0 text to extract prefix and suffix
run0_t = p_elem.findall(w('r'))[0].find(w('t')).text

idx_start = run0_t.find(': DA_h')
idx_end   = run0_t.find('0 otherwise.') + len('0 otherwise.')

text_before = run0_t[: idx_start + 2]   # "...defined as: "
text_after  = run0_t[idx_end :]         # " Probabilistic..."

# Remove ALL existing w:r children  
for child in list(p_elem):
    if child.tag == w('r'):
        p_elem.remove(child)

# ── Reassemble P42 ────────────────────────────────────────────────────────────

SEQ = [
    word_run(text_before),         # "...Directional Accuracy (DA, %) is formally defined as: "
    DA_h(),                        # DA_h  (oMath)
    word_run(' = '),
    frac_1_M(),                    # (1/M)
    word_run(' \u00b7\u00a0'),    # · (centre dot)
    sum_t1_M(),                    # ∑_{t=1}^{M}
    word_run(' 1\u2061(\u2009sgn\u2061('),   # 1( sgn(
    P_hat_th(),                    # P̂_{t+h}
    word_run(' \u2212 '),         # −
    P_t(),                         # P_t
    word_run(') = sgn\u2061('),   # ) == sgn(   NOTE: use single = for readability in Word
    P_th(),                        # P_{t+h}
    word_run(' \u2212 '),
    P_t(),                         # P_t
    word_run(
        ')) \u00d7 100%, '
        'where M = T \u2212 h + 1 denotes the total number of evaluated forecast steps '
        'in the out-of-sample window, '
    ),
    P_t(),                         # P_t inline
    word_run(' is the known spot price at forecast origin t, '),
    P_hat_th(),                    # P̂_{t+h}
    word_run(
        ' is the predicted spot price level recovered from the median quantile return ('
    ),
    q_hat_05(),                    # q̂_{0.5}
    word_run(
        ') via (2), and 1(\u00b7) is the indicator function equal to 1 if the '
        'predicted price change sign matches the realized price change sign, '
        'and 0 otherwise.'
    ),
    word_run(text_after),
    word_run(
        ' All baselines are implemented with their published default hyperparameters '
        'and standard squared-error training objectives, without additional horizon-specific tuning. '
        'Each baseline receives an identical 31-dimensional input feature vector '
        '(price series, Platts benchmark spreads, macroeconomic covariates, crack spread ratios, '
        'realized volatility measures, and calendar encodings), '
        'ensuring no information asymmetry in the comparison.'
    ),
]

for elem in SEQ:
    p_elem.append(elem)

doc.save('GUMNETHet_FAIRv8.docx')
doc.save('GUMNETHet_FAIRv8_revised.docx')
print('Saved.')

# Verify
doc2   = docx.Document('GUMNETHet_FAIRv8.docx')
p42v   = doc2.paragraphs[42]
omaths = p42v._p.findall(f'.//{{{MATH_NS}}}oMath')
print(f'P42 now has {len(omaths)} oMath objects')
print(f'P42 plain text preview: {p42v.text[:80]}')
