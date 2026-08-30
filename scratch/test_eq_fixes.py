import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_orig = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(backup_orig, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

# Let's inspect all equation tables and design the exact replacement for each
# Table 1: Eq 1 (Rt->t+h, c = ln(Pt+h, c) - ln(Pt, c))
# Table 2: Eq 2 (Pt+h, c = Pt, c * exp(Rt->t+h, c))
# Table 3: Eq 3 & 4
# Table 4: Eq 5 (ht = GRU(xt, ht-1), fGRU = hL \in Rd)
# Table 5: Eq 6 & 7
# Table 6: Eq 8, 9, 10
# Table 7: Eq 11 (y_hat = Head(f_fused) + gamma * x_target)
# Table 8: Eq 12, 13, 14

print("Loaded doc_xml successfully")
