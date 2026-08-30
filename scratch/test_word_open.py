import win32com.client
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

docx_path = os.path.abspath(r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx')

print(f"Testing opening {docx_path} in MS Word COM interface...")
try:
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    doc = word.Documents.Open(docx_path, ReadOnly=True, ConfirmConversions=False)
    print(f"✓ MS Word opened successfully! Paragraph count: {doc.Paragraphs.Count}")
    doc.Close(False)
    word.Quit()
    print("✓ MS Word closed cleanly without errors!")
except Exception as e:
    print(f"❌ Error opening in MS Word: {e}")
    try:
        word.Quit()
    except:
        pass
