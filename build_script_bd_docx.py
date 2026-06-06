#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère Script_BD_UVCI.docx — même format académique que Guide_Utilisateur_UVCI.docx."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

LOGO_MIN  = '/tmp/docx_imgs/14518ad006362d68c9948ef2b155814428506f51.png'
LOGO_UVCI = '/tmp/docx_imgs/1a1e88b7b37ea3fb5b85c07c44d804697606eecd.png'
OUT       = '/Users/apple/projet/projet_UVCI/Script_BD_UVCI.docx'

FONT        = "Times New Roman"
NAVY        = RGBColor(0x1F, 0x4E, 0x79)
GREY_HEADER = "D9E2F3"
GREY_ROW    = "F2F5FA"
CONTENT_W   = 21 - 3 - 2.5   # 15.5 cm

doc = Document()

# ─── marges A4 ────────────────────────────────────────────────────────────────
sec = doc.sections[0]
sec.page_height     = Cm(29.7);  sec.page_width      = Cm(21.0)
sec.left_margin     = Cm(3.0);   sec.right_margin    = Cm(2.5)
sec.top_margin      = Cm(2.5);   sec.bottom_margin   = Cm(2.5)
sec.header_distance = Cm(1.5);   sec.footer_distance = Cm(1.5)

# ─── style Normal ─────────────────────────────────────────────────────────────
normal = doc.styles["Normal"]
normal.font.name = FONT
normal.font.size = Pt(12)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
pf = normal.paragraph_format
pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
pf.line_spacing      = 1.5
pf.space_after       = Pt(6)
pf.alignment         = WD_ALIGN_PARAGRAPH.JUSTIFY

# ─── styles Heading (même approche que build_guide_docx.py) ───────────────────
def style_heading(name, size, before, after, color=NAVY, page_break=False):
    s = doc.styles[name]
    s.font.name      = FONT
    s.font.size      = Pt(size)
    s.font.bold      = True
    s.font.color.rgb = color
    s.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    fp = s.paragraph_format
    fp.space_before      = Pt(before);  fp.space_after = Pt(after)
    fp.line_spacing_rule = WD_LINE_SPACING.SINGLE
    fp.keep_with_next    = True
    fp.alignment         = WD_ALIGN_PARAGRAPH.LEFT
    fp.page_break_before = page_break
    rpr    = s.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is not None:
        for a in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
            k = qn("w:" + a)
            if rfonts.get(k) is not None:
                del rfonts.attrib[k]
        rfonts.set(qn("w:cs"), FONT)
    return s

style_heading("Heading 1", 14, 18, 10, color=NAVY, page_break=True)
style_heading("Heading 2", 12, 12,  6, color=NAVY)
style_heading("Heading 3", 12,  8,  4, color=RGBColor(0x2E, 0x75, 0xB6))


# ─── helpers ──────────────────────────────────────────────────────────────────
def set_cell_bg(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)

def remove_borders(table):
    tbl   = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    tblBorders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "none")
        tblBorders.append(b)
    ex = tblPr.find(qn("w:tblBorders"))
    if ex is not None:
        tblPr.remove(ex)
    tblPr.append(tblBorders)

def set_col_width(table, col_idx, width_cm):
    for row in table.rows:
        row.cells[col_idx].width = Cm(width_cm)

def add_para(text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, bold=False, italic=False, size=12):
    p = doc.add_paragraph()
    p.alignment = align
    r = p.add_run(text)
    r.bold       = bold
    r.italic     = italic
    r.font.size  = Pt(size)
    return p

def add_caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing  = 1.0
    p.paragraph_format.space_before  = Pt(2)
    p.paragraph_format.space_after   = Pt(8)
    r = p.add_run(text)
    r.italic    = True
    r.font.size = Pt(10.5)
    return p

