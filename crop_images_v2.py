import os
import glob
from PIL import Image

# Re-copy originals
commands = [
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778971841384.png /home/dev/projects/projet_UVCI/assets/admin_cours.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778971815519.png /home/dev/projects/projet_UVCI/assets/admin_dashboard_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778977065206.png /home/dev/projects/projet_UVCI/assets/admin_saisie_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778973497627.png /home/dev/projects/projet_UVCI/assets/secretaire_dashboard_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778973518984.png /home/dev/projects/projet_UVCI/assets/secretaire_enseignants_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778977190085.png /home/dev/projects/projet_UVCI/assets/secretaire_saisie_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778977225460.png /home/dev/projects/projet_UVCI/assets/secretaire_rapports_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778973713195.png /home/dev/projects/projet_UVCI/assets/enseignant_dashboard_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778976725426.png /home/dev/projects/projet_UVCI/assets/enseignant_activites_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778976791533.png /home/dev/projects/projet_UVCI/assets/enseignant_recap_full.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778973994384.png /home/dev/projects/projet_UVCI/assets/resultat_excel.png",
    "cp /home/dev/.gemini/antigravity/brain/fb405462-c0cd-40f3-976a-313fe8c0555c/media__1778974104441.png /home/dev/projects/projet_UVCI/assets/resultat_pdf.png"
]

for cmd in commands:
    os.system(cmd)

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
    "enseignant_recap_full.png"
]

for img_name in images_to_crop:
    img_path = os.path.join(assets_dir, img_name)
    if not os.path.exists(img_path):
        continue
    try:
        with Image.open(img_path) as img:
            width, height = img.size
            if width == 1024 and height == 576:
                # 145px top to remove tabs, url, bookmarks, and the extra bar
                # 45px bottom to remove the windows taskbar
                top_crop = 145
                bottom_crop = 45
                
                cropped_img = img.crop((0, top_crop, width, height - bottom_crop))
                cropped_img.save(img_path)
                print(f"Aggressively cropped {img_name}")
    except Exception as e:
        print(f"Error {img_name}: {e}")

