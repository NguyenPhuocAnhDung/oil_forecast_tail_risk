#!/usr/bin/env python3
from PIL import Image, ImageDraw

img_path = 'docs/figures/architecture_system.png'
img = Image.open(img_path)
draw = ImageDraw.Draw(img)

# We paint a white rectangle over the outdated text "Không chứa hình phạt (penalty term)."
# Left=530, Top=760, Right=820, Bottom=788
draw.rectangle([530, 760, 820, 788], fill='white')

img.save(img_path)
print("Removed 'Không chứa hình phạt' text from Section 3.")