def add_sql_block(sql_text):
    """Bloc SQL monochrome (noir) Courier New 9pt dans un cadre gris clair."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    cell = table.cell(0, 0)
    set_cell_bg(cell, "F5F5F5")
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"),   "single")
        b.set(qn("w:sz"),    "4")
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), "BFBFBF")
        tcBorders.append(b)
    tcPr.append(tcBorders)
    # retirer paragraphe auto
    cell.paragraphs[0]._element.getparent().remove(cell.paragraphs[0]._element)
    for raw_line in sql_text.strip("\n").split("\n"):
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(0)
        p.paragraph_format.line_spacing = Pt(13)
        r = p.add_run(raw_line)
        r.font.name      = "Courier New"
        r.font.size      = Pt(9)
        r.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_col_table(rows_data, caption=None):
    """Tableau 4 colonnes : Colonne | Type SQL | Contraintes | Description."""
    tbl = doc.add_table(rows=1 + len(rows_data), cols=4)
    tbl.style     = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, w in enumerate([3.5, 3.0, 4.5, 5.5]):
        set_col_width(tbl, i, w)
    for i, h in enumerate(["Colonne", "Type SQL", "Contraintes", "Description"]):
        cell = tbl.cell(0, i)
        set_cell_bg(cell, GREY_HEADER)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing  = 1.0
        p.paragraph_format.space_after   = Pt(2)
        p.paragraph_format.space_before  = Pt(2)
        r = p.add_run(h)
        r.bold      = True
        r.font.size = Pt(10.5)
    for ri, (col, typ, cst, desc) in enumerate(rows_data):
        bg = GREY_ROW if ri % 2 else None
        for ci, val in enumerate([col, typ, cst, desc]):
            cell = tbl.cell(ri + 1, ci)
            if bg:
                set_cell_bg(cell, bg)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after  = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(10.5)
            r.bold      = (ci == 0)
    if caption:
        add_caption(caption)

def add_simple_table(headers, rows_data, col_widths, caption=None):
    """Tableau générique n colonnes."""
    tbl = doc.add_table(rows=1 + len(rows_data), cols=len(headers))
    tbl.style     = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, w in enumerate(col_widths):
        set_col_width(tbl, i, w)
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        set_cell_bg(cell, GREY_HEADER)
        p = cell.paragraphs[0]
        p.alignment                      = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing  = 1.0
        p.paragraph_format.space_after   = Pt(2)
        p.paragraph_format.space_before  = Pt(2)
        r = p.add_run(h)
        r.bold      = True
        r.font.size = Pt(10.5)
    for ri, row_vals in enumerate(rows_data):
        bg     = GREY_ROW if ri % 2 else None
        is_tot = (row_vals[0] == "TOTAL")
        if is_tot:
            bg = GREY_HEADER
        for ci, val in enumerate(row_vals):
            cell = tbl.cell(ri + 1, ci)
            if bg:
                set_cell_bg(cell, bg)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after  = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(10.5)
            r.bold      = (ci == 0 or is_tot)
            if ci > 0 and len(headers) > 2:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        add_caption(caption)

# ─── champ TOC réel (Word natif, mêmes helpers que build_guide_docx.py) ───────
def _fldchar(run, t):
    fc = OxmlElement("w:fldChar")
    fc.set(qn("w:fldCharType"), t)
    run._r.append(fc)

def _instr(run, text):
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = text
    run._r.append(it)

def _style_toc_par(p, lvl):
    pf = p.paragraph_format
    pf.line_spacing = 1.15
    pf.space_after  = Pt(2)
    pf.space_before = Pt(0)
    pf.left_indent  = Cm({1: 0.0, 2: 0.5}[min(lvl, 2)])
    pf.tab_stops.add_tab_stop(Cm(CONTENT_W), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

TOC_ENTRIES = [
    (1, "Introduction"),
    (1, "Conventions de nommage"),
    (1, "Section I. — Table USERS"),
    (2, "Script DDL"),
    (2, "Description des colonnes"),
    (1, "Section II. — Table TEACHERS"),
    (2, "Script DDL"),
    (2, "Description des colonnes"),
    (1, "Section III. — Table COURSES"),
    (2, "Script DDL"),
    (2, "Description des colonnes"),
    (1, "Section IV. — Table ACADEMIC_YEARS"),
    (2, "Script DDL"),
    (2, "Description des colonnes"),
    (1, "Section V. — Table RESOURCES"),
    (2, "Script DDL"),
    (2, "Description des colonnes"),
    (1, "Section VI. — Table ACTIVITIES"),
    (2, "Script DDL"),
    (2, "Description des colonnes"),
    (1, "Section VII. — Table COEFFICIENT_CONFIGS"),
    (2, "Script DDL"),
    (2, "Description des colonnes"),
    (1, "Section VIII. — Table QUOTAS_STATUTAIRES"),
    (2, "Script DDL"),
    (2, "Description des colonnes"),
    (1, "Section IX. — Données de référence (INSERT)"),
    (2, "Barème officiel des coefficients"),
    (2, "Quotas statutaires par défaut"),
    (1, "Annexe A. — Récapitulatif des tables"),
    (1, "Annexe B. — Matrice des contraintes"),
    (1, "Annexe C. — Schéma des relations"),
]

def add_toc():
    n = len(TOC_ENTRIES)
    for i, (lvl, text) in enumerate(TOC_ENTRIES):
        p = doc.add_paragraph()
        _style_toc_par(p, lvl)
        big = (lvl == 1)
        if i == 0:
            r0 = p.add_run()
            _fldchar(r0, "begin")
            _instr(r0, 'TOC \\o "1-2" \\h \\z \\u')
            _fldchar(r0, "separate")
        rt = p.add_run(text)
        rt.font.name = FONT
        rt.font.size = Pt(12 if big else 11)
        rt.bold      = big
        rp = p.add_run("\t")
        rp.font.name = FONT
        rp.font.size = Pt(12 if big else 11)
        if i == n - 1:
            rend = p.add_run()
            _fldchar(rend, "end")

def set_update_fields_on_open():
    settings = doc.settings.element
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    settings.append(el)


# ════════════════════════════════════════════════════════════════════════════
# PAGE DE GARDE  (même structure exacte que build_guide_docx.py)
# ════════════════════════════════════════════════════════════════════════════

# Logos côte à côte (table invisible)
lt = doc.add_table(rows=1, cols=2)
lt.autofit = True
remove_borders(lt)
lc, rc = lt.rows[0].cells
lp = lc.paragraphs[0]; lp.alignment = WD_ALIGN_PARAGRAPH.LEFT
lp.add_run().add_picture(LOGO_MIN, height=Cm(2.6))
rp = rc.paragraphs[0]; rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
rp.add_run().add_picture(LOGO_UVCI, height=Cm(2.8))

def cover_line(text, size, bold=False, italic=False, space=2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after  = Pt(space)
    p.paragraph_format.space_before = Pt(0)
    r = p.add_run(text)
    r.bold       = bold
    r.italic     = italic
    r.font.size  = Pt(size)
    r.font.name  = FONT
    return p

doc.add_paragraph().paragraph_format.space_after = Pt(6)
cover_line("RÉPUBLIQUE DE CÔTE D'IVOIRE", 12, bold=True)
cover_line("Union – Discipline – Travail", 11, italic=True)
cover_line("MINISTÈRE DE L'ENSEIGNEMENT SUPÉRIEUR ET DE LA RECHERCHE SCIENTIFIQUE", 11, bold=True)
cover_line("Université Virtuelle de Côte d'Ivoire (UVCI)", 11, bold=True)
cover_line("UFR : Informatique et Sciences du Numérique", 11)
cover_line("Licence 3 – Option : Développement d'Applications et e-Services (DAS)", 11, space=10)

cover_line("PROJET COLLECTIF TUTORÉ", 13, bold=True)
cover_line("En vue de l'obtention du diplôme de Licence en Informatique et Sciences du Numérique",
           11, italic=True, space=12)

# Encadré titre (table 1×1 bordurée, exactement comme le guide)
bt = doc.add_table(rows=1, cols=1)
bt.alignment = WD_TABLE_ALIGNMENT.CENTER
bt.style = "Table Grid"
bc = bt.rows[0].cells[0]
bc.width = Cm(CONTENT_W)
p1 = bc.paragraphs[0]
p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
p1.paragraph_format.space_after   = Pt(4)
p1.paragraph_format.line_spacing  = 1.0
r = p1.add_run("LIVRABLE")
r.italic    = True
r.font.size = Pt(11)
p2 = bc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p2.paragraph_format.line_spacing = 1.3
p2.paragraph_format.space_after  = Pt(2)
for i, line in enumerate([
    "SCRIPT DE CRÉATION DE LA BASE DE DONNÉES",
    "SYSTÈME DE GESTION DES HEURES PÉDAGOGIQUES",
    "DES ENSEIGNANTS DE L'UVCI",
]):
    if i:
        p2.add_run().add_break()
    rr = p2.add_run(line)
    rr.bold      = True
    rr.font.size = Pt(14)
    rr.font.name = FONT

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# Tableau fiche technique
info_tbl = doc.add_table(rows=1, cols=2)
info_tbl.style     = "Table Grid"
info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(["Référence technique", "Valeur"]):
    cell = info_tbl.cell(0, i)
    set_cell_bg(cell, GREY_HEADER)
    p = cell.paragraphs[0]
    p.alignment                    = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(h)
    r.bold      = True
    r.font.size = Pt(11)
for lbl, val in [
    ("SGBD cible",        "PostgreSQL 14+"),
    ("Encodage",          "UTF-8"),
    ("Version",           "1.0"),
    ("Référence",         "PCT25-26_DAS-N°11"),
    ("Année académique",  "2025 – 2026"),
]:
    row = info_tbl.add_row()
    for ci, txt in enumerate([lbl, val]):
        cell = row.cells[ci]
        p = cell.paragraphs[0]
        p.paragraph_format.space_after  = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(txt)
        r.font.size = Pt(11)
        r.bold      = (ci == 0)
set_col_width(info_tbl, 0, 5.5)
set_col_width(info_tbl, 1, 9.5)

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# Tableau auteurs / encadreur (identique au guide)
at = doc.add_table(rows=2, cols=2)
at.style     = "Table Grid"
at.alignment = WD_TABLE_ALIGNMENT.CENTER
h1, h2 = at.rows[0].cells
for c, txt in ((h1, "PRÉSENTÉ PAR :"), (h2, "TUTEUR D'ENCADREMENT :")):
    set_cell_bg(c, GREY_HEADER)
    pp = c.paragraphs[0]
    pp.alignment                    = WD_ALIGN_PARAGRAPH.CENTER
    pp.paragraph_format.line_spacing = 1.0
    rr = pp.add_run(txt)
    rr.bold      = True
    rr.font.size = Pt(11)
c1, c2 = at.rows[1].cells
authors = [
    "YEO YANOUGUI SOULEYMANE",
    "TUO CHIGATA JEAN MARC",
    "SOUMAHORO SOUALIO",
    "SEDJI YEDO LINDA COLOMBE TIPHAINE",
    "ASSALÉ CHIMÈNE-FLORE",
]
pa = c1.paragraphs[0]
pa.paragraph_format.line_spacing = 1.3
pa.alignment = WD_ALIGN_PARAGRAPH.LEFT
for i, a in enumerate(authors):
    if i:
        pa.add_run().add_break()
    pa.add_run(a).font.size = Pt(11)
pt2 = c2.paragraphs[0]
pt2.paragraph_format.line_spacing = 1.3
pt2.alignment = WD_ALIGN_PARAGRAPH.LEFT
rr = pt2.add_run("M. SANGARÉ SEYDOU")
rr.bold      = True
rr.font.size = Pt(11)
pt2.add_run().add_break()
pt2.add_run("Docteur en Informatique").font.size = Pt(11)

doc.add_paragraph().paragraph_format.space_after = Pt(10)
fp1 = doc.add_paragraph()
fp1.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp1.add_run("Groupe : PCT25-26_DAS-N°11")
r.bold      = True
r.font.size = Pt(11)
fp2 = doc.add_paragraph()
fp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp2.add_run("Année académique : 2025 – 2026")
r.bold      = True
r.font.size = Pt(11)

# ─── en-tête et pied de page (pas sur la couverture) ─────────────────────────
sec.different_first_page_header_footer = True

footer = sec.footer
fpp = footer.paragraphs[0]
fpp.alignment                    = WD_ALIGN_PARAGRAPH.CENTER
fpp.paragraph_format.line_spacing = 1.0
run = fpp.add_run()
run.font.size = Pt(10)
run.font.name = FONT
fb = OxmlElement("w:fldChar"); fb.set(qn("w:fldCharType"), "begin")
it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = "PAGE"
fe = OxmlElement("w:fldChar"); fe.set(qn("w:fldCharType"), "end")
run._r.append(fb); run._r.append(it); run._r.append(fe)

header = sec.header
hp = header.paragraphs[0]
hp.alignment                    = WD_ALIGN_PARAGRAPH.CENTER
hp.paragraph_format.line_spacing = 1.0
hr_run = hp.add_run("Script BD – Gestion des Heures Pédagogiques UVCI")
hr_run.font.size = Pt(9)
hr_run.italic    = True
hr_run.font.name = FONT
hpr = hp._p.get_or_add_pPr()
bd  = OxmlElement("w:pBdr")
b   = OxmlElement("w:bottom")
b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "4")
b.set(qn("w:space"), "4");    b.set(qn("w:color"), "999999")
bd.append(b); hpr.append(bd)


# ════════════════════════════════════════════════════════════════════════════
# SOMMAIRE
# ════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after   = Pt(16)
p.paragraph_format.line_spacing  = 1.0
p.paragraph_format.page_break_before = False
r = p.add_run("SOMMAIRE")
r.bold      = True
r.font.size = Pt(14)
r.font.name = FONT
add_toc()


# ════════════════════════════════════════════════════════════════════════════
# INTRODUCTION
# ════════════════════════════════════════════════════════════════════════════
doc.add_heading("Introduction", level=1)
add_para(
    "Le présent document constitue le script complet de définition du schéma relationnel "
    "(DDL — Data Definition Language) de la base de données du Système de Gestion des Heures "
    "Pédagogiques des Enseignants de l'Université Virtuelle de Côte d'Ivoire (UVCI). "
    "Ce script est destiné à être exécuté sur un serveur PostgreSQL 14 ou supérieur."
)
add_para(
    "Il contient : (1) la suppression conditionnelle des tables existantes "
    "(DROP … IF EXISTS CASCADE), garantissant l'idempotence du script ; "
    "(2) la création des huit tables du modèle relationnel avec leurs contraintes "
    "d'intégrité, clés primaires, clés étrangères et index ; "
    "(3) l'insertion des données de référence (barème officiel UVCI et quotas statutaires par défaut)."
)
add_para(
    "Le script est encadré dans une transaction explicite (BEGIN … COMMIT) : "
    "en cas d'erreur, la totalité du script est annulée, préservant la cohérence de la base."
)
add_para("Commande d'exécution :")
add_sql_block("    psql -U <utilisateur> -d <base_de_données> -f schema_uvci.sql")


# ════════════════════════════════════════════════════════════════════════════
# CONVENTIONS DE NOMMAGE
# ════════════════════════════════════════════════════════════════════════════
doc.add_heading("Conventions de nommage", level=1)
add_simple_table(
    headers    = ["Élément", "Motif de nommage", "Exemples"],
    col_widths = [3.5, 4.0, 8.5],
    rows_data  = [
        ("Tables",             "pluriel, snake_case",       "users, activities, academic_years"),
        ("Clés primaires",     "pk_<table>",                "pk_users, pk_teachers"),
        ("Clés étrangères",    "fk_<table>_<colonne>",      "fk_teachers_user, fk_activities_resource"),
        ("Contraintes UNIQUE", "uq_<table>_<colonnes>",     "uq_users_email, uq_coeff_niveau_type"),
        ("Contraintes CHECK",  "ck_<table>_<colonne>",      "ck_users_role, ck_teachers_statut"),
        ("Index",              "ix_<table>_<colonne>",      "ix_users_email, ix_activities_status"),
    ],
    caption = "Tableau 1. Conventions de nommage appliquées au schéma UVCI.",
)


# ════════════════════════════════════════════════════════════════════════════
# SECTIONS I–VIII : chaque table
# ════════════════════════════════════════════════════════════════════════════

SECTIONS = [

  # ── SECTION I : USERS ────────────────────────────────────────────────────
  dict(
    heading="Section I. — Table USERS",
    description=(
        "La table USERS centralise les comptes d'authentification de l'application. "
        "Chaque utilisateur se voit attribuer un rôle RBAC (admin, secretary, teacher) "
        "qui détermine ses droits d'accès à l'API. "
        "Le mot de passe est systématiquement haché avec l'algorithme bcrypt avant stockage : "
        "la valeur en clair n'est jamais persistée en base."
    ),
    sql="""\
