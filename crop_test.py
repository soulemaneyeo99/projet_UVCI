import sys
from PIL import Image

img_path = "/home/dev/projects/projet_UVCI/assets/secretaire_rapports_full.png"
with Image.open(img_path) as img:
    width, height = img.size
    print(f"Original: {width}x{height}")
    
    # We want to remove the browser tabs (dark mode or light mode) and the Windows taskbar.
    # The browser UI ends where the white app background starts.
    # The UVCI app has a white background (255,255,255) or a sidebar on the left.
    # Let's just crop 12% from top and 6% from bottom.
    top_crop = int(height * 0.13)
    bottom_crop = int(height * 0.06)
    
    cropped = img.crop((0, top_crop, width, height - bottom_crop))
    cropped.save(img_path)
    print(f"Cropped to: {cropped.size}")
