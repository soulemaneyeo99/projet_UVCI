import re
import markdown
import subprocess

with open('/home/dev/.gemini/antigravity/brain/133f812f-0bd6-4230-b983-ae1a29ab8fcb/Rapport_Final_UVCI.md', 'r') as f:
    md_content = f.read()

# Helper to extract SVG from our HTML files
def get_svg(filename):
    with open(filename, 'r') as f:
        content = f.read()
    match = re.search(r'<svg.*?</svg>', content, re.DOTALL)
    if match:
        return f'<div class="svg-container">{match.group(0)}</div>'
    return f'<p>Error loading {filename}</p>'

# Replacements
md_content = md_content.replace("*(Insérer ici la capture d'écran du fichier `mcd_uvci.html`)*", get_svg('mcd_uvci.html'))
md_content = md_content.replace("*(Insérer ici la capture d'écran du fichier `mld_uvci.html`)*", get_svg('mld_uvci.html'))
md_content = md_content.replace("*(Insérer ici la 1ère capture d'écran du fichier `mot_flux_uvci.html`)*", get_svg('mot_flux_uvci.html').split('</svg>')[0] + '</svg>')
md_content = md_content.replace("*(Insérer ici la 2ème capture d'écran du fichier `mot_flux_uvci.html`)*", get_svg('mot_flux_uvci.html').split('</svg>')[1] + '</svg>' if len(get_svg('mot_flux_uvci.html').split('</svg>')) > 1 else '')
md_content = md_content.replace("*(Insérer ici la 3ème capture d'écran du fichier `mot_flux_uvci.html`)*", get_svg('mot_flux_uvci.html').split('</svg>')[2] + '</svg>' if len(get_svg('mot_flux_uvci.html').split('</svg>')) > 2 else '')

# Fix MCT
with open('mct_uvci.html', 'r') as f:
    mct_content = f.read()
mct_svgs = re.findall(r'<svg.*?</svg>', mct_content, re.DOTALL)
mct_combined = '<div class="svg-container">' + '<br>'.join(mct_svgs) + '</div>'
md_content = md_content.replace("*(Insérer ici la capture d'écran du fichier `mct_uvci.html`)*", mct_combined)

# Fix MPD
with open('mpd_uvci.html', 'r') as f:
    mpd_content = f.read()
mpd_match = re.search(r'<div class="wrap">(.*?)</div><!-- /wrap -->', mpd_content, re.DOTALL)
if mpd_match:
    md_content = md_content.replace("*(Insérer ici une capture du fichier `mpd_uvci.html` ou copier-coller un extrait du SQL)*", f'<div class="sql-code">{mpd_match.group(1)}</div>')

# Convert to HTML
html_body = markdown.markdown(md_content, extensions=['tables'])

html_template = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Rapport UVCI</title>
<style>
    body {{ font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 1.5; color: #000; max-width: 21cm; margin: 0 auto; }}
    h1 {{ font-size: 24pt; text-align: center; color: #2C3E50; margin-top: 50px; page-break-after: always; }}
    h2 {{ font-size: 18pt; color: #2980B9; border-bottom: 2px solid #2980B9; margin-top: 40px; page-break-before: always; }}
    h3 {{ font-size: 14pt; color: #E67E22; margin-top: 30px; }}
    h4 {{ font-size: 12pt; font-weight: bold; margin-top: 20px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 10pt; }}
    th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
    th {{ background-color: #ecf0f1; }}
    .svg-container {{ text-align: center; margin: 20px 0; page-break-inside: avoid; }}
    .svg-container svg {{ max-width: 100%; height: auto; }}
    .sql-code {{ font-family: monospace; font-size: 9pt; background: #f9f9f9; padding: 10px; border: 1px solid #ddd; }}
    pre {{ background: #f9f9f9; padding: 10px; border: 1px solid #ddd; font-size: 10pt; white-space: pre-wrap; }}
    .cover-page {{ display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; text-align: center; }}
    @page {{ size: A4; margin: 2cm; }}
</style>
</head>
<body>
    <div class="cover-page">
        <h1>RAPPORT DE PROJET<br><br>SYSTÈME DE GESTION DES HEURES PÉDAGOGIQUES DES ENSEIGNANTS DE L'UVCI</h1>
        <p style="margin-top:50px; font-size:14pt;">Université Virtuelle de Côte d'Ivoire</p>
    </div>
    {html_body.replace("<h1>RAPPORT DE PROJET : SYSTÈME DE GESTION DES HEURES PÉDAGOGIQUES DES ENSEIGNANTS DE L'UVCI</h1>", "")}
</body>
</html>
"""

with open('Rapport_Final_Complet.html', 'w') as f:
    f.write(html_template)

subprocess.run(['google-chrome', '--headless', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=Rapport_Final_Complet_UVCI.pdf', 'Rapport_Final_Complet.html'])
print("PDF Generated!")