BEGIN;
SET client_encoding = 'UTF8';

-- ===================================================================
-- 1. UTILISATEURS (comptes d'authentification)
-- ===================================================================
CREATE TABLE users (
    id              INTEGER       GENERATED ALWAYS AS IDENTITY,
    email           VARCHAR(255)  NOT NULL,
    hashed_password VARCHAR(255)  NOT NULL,
    role            VARCHAR(20)   NOT NULL DEFAULT 'teacher',
    est_actif       BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT pk_users       PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_role  CHECK (role IN ('admin', 'secretary', 'teacher'))
);

CREATE INDEX ix_users_email ON users (email);

COMMENT ON TABLE  users                 IS 'Comptes authentification (admin, secrétaire, enseignant).';
COMMENT ON COLUMN users.hashed_password IS 'Haché bcrypt — jamais en clair.';
COMMENT ON COLUMN users.role            IS 'RBAC : admin | secretary | teacher.';
COMMENT ON COLUMN users.est_actif       IS 'FALSE = compte désactivé sans suppression.';\
""",
    cols=[
        ("id",              "INTEGER",      "PK, GENERATED ALWAYS AS IDENTITY",  "Identifiant auto-incrémenté"),
        ("email",           "VARCHAR(255)", "NOT NULL, UNIQUE",                   "Adresse courriel — identifiant de connexion"),
        ("hashed_password", "VARCHAR(255)", "NOT NULL",                           "Mot de passe haché bcrypt"),
        ("role",            "VARCHAR(20)",  "NOT NULL, DEFAULT 'teacher', CHECK", "Rôle RBAC : admin | secretary | teacher"),
        ("est_actif",       "BOOLEAN",      "NOT NULL, DEFAULT TRUE",             "Compte actif (TRUE) ou désactivé (FALSE)"),
        ("created_at",      "TIMESTAMPTZ",  "NOT NULL, DEFAULT now()",            "Horodatage de création du compte"),
    ],
    caption   = "Tableau 2. Colonnes de la table USERS.",
    note      = "Index sur email — recherche O(log n) à l'authentification.",
  ),

  # ── SECTION II : TEACHERS ────────────────────────────────────────────────
  dict(
    heading="Section II. — Table TEACHERS",
    description=(
        "La table TEACHERS stocke le profil métier de chaque enseignant. "
        "Elle est liée à la table USERS par une relation 1:1 optionnelle (user_id nullable) : "
        "un enseignant peut être enregistré dans le système sans disposer encore d'un compte "
        "d'authentification. Le statut (Permanent ou Vacataire) conditionne le quota horaire "
        "annuel applicable, défini dans la table QUOTAS_STATUTAIRES."
    ),
    sql="""\
-- ===================================================================
-- 2. ENSEIGNANTS (profil métier)
-- ===================================================================
CREATE TABLE teachers (
    id           INTEGER       GENERATED ALWAYS AS IDENTITY,
    nom          VARCHAR(100)  NOT NULL,
    prenom       VARCHAR(100)  NOT NULL,
    grade        VARCHAR(100)  NOT NULL,
    statut       VARCHAR(20)   NOT NULL,
    departement  VARCHAR(150)  NOT NULL,
    taux_horaire NUMERIC(8,2)  NOT NULL DEFAULT 0.00,
    email        VARCHAR(255)  NOT NULL,
    telephone    VARCHAR(30),
    user_id      INTEGER,

    CONSTRAINT pk_teachers              PRIMARY KEY (id),
    CONSTRAINT uq_teachers_email        UNIQUE (email),
    CONSTRAINT uq_teachers_user         UNIQUE (user_id),
    CONSTRAINT ck_teachers_statut       CHECK (statut IN ('Permanent', 'Vacataire')),
    CONSTRAINT ck_teachers_taux_horaire CHECK (taux_horaire >= 0),
    CONSTRAINT fk_teachers_user         FOREIGN KEY (user_id)
        REFERENCES users (id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX ix_teachers_user_id     ON teachers (user_id);
CREATE INDEX ix_teachers_departement ON teachers (departement);\
""",
    cols=[
        ("id",           "INTEGER",      "PK, GENERATED ALWAYS AS IDENTITY", "Identifiant auto-incrémenté"),
        ("nom",          "VARCHAR(100)", "NOT NULL",                          "Nom de famille"),
        ("prenom",       "VARCHAR(100)", "NOT NULL",                          "Prénom"),
        ("grade",        "VARCHAR(100)", "NOT NULL",                          "Grade académique (Professeur, Maître-Assistant…)"),
        ("statut",       "VARCHAR(20)",  "NOT NULL, CHECK",                   "Permanent ou Vacataire"),
        ("departement",  "VARCHAR(150)", "NOT NULL",                          "Département d'appartenance"),
        ("taux_horaire", "NUMERIC(8,2)", "NOT NULL, DEFAULT 0, CHECK ≥ 0",   "Rémunération en FCFA par heure"),
        ("email",        "VARCHAR(255)", "NOT NULL, UNIQUE",                  "Adresse courriel professionnelle"),
        ("telephone",    "VARCHAR(30)",  "NULL autorisé",                     "Numéro de téléphone (optionnel)"),
        ("user_id",      "INTEGER",      "FK → users.id, UNIQUE, NULL OK",   "Lien vers le compte utilisateur (1:1)"),
    ],
    caption = "Tableau 3. Colonnes de la table TEACHERS.",
    note    = "Index sur user_id (jointure fréquente) et departement (filtres statistiques).",
  ),

  # ── SECTION III : COURSES ─────────────────────────────────────────────────
  dict(
    heading="Section III. — Table COURSES",
    description=(
        "La table COURSES constitue le catalogue des unités d'enseignement (UE) pour lesquelles "
        "des ressources pédagogiques numériques sont produites. Elle sert de référentiel partagé "
        "entre la secrétaire (saisie des activités) et l'administration. "
        "Le niveau est contraint aux cinq paliers du système LMD ivoirien."
    ),
    sql="""\
-- ===================================================================
-- 3. COURS (catalogue pédagogique)
-- ===================================================================
CREATE TABLE courses (
    id         INTEGER       GENERATED ALWAYS AS IDENTITY,
    intitule   VARCHAR(255)  NOT NULL,
    filiere    VARCHAR(150)  NOT NULL,
    niveau     VARCHAR(10)   NOT NULL,
    semestre   VARCHAR(20)   NOT NULL,
    nb_heures  INTEGER,
    nb_credits INTEGER,

    CONSTRAINT pk_courses           PRIMARY KEY (id),
    CONSTRAINT ck_courses_niveau    CHECK (niveau IN ('L1','L2','L3','M1','M2')),
    CONSTRAINT ck_courses_nb_heures CHECK (nb_heures  IS NULL OR nb_heures  >= 0),
    CONSTRAINT ck_courses_credits   CHECK (nb_credits IS NULL OR nb_credits >= 0)
);

CREATE INDEX ix_courses_filiere ON courses (filiere);
CREATE INDEX ix_courses_niveau  ON courses (niveau);\
""",
    cols=[
        ("id",         "INTEGER",      "PK, GENERATED ALWAYS AS IDENTITY", "Identifiant auto-incrémenté"),
        ("intitule",   "VARCHAR(255)", "NOT NULL",                          "Intitulé complet du cours"),
        ("filiere",    "VARCHAR(150)", "NOT NULL",                          "Filière ou spécialité"),
        ("niveau",     "VARCHAR(10)",  "NOT NULL, CHECK",                   "Niveau LMD : L1, L2, L3, M1 ou M2"),
        ("semestre",   "VARCHAR(20)",  "NOT NULL",                          "Semestre (S1, S2, S3…)"),
        ("nb_heures",  "INTEGER",      "NULL OK, CHECK ≥ 0",               "Volume horaire présentiel (optionnel)"),
        ("nb_credits", "INTEGER",      "NULL OK, CHECK ≥ 0",               "Nombre de crédits ECTS (optionnel)"),
    ],
    caption = "Tableau 4. Colonnes de la table COURSES.",
    note    = "Index sur filière et niveau — colonnes de filtrage des listes déroulantes.",
  ),

  # ── SECTION IV : ACADEMIC_YEARS ───────────────────────────────────────────
  dict(
    heading="Section IV. — Table ACADEMIC_YEARS",
    description=(
        "La table ACADEMIC_YEARS permet de rattacher chaque activité à une année académique précise, "
        "facilitant les calculs de volumes horaires annuels et les comparaisons inter-années. "
        "Un index partiel unique garantit qu'une seule année peut être marquée comme active "
        "(status = TRUE) à un instant donné, sans nécessiter de trigger ni de logique applicative."
    ),
    sql="""\
-- ===================================================================
-- 4. ANNÉES ACADÉMIQUES
-- ===================================================================
CREATE TABLE academic_years (
    id         INTEGER      GENERATED ALWAYS AS IDENTITY,
    libelle    VARCHAR(20)  NOT NULL,
    date_debut DATE,
    date_fin   DATE,
    status     BOOLEAN      NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_academic_years       PRIMARY KEY (id),
    CONSTRAINT uq_academic_years_lib   UNIQUE (libelle),
    CONSTRAINT ck_academic_years_dates CHECK (
        date_debut IS NULL OR date_fin IS NULL OR date_fin >= date_debut
    )
);

-- Une seule année active à la fois (index partiel unique)
CREATE UNIQUE INDEX uq_academic_years_active
    ON academic_years (status) WHERE status = TRUE;\
""",
    cols=[
        ("id",         "INTEGER",     "PK, GENERATED ALWAYS AS IDENTITY", "Identifiant auto-incrémenté"),
        ("libelle",    "VARCHAR(20)", "NOT NULL, UNIQUE",                  "Libellé, ex. « 2025-2026 »"),
        ("date_debut", "DATE",        "NULL OK",                           "Date de début de l'année"),
        ("date_fin",   "DATE",        "NULL OK, CHECK ≥ date_debut",      "Date de fin de l'année"),
        ("status",     "BOOLEAN",     "NOT NULL, DEFAULT FALSE",           "TRUE = année courante active (une seule à la fois)"),
    ],
    caption = "Tableau 5. Colonnes de la table ACADEMIC_YEARS.",
    note    = "Index partiel unique sur status WHERE status = TRUE — unicité de l'année active sans colonne redondante.",
  ),

  # ── SECTION V : RESOURCES ─────────────────────────────────────────────────
  dict(
    heading="Section V. — Table RESOURCES",
    description=(
        "La table RESOURCES représente la combinaison unique "
        "(enseignant × cours × type d'activité × niveau de complexité). "
        "Elle constitue la couche de référentiel entre les entités métier et les activités déclarées. "
        "La contrainte d'unicité composite sur (teacher_id, course_id, type, niveau_complexite) "
        "empêche la création de doublons de ressources pour un même enseignant."
    ),
    sql="""\
-- ===================================================================
-- 5. RESSOURCES PÉDAGOGIQUES
-- ===================================================================
CREATE TABLE resources (
    id                INTEGER      GENERATED ALWAYS AS IDENTITY,
    type              VARCHAR(30)  NOT NULL,
    niveau_complexite SMALLINT     NOT NULL DEFAULT 1,
    course_id         INTEGER      NOT NULL,
    teacher_id        INTEGER      NOT NULL,
    date_creation     TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT pk_resources          PRIMARY KEY (id),
    CONSTRAINT uq_resources_business UNIQUE (teacher_id, course_id, type, niveau_complexite),
    CONSTRAINT ck_resources_type     CHECK (type IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_resources_niveau   CHECK (niveau_complexite IN (1, 2, 3)),
    CONSTRAINT fk_resources_course   FOREIGN KEY (course_id)
        REFERENCES courses  (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_resources_teacher  FOREIGN KEY (teacher_id)
        REFERENCES teachers (id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX ix_resources_course_id  ON resources (course_id);
CREATE INDEX ix_resources_teacher_id ON resources (teacher_id);\
""",
    cols=[
        ("id",                "INTEGER",     "PK, GENERATED ALWAYS AS IDENTITY",  "Identifiant auto-incrémenté"),
        ("type",              "VARCHAR(30)", "NOT NULL, CHECK",                    "creation ou mise_a_jour"),
        ("niveau_complexite", "SMALLINT",    "NOT NULL, DEFAULT 1, CHECK 1–3",    "Niveau 1, 2 ou 3 (détermine le coefficient)"),
        ("course_id",         "INTEGER",     "NOT NULL, FK → courses.id",         "Cours concerné par la ressource"),
        ("teacher_id",        "INTEGER",     "NOT NULL, FK → teachers.id",        "Enseignant auteur de la ressource"),
        ("date_creation",     "TIMESTAMPTZ", "NOT NULL, DEFAULT now()",            "Horodatage de création"),
    ],
    caption = "Tableau 6. Colonnes de la table RESOURCES.",
    note    = "Contrainte UNIQUE composite (teacher_id, course_id, type, niveau) garantit l'unicité métier.",
  ),

  # ── SECTION VI : ACTIVITIES ───────────────────────────────────────────────
  dict(
    heading="Section VI. — Table ACTIVITIES",
    description=(
        "La table ACTIVITIES enregistre chaque acte de production pédagogique générateur "
        "d'un volume horaire calculé (Vhtc). La formule officielle UVCI est : Vhtc = Ic × S, "
        "où Ic est le coefficient de complexité (issu de COEFFICIENT_CONFIGS) "
        "et S le nombre de séquences produites. "
        "Les activités suivent un cycle de validation à trois états : "
        "en_attente → valide | rejetee, avec traçabilité du validateur."
    ),
    sql="""\
-- ===================================================================
-- 6. ACTIVITÉS (volume horaire généré)
-- ===================================================================
CREATE TABLE activities (
    id                     INTEGER       GENERATED ALWAYS AS IDENTITY,
    type                   VARCHAR(20)   NOT NULL,
    resource_id            INTEGER       NOT NULL,
    teacher_id             INTEGER       NOT NULL,
    nb_sequences           INTEGER       NOT NULL DEFAULT 1,
    volume_horaire_calcule NUMERIC(8,3)  NOT NULL DEFAULT 0.000,
    academic_year_id       INTEGER,
    annee_academique       VARCHAR(20),
    validation_status      VARCHAR(20)   NOT NULL DEFAULT 'en_attente',
    validated_by           INTEGER,
    validated_at           TIMESTAMPTZ,
    created_at             TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT pk_activities           PRIMARY KEY (id),
    CONSTRAINT ck_activities_type      CHECK (type IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_activities_status    CHECK (validation_status IN
                                        ('en_attente', 'valide', 'rejetee')),
    CONSTRAINT ck_activities_sequences CHECK (nb_sequences > 0),
    CONSTRAINT ck_activities_volume    CHECK (volume_horaire_calcule >= 0),
    CONSTRAINT fk_activities_resource  FOREIGN KEY (resource_id)
        REFERENCES resources     (id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_activities_teacher   FOREIGN KEY (teacher_id)
        REFERENCES teachers      (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_activities_year      FOREIGN KEY (academic_year_id)
        REFERENCES academic_years(id) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_activities_validator FOREIGN KEY (validated_by)
        REFERENCES users         (id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX ix_activities_resource_id ON activities (resource_id);
CREATE INDEX ix_activities_teacher_id  ON activities (teacher_id);
CREATE INDEX ix_activities_year_id     ON activities (academic_year_id);
CREATE INDEX ix_activities_status      ON activities (validation_status);\
""",
    cols=[
        ("id",                     "INTEGER",      "PK, GENERATED ALWAYS AS IDENTITY",     "Identifiant auto-incrémenté"),
        ("type",                   "VARCHAR(20)",  "NOT NULL, CHECK",                        "creation (Ic plein) ou mise_a_jour (½ Ic)"),
        ("resource_id",            "INTEGER",      "NOT NULL, FK → resources.id, CASCADE",  "Ressource concernée (suppression en cascade)"),
        ("teacher_id",             "INTEGER",      "NOT NULL, FK → teachers.id, RESTRICT",  "Enseignant déclarant l'activité"),
        ("nb_sequences",           "INTEGER",      "NOT NULL, DEFAULT 1, CHECK > 0",         "Nombre de séquences S produites"),
        ("volume_horaire_calcule", "NUMERIC(8,3)", "NOT NULL, DEFAULT 0, CHECK ≥ 0",        "Vhtc = Ic × S (3 décimales)"),
        ("academic_year_id",       "INTEGER",      "NULL OK, FK → academic_years.id",       "Année académique (NULL si non renseignée)"),
        ("annee_academique",       "VARCHAR(20)",  "NULL OK",                                "Libellé textuel complémentaire (dénormalisation légère)"),
        ("validation_status",      "VARCHAR(20)",  "NOT NULL, DEFAULT en_attente, CHECK",   "État : en_attente | valide | rejetee"),
        ("validated_by",           "INTEGER",      "NULL OK, FK → users.id",                "Compte admin/secrétaire ayant validé"),
        ("validated_at",           "TIMESTAMPTZ",  "NULL OK",                                "Horodatage de la validation"),
        ("created_at",             "TIMESTAMPTZ",  "NOT NULL, DEFAULT now()",                "Horodatage de création"),
    ],
    caption = "Tableau 7. Colonnes de la table ACTIVITIES.",
    note    = "4 index : resource_id, teacher_id, academic_year_id, validation_status — colonnes de filtrage fréquent.",
  ),

  # ── SECTION VII : COEFFICIENT_CONFIGS ────────────────────────────────────
  dict(
    heading="Section VII. — Table COEFFICIENT_CONFIGS",
    description=(
        "La table COEFFICIENT_CONFIGS stocke le barème officiel UVCI des coefficients horaires (Ic) "
        "utilisés dans la formule Vhtc = Ic × S. "
        "L'administrateur peut modifier ces valeurs via l'API (PUT /config/coefficients) "
        "sans redéploiement. Les six lignes initiales correspondent au barème officiel, "
        "avec le principe que le coefficient de mise à jour vaut la moitié de celui de création."
    ),
    sql="""\
-- ===================================================================
-- 7. CONFIGURATION DES COEFFICIENTS (barème UVCI)
-- ===================================================================
CREATE TABLE coefficient_configs (
    id                INTEGER       GENERATED ALWAYS AS IDENTITY,
    niveau_complexite SMALLINT      NOT NULL,
    type_activite     VARCHAR(20)   NOT NULL,
    coefficient       NUMERIC(6,3)  NOT NULL,

    CONSTRAINT pk_coefficient_configs PRIMARY KEY (id),
    CONSTRAINT uq_coeff_niveau_type   UNIQUE (niveau_complexite, type_activite),
    CONSTRAINT ck_coeff_niveau        CHECK (niveau_complexite IN (1, 2, 3)),
    CONSTRAINT ck_coeff_type          CHECK (type_activite IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_coeff_value         CHECK (coefficient >= 0)
);\
""",
    cols=[
        ("id",                "INTEGER",      "PK, GENERATED ALWAYS AS IDENTITY",      "Identifiant auto-incrémenté"),
        ("niveau_complexite", "SMALLINT",     "NOT NULL, UNIQUE composite, CHECK 1–3", "Niveau de complexité du contenu (1, 2 ou 3)"),
        ("type_activite",     "VARCHAR(20)",  "NOT NULL, UNIQUE composite, CHECK",     "creation ou mise_a_jour"),
        ("coefficient",       "NUMERIC(6,3)", "NOT NULL, CHECK ≥ 0",                  "Valeur du coefficient Ic (3 décimales)"),
    ],
    caption = "Tableau 8. Colonnes de la table COEFFICIENT_CONFIGS.",
    note    = "Contrainte UNIQUE (niveau_complexite, type_activite) — une seule ligne par combinaison niveau × type.",
  ),

  # ── SECTION VIII : QUOTAS_STATUTAIRES ────────────────────────────────────
  dict(
    heading="Section VIII. — Table QUOTAS_STATUTAIRES",
    description=(
        "La table QUOTAS_STATUTAIRES définit le volume horaire annuel dû "
        "pour chaque combinaison (grade × statut). "
        "Ces valeurs permettent de calculer la proportion du quota atteint par chaque enseignant "
        "(tableau de bord). L'administrateur peut les ajuster sans redéploiement via l'API "
        "(PUT /config/quotas). Par défaut : 192 h pour les permanents, 96 h pour les vacataires."
    ),
    sql="""\
-- ===================================================================
-- 8. QUOTAS STATUTAIRES
-- ===================================================================
CREATE TABLE quotas_statutaires (
    id           INTEGER       GENERATED ALWAYS AS IDENTITY,
    grade        VARCHAR(100)  NOT NULL,
    statut       VARCHAR(20)   NOT NULL,
    quota_heures NUMERIC(8,2)  NOT NULL,

    CONSTRAINT pk_quotas_statutaires PRIMARY KEY (id),
    CONSTRAINT uq_quota_grade_statut UNIQUE (grade, statut),
    CONSTRAINT ck_quota_statut       CHECK (statut IN ('Permanent', 'Vacataire')),
    CONSTRAINT ck_quota_value        CHECK (quota_heures >= 0)
);

COMMIT;\
""",
    cols=[
        ("id",           "INTEGER",      "PK, GENERATED ALWAYS AS IDENTITY",  "Identifiant auto-incrémenté"),
        ("grade",        "VARCHAR(100)", "NOT NULL, UNIQUE composite",         "Grade académique de l'enseignant"),
        ("statut",       "VARCHAR(20)",  "NOT NULL, UNIQUE composite, CHECK",  "Permanent ou Vacataire"),
        ("quota_heures", "NUMERIC(8,2)", "NOT NULL, CHECK ≥ 0",               "Quota horaire annuel en heures"),
    ],
    caption = "Tableau 9. Colonnes de la table QUOTAS_STATUTAIRES.",
    note    = "Contrainte UNIQUE (grade, statut) — une seule ligne par combinaison grade × statut.",
  ),
]

for s in SECTIONS:
    doc.add_heading(s["heading"], level=1)
    add_para(s["description"])
    doc.add_heading("Script DDL", level=2)
    add_sql_block(s["sql"])
    doc.add_heading("Description des colonnes", level=2)
    add_col_table(s["cols"], caption=s["caption"])
    add_para(f'Note : {s["note"]}', italic=True, size=10)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


# ════════════════════════════════════════════════════════════════════════════
# SECTION IX : DONNÉES DE RÉFÉRENCE (INSERT)
# ════════════════════════════════════════════════════════════════════════════
doc.add_heading("Section IX. — Données de référence (INSERT)", level=1)
add_para(
    "Cette section regroupe les données initiales insérées au moment de la création du schéma. "
    "Elles correspondent au barème officiel UVCI des coefficients horaires (six lignes) "
    "et aux quotas statutaires par défaut (huit lignes, pour quatre grades × deux statuts). "
    "Ces valeurs peuvent être modifiées ultérieurement par l'administrateur via l'interface."
)

doc.add_heading("Barème officiel des coefficients", level=2)
add_sql_block("""\
-- Barème officiel UVCI : Vhtc = Ic x S ; mise à jour = ½ x création.
INSERT INTO coefficient_configs (niveau_complexite, type_activite, coefficient) VALUES
    (1, 'creation',    0.400),
    (1, 'mise_a_jour', 0.200),
    (2, 'creation',    0.750),
    (2, 'mise_a_jour', 0.375),
    (3, 'creation',    1.500),
    (3, 'mise_a_jour', 0.750);\
""")
add_simple_table(
    headers    = ["Niveau", "Type d'activité", "Coefficient Ic", "Description"],
    col_widths = [3.0, 3.5, 3.5, 6.5],
    rows_data  = [
        ("Niveau 1", "creation",    "0.400", "Contenus simples + quiz"),
        ("Niveau 1", "mise_a_jour", "0.200", "½ × création"),
        ("Niveau 2", "creation",    "0.750", "+25 % activités interactives"),
        ("Niveau 2", "mise_a_jour", "0.375", "½ × création"),
        ("Niveau 3", "creation",    "1.500", "Serious games, simulations"),
        ("Niveau 3", "mise_a_jour", "0.750", "½ × création"),
    ],
    caption = "Tableau 10. Barème officiel UVCI des coefficients horaires.",
)

doc.add_heading("Quotas statutaires par défaut", level=2)
add_sql_block("""\
-- Quotas par défaut : 192 h (permanents), 96 h (vacataires).
INSERT INTO quotas_statutaires (grade, statut, quota_heures) VALUES
    ('Professeur',            'Permanent', 192.00),
    ('Maitre de Conferences', 'Permanent', 192.00),
    ('Maitre-Assistant',      'Permanent', 192.00),
    ('Assistant',             'Permanent', 192.00),
    ('Professeur',            'Vacataire',  96.00),
    ('Maitre de Conferences', 'Vacataire',  96.00),
    ('Maitre-Assistant',      'Vacataire',  96.00),
    ('Assistant',             'Vacataire',  96.00);\
""")
add_simple_table(
    headers    = ["Grade", "Statut", "Quota (heures/an)"],
    col_widths = [6.5, 4.0, 4.0],
    rows_data  = [
        ("Professeur",            "Permanent", "192.00"),
        ("Maître de Conférences", "Permanent", "192.00"),
        ("Maître-Assistant",      "Permanent", "192.00"),
        ("Assistant",             "Permanent", "192.00"),
        ("Professeur",            "Vacataire",  "96.00"),
        ("Maître de Conférences", "Vacataire",  "96.00"),
        ("Maître-Assistant",      "Vacataire",  "96.00"),
        ("Assistant",             "Vacataire",  "96.00"),
    ],
    caption = "Tableau 11. Quotas statutaires par défaut (modifiables via l'interface admin).",
)


# ════════════════════════════════════════════════════════════════════════════
# ANNEXE A : RÉCAPITULATIF DES TABLES
# ════════════════════════════════════════════════════════════════════════════
doc.add_heading("Annexe A. — Récapitulatif des tables", level=1)
add_simple_table(
    headers    = ["Table", "Colonnes", "Rôle"],
    col_widths = [4.5, 2.5, 9.5],
    rows_data  = [
        ("users",               "6",  "Comptes d'authentification (admin / secretary / teacher)"),
        ("teachers",            "10", "Profils métier des enseignants"),
        ("courses",             "7",  "Catalogue des unités d'enseignement"),
        ("academic_years",      "5",  "Années académiques de rattachement"),
        ("resources",           "6",  "Combinaisons enseignant × cours × type × niveau"),
        ("activities",          "12", "Activités déclarées et volumes horaires calculés"),
        ("coefficient_configs", "4",  "Barème officiel des coefficients Ic (paramétrable)"),
        ("quotas_statutaires",  "4",  "Quotas horaires annuels par grade et statut (paramétrable)"),
        ("TOTAL",               "54", "8 tables, 7 clés étrangères, 18 contraintes CHECK"),
    ],
    caption = "Tableau 12. Récapitulatif des 8 tables du schéma UVCI.",
)


# ════════════════════════════════════════════════════════════════════════════
# ANNEXE B : MATRICE DES CONTRAINTES
# ════════════════════════════════════════════════════════════════════════════
doc.add_heading("Annexe B. — Matrice des contraintes", level=1)
add_simple_table(
    headers    = ["Table", "Clés primaires", "Clés étrangères", "UNIQUE", "CHECK"],
    col_widths = [4.5, 3.0, 3.0, 2.5, 2.5],
    rows_data  = [
        ("users",               "1 PK", "0 FK", "1", "1"),
        ("teachers",            "1 PK", "1 FK", "2", "2"),
        ("courses",             "1 PK", "0 FK", "0", "3"),
        ("academic_years",      "1 PK", "0 FK", "2", "1"),
        ("resources",           "1 PK", "2 FK", "1", "2"),
        ("activities",          "1 PK", "4 FK", "0", "4"),
        ("coefficient_configs", "1 PK", "0 FK", "1", "3"),
        ("quotas_statutaires",  "1 PK", "0 FK", "1", "2"),
        ("TOTAL",               "8",    "7",    "8", "18"),
    ],
    caption = "Tableau 13. Matrice récapitulative des contraintes d'intégrité par table.",
)


# ════════════════════════════════════════════════════════════════════════════
# ANNEXE C : SCHÉMA DES RELATIONS
# ════════════════════════════════════════════════════════════════════════════
doc.add_heading("Annexe C. — Schéma des relations", level=1)
add_para(
    "Le diagramme ci-dessous synthétise les relations entre les huit tables du schéma. "
    "Les flèches indiquent le sens de la clé étrangère (table enfant vers table parent). "
    "Les tables de paramétrage (coefficient_configs, quotas_statutaires) n'ont pas de clé "
    "étrangère vers les tables métier ; elles sont lues par les services applicatifs."
)
add_sql_block("""\
users (1) ─────────────────────────── (0,1) teachers
  │                                          │
  │ validated_by (FK)                        │ teacher_id (FK)
  ▼                                          ▼
activities (n) ─── (1) resources (n) ──── (1) courses
  │                      │
  │ academic_year_id (FK)│ teacher_id (FK, redondant — optimisation lecture)
  ▼                      ▼
academic_years (1)    teachers (1)

-- Tables de paramétrage (sans FK vers les tables métier) :
coefficient_configs   --> lue par le service de calcul (Vhtc = Ic x S)
quotas_statutaires    --> lue par le tableau de bord (taux d'atteinte du quota)\
""")
add_para(
    "La table RESOURCES joue le rôle de table de jonction entre TEACHERS, COURSES "
    "et le type d'activité/niveau, matérialisant la contrainte métier d'unicité. "
    "La table ACTIVITIES référence RESOURCES (et non directement TEACHERS × COURSES) "
    "afin de garantir la cohérence des données et d'éviter les duplications.",
    italic=True,
    size=11,
)

# ─── champ de mise à jour du TOC ─────────────────────────────────────────────
set_update_fields_on_open()

doc.save(OUT)
print(f"Sauvegardé → {OUT}")
