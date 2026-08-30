import win32com.client
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

for name in ['GUMNETHet_FAIRv6_final.docx', 'GUMNETHet_FAIRv6_redline.docx']:
    docx_path = os.path.abspath(os.path.join(r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk', name))
    print(f"Testing opening {docx_path} in MS Word COM...")
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        doc = word.Documents.Open(docx_path, ReadOnly=True, ConfirmConversions=False)
        print(f"✓ {name} opened successfully! Paragraphs: {doc.Paragraphs.Count}")
        doc.Close(False)
        word.Quit()
    except Exception as e:
        print(f"❌ Error opening {name}: {e}")
        try:
            word.Quit()
        except:
            pass
