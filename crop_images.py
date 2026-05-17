import os
from PIL import Image

assets_dir = "/home/dev/projects/projet_UVCI/assets"
images_to_crop = [
    "admin_dashboard_full.png",
    "admin_cours.png",
    "admin_saisie_full.png",
    "secretaire_dashboard_full.png",
    "secretaire_enseignants_full.png",
    "secretaire_saisie_full.png",
    "secretaire_rapports_full.png",
    "enseignant_dashboard_full.png",
    "enseignant_activites_full.png",
    "enseignant_profil_full.png",
    "enseignant_recap_full.png",
    "resultat_pdf.png",
    "resultat_excel.png",
    "login_page.png"
]

for img_name in images_to_crop:
    img_path = os.path.join(assets_dir, img_name)
    if not os.path.exists(img_path):
        print(f"Not found: {img_name}")
        continue
        
    try:
        with Image.open(img_path) as img:
            width, height = img.size
            
            # Crop 1024x576 images (scaled down screenshots)
            if width == 1024 and height == 576:
                top_crop = 65
                bottom_crop = 26
                
                print(f"Cropping {img_name} ({width}x{height})")
                cropped_img = img.crop((0, top_crop, width, height - bottom_crop))
                cropped_img.save(img_path)
            else:
                print(f"Skipping {img_name} (dimensions: {width}x{height})")
    except Exception as e:
        print(f"Error processing {img_name}: {e}")

print("Done cropping.")
