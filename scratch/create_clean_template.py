import zipfile
import re

def create_cleaned_template(src_path, dst_path):
    print(f"Creating cleaned template without duplicate numbering from {src_path} -> {dst_path}...")
    with zipfile.ZipFile(src_path, 'r') as z_in:
        with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
            for item in z_in.infolist():
                data = z_in.read(item.filename)
                if item.filename == 'word/styles.xml':
                    text = data.decode('utf-8')
                    # Strip all <w:numPr>...</w:numPr> from styles.xml
                    text_clean = re.sub(r'<w:numPr>.*?</w:numPr>', '', text)
                    data = text_clean.encode('utf-8')
                z_out.writestr(item, data)
    print("Cleaned template created successfully!")

if __name__ == '__main__':
    create_cleaned_template('conference-template-a4_transitional.docx', 'conference-template-a4_clean_styles.docx')
