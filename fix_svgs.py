import re

with open('Rapport_Final_Groupe11.html', 'r', encoding='utf-8') as f:
    content = f.read()

mcd_svg = """<svg id="svg" width="100%" height="auto" viewBox="0 0 900 720" style="max-width: 900px;" xmlns="http://www.w3.org/2000/svg">
<defs>
  <style>
    .eb  { fill:#FFFF99; stroke:#CC8800; stroke-width:2; }
    .eh  { fill:#FFD700; stroke:#CC8800; stroke-width:2; }
    .et  { font:bold 12px Arial; fill:#333; text-anchor:middle; }
    .ea  { font:11px Arial; fill:#333; text-anchor:start; }
    .eu  { font:11px Arial; fill:#333; text-anchor:start; text-decoration:underline; }
    .ae  { fill:#00CCCC; stroke:#006666; stroke-width:2; }
    .at  { font:bold 11px Arial; fill:#004444; text-anchor:middle; dominant-baseline:middle; }
    .cl  { stroke:#444; stroke-width:1.5; fill:none; }
    .ct  { font:bold 10px Arial; fill:#CC0000; }
    .sep { stroke:#CC8800; stroke-width:1; }
  </style>
</defs>

<!-- LIGNES DE CONNEXION -->
<line class="cl" x1="120" y1="218" x2="120" y2="282"/>
<line class="cl" x1="120" y1="328" x2="120" y2="375"/>

<line class="cl" x1="420" y1="240" x2="420" y2="275"/>
<line class="cl" x1="420" y1="321" x2="420" y2="375"/>

<line class="cl" x1="225" y1="468" x2="245" y2="468"/>
<line class="cl" x1="295" y1="468" x2="320" y2="430"/>

<line class="cl" x1="520" y1="428" x2="540" y2="440"/>
<line class="cl" x1="610" y1="450" x2="630" y2="455"/>

<line class="cl" x1="765" y1="198" x2="760" y2="272"/>
<line class="cl" x1="760" y1="318" x2="755" y2="375"/>

<line class="cl" x1="160" y1="218" x2="410" y2="590"/>
<line class="cl" x1="490" y1="618" x2="700" y2="545"/>

<!-- CARDINALITÉS -->
<text class="ct" x="130" y="245">0,1</text>
<text class="ct" x="130" y="370">1,1</text>

<text class="ct" x="430" y="255">1,n</text>
<text class="ct" x="430" y="370">1,1</text>

<text class="ct" x="230" y="458">0,n</text>
<text class="ct" x="305" y="418">0,n</text>

<text class="ct" x="530" y="420">0,n</text>
<text class="ct" x="615" y="442">0,n</text>

<text class="ct" x="775" y="216">1,n</text>
<text class="ct" x="765" y="368">1,n</text>

<text class="ct" x="172" y="242">0,n</text>
<text class="ct" x="670" y="548">0,n</text>

<!-- ENTITÉS -->
<g transform="translate(20,60)">
  <rect class="eb" width="200" height="158" rx="3"/>
  <rect class="eh" width="200" height="28"  rx="3"/>
  <line class="sep" x1="0" y1="28" x2="200" y2="28"/>
  <text class="et" x="100" y="19">UTILISATEUR</text>
  <text class="eu" x="8" y="44">ID_Utilisateur</text>
  <text class="ea" x="8" y="62">Email_Utilisateur</text>
  <text class="ea" x="8" y="80">Mot_de_passe_Utilisateur</text>
  <text class="ea" x="8" y="98">Role_Utilisateur</text>
  <text class="ea" x="8" y="116">Est_actif_Utilisateur</text>
  <text class="ea" x="8" y="134">Cree_a_Utilisateur</text>
</g>

<g transform="translate(320,60)">
  <rect class="eb" width="200" height="196" rx="3"/>
  <rect class="eh" width="200" height="28"  rx="3"/>
  <line class="sep" x1="0" y1="28" x2="200" y2="28"/>
  <text class="et" x="100" y="19">COURS</text>
  <text class="eu" x="8" y="44">ID_Cours</text>
  <text class="ea" x="8" y="62">Intitule_Cours</text>
  <text class="ea" x="8" y="80">Filiere_Cours</text>
  <text class="ea" x="8" y="98">Niveau_Cours</text>
  <text class="ea" x="8" y="116">Semestre_Cours</text>
  <text class="ea" x="8" y="134">Nombre_heures_Cours</text>
  <text class="ea" x="8" y="152">Nombre_credits_Cours</text>
</g>

<g transform="translate(650,60)">
  <rect class="eb" width="230" height="140" rx="3"/>
  <rect class="eh" width="230" height="28"  rx="3"/>
  <line class="sep" x1="0" y1="28" x2="230" y2="28"/>
  <text class="et" x="115" y="19">ANNEE_ACADEMIQUE</text>
  <text class="eu" x="8" y="44">ID_Annee_academique</text>
  <text class="ea" x="8" y="62">Libelle_Annee_academique</text>
  <text class="ea" x="8" y="80">Date_debut_Annee_acad.</text>
  <text class="ea" x="8" y="98">Date_fin_Annee_acad.</text>
  <text class="ea" x="8" y="116">Est_active_Annee_acad.</text>
</g>

<g transform="translate(20,375)">
  <rect class="eb" width="205" height="214" rx="3"/>
  <rect class="eh" width="205" height="28"  rx="3"/>
  <line class="sep" x1="0" y1="28" x2="205" y2="28"/>
  <text class="et" x="102" y="19">ENSEIGNANT</text>
  <text class="eu" x="8" y="44">ID_Enseignant</text>
  <text class="ea" x="8" y="62">Nom_Enseignant</text>
  <text class="ea" x="8" y="80">Prenom_Enseignant</text>
  <text class="ea" x="8" y="98">Grade_Enseignant</text>
  <text class="ea" x="8" y="116">Statut_Enseignant</text>
  <text class="ea" x="8" y="134">Departement_Enseignant</text>
  <text class="ea" x="8" y="152">Taux_horaire_Enseignant</text>
  <text class="ea" x="8" y="170">Contact_Enseignant</text>
</g>

<g transform="translate(320,375)">
  <rect class="eb" width="200" height="120" rx="3"/>
  <rect class="eh" width="200" height="28"  rx="3"/>
  <line class="sep" x1="0" y1="28" x2="200" y2="28"/>
  <text class="et" x="100" y="19">RESSOURCE</text>
  <text class="eu" x="8" y="44">ID_Ressource</text>
  <text class="ea" x="8" y="62">Type_contenu_Ressource</text>
  <text class="ea" x="8" y="80">Niveau_complexite_Ress.</text>
  <text class="ea" x="8" y="98">Date_creation_Ressource</text>
</g>

<g transform="translate(630,375)">
  <rect class="eb" width="250" height="178" rx="3"/>
  <rect class="eh" width="250" height="28"  rx="3"/>
  <line class="sep" x1="0" y1="28" x2="250" y2="28"/>
  <text class="et" x="125" y="19">ACTIVITE_PEDAGOGIQUE</text>
  <text class="eu" x="8" y="44">ID_Activite_pedagogique</text>
  <text class="ea" x="8" y="62">Type_activite_Activite</text>
  <text class="ea" x="8" y="80">Nombre_sequences_Activite</text>
  <text class="ea" x="8" y="98">Volume_horaire_calcule</text>
  <text class="ea" x="8" y="116">Statut_validation_Activite</text>
  <text class="ea" x="8" y="134">Date_validation_Activite</text>
  <text class="ea" x="8" y="152">Cree_a_Activite</text>
</g>

<!-- ASSOCIATIONS -->
<ellipse class="ae" cx="120" cy="305" rx="52" ry="23"/>
<text class="at" x="120" y="305">APPARTENIR</text>

<ellipse class="ae" cx="420" cy="298" rx="46" ry="23"/>
<text class="at" x="420" y="298">CONTIENT</text>

<ellipse class="ae" cx="272" cy="468" rx="40" ry="23"/>
<text class="at" x="272" y="468">PRODUIT</text>

<ellipse class="ae" cx="575" cy="445" rx="45" ry="23"/>
<text class="at" x="575" y="445">CONCERNE</text>

<ellipse class="ae" cx="760" cy="295" rx="52" ry="23"/>
<text class="at" x="760" y="295">REGROUPE</text>

<ellipse class="ae" cx="450" cy="605" rx="46" ry="23"/>
<text class="at" x="450" y="605">VALIDE</text>

<!-- LÉGENDE -->
<rect x="20" y="660" width="16" height="14" fill="#FFFF99" stroke="#CC8800" stroke-width="1.5" rx="2"/>
<text x="42" y="672" font="11px Arial" font-size="11" fill="#444">Entité</text>
<ellipse cx="108" cy="667" rx="22" ry="11" fill="#00CCCC" stroke="#006666" stroke-width="1.5"/>
<text x="136" y="672" font-size="11" fill="#444">Association</text>
<text x="260" y="672" font-size="11" fill="#CC0000" font-weight="bold">0,n</text>
<text x="278" y="672" font-size="11" fill="#444">Cardinalité</text>
<text x="20" y="695" font-size="10" fill="#888">* Les attributs soulignés constituent la clé primaire (identifiant) de l'entité.</text>
</svg>"""

mld_svg = """<svg width="100%" height="auto" viewBox="0 0 920 840" style="max-width: 920px;" xmlns="http://www.w3.org/2000/svg">
<defs>
  <marker id="fk" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0,8 3,0 6" fill="#1a5276"/>
  </marker>
  <style>
    .th { fill:#1a5276; }
    .tb { fill:#EEF4FB; stroke:#2C5F8A; stroke-width:1.8; }
    .tn { font:bold 12px Arial; fill:#fff; text-anchor:middle; }
    .pk { font:bold 11px Arial; fill:#7D2D00; text-anchor:start; text-decoration:underline; }
    .fk { font:italic 11px Arial; fill:#1a5276; text-anchor:start; }
    .at { font:11px Arial; fill:#222; text-anchor:start; }
    .lg { font:10px Arial; fill:#555; }
    .cl { stroke:#1a5276; stroke-width:1.5; fill:none; marker-end:url(#fk); stroke-dasharray:5,3; }
  </style>
</defs>

<!-- CONNEXIONS FK -->
<line class="cl" x1="132" y1="280" x2="132" y2="218"/>
<line class="cl" x1="395" y1="280" x2="395" y2="218"/>
<line class="cl" x1="280" y1="355" x2="252" y2="355"/>
<line class="cl" x1="550" y1="370" x2="515" y2="340"/>
<line class="cl" x1="550" y1="415" x2="252" y2="400"/>
<line class="cl" x1="720" y1="280" x2="720" y2="173"/>
<polyline class="cl" points="895,290 905,290 905,8 15,8 15,120 18,120"/>

<!-- TABLES -->
<rect class="tb" x="18" y="20" width="235" height="198" rx="3"/>
<rect class="th" x="18" y="20" width="235" height="30"  rx="3"/>
<text class="tn" x="136" y="40">UTILISATEUR</text>
<line stroke="#2C5F8A" stroke-width="1" x1="18" y1="50" x2="253" y2="50"/>
<text class="pk" x="28" y="68">PK  id</text>
<text class="at" x="28" y="88">     email</text>
<text class="at" x="28" y="108">     mot_de_passe_hache</text>
<text class="at" x="28" y="128">     role</text>
<text class="at" x="28" y="148">     est_actif</text>
<text class="at" x="28" y="168">     encodage_facial</text>
<text class="at" x="28" y="188">     cree_a</text>

<rect class="tb" x="280" y="20" width="235" height="198" rx="3"/>
<rect class="th" x="280" y="20" width="235" height="30"  rx="3"/>
<text class="tn" x="398" y="40">COURS</text>
<line stroke="#2C5F8A" stroke-width="1" x1="280" y1="50" x2="515" y2="50"/>
<text class="pk" x="290" y="68">PK  id</text>
<text class="at" x="290" y="88">     intitule</text>
<text class="at" x="290" y="108">     filiere</text>
<text class="at" x="290" y="128">     niveau</text>
<text class="at" x="290" y="148">     semestre</text>
<text class="at" x="290" y="168">     nb_heures</text>
<text class="at" x="290" y="188">     nb_credits</text>

<rect class="tb" x="550" y="20" width="345" height="155" rx="3"/>
<rect class="th" x="550" y="20" width="345" height="30"  rx="3"/>
<text class="tn" x="723" y="40">ANNEE_ACADEMIQUE</text>
<line stroke="#2C5F8A" stroke-width="1" x1="550" y1="50" x2="895" y2="50"/>
<text class="pk" x="560" y="68">PK  id</text>
<text class="at" x="560" y="88">     libelle</text>
<text class="at" x="560" y="108">     date_debut</text>
<text class="at" x="560" y="128">     date_fin</text>
<text class="at" x="560" y="148">     est_active</text>

<rect class="tb" x="18" y="280" width="235" height="262" rx="3"/>
<rect class="th" x="18" y="280" width="235" height="30"  rx="3"/>
<text class="tn" x="136" y="300">ENSEIGNANT</text>
<line stroke="#2C5F8A" stroke-width="1" x1="18" y1="310" x2="253" y2="310"/>
<text class="pk" x="28" y="328">PK  id</text>
<text class="at" x="28" y="348">     nom</text>
<text class="at" x="28" y="368">     prenom</text>
<text class="at" x="28" y="388">     grade</text>
<text class="at" x="28" y="408">     statut</text>
<text class="at" x="28" y="428">     departement</text>
<text class="at" x="28" y="448">     taux_horaire</text>
<text class="at" x="28" y="468">     email</text>
<text class="at" x="28" y="488">     telephone</text>
<text class="fk" x="28" y="508">FK  utilisateur_id  →  UTILISATEUR.id</text>

<rect class="tb" x="280" y="280" width="235" height="174" rx="3"/>
<rect class="th" x="280" y="280" width="235" height="30"  rx="3"/>
<text class="tn" x="398" y="300">RESSOURCE</text>
<line stroke="#2C5F8A" stroke-width="1" x1="280" y1="310" x2="515" y2="310"/>
<text class="pk" x="290" y="328">PK  id</text>
<text class="at" x="290" y="348">     type_contenu</text>
<text class="at" x="290" y="368">     niveau_complexite</text>
<text class="at" x="290" y="388">     date_creation</text>
<text class="fk" x="290" y="408">FK  cours_id  →  COURS.id</text>
<text class="fk" x="290" y="428">FK  enseignant_id  →  ENSEIGNANT.id</text>

<rect class="tb" x="550" y="280" width="345" height="308" rx="3"/>
<rect class="th" x="550" y="280" width="345" height="30"  rx="3"/>
<text class="tn" x="723" y="300">ACTIVITE_PEDAGOGIQUE</text>
<line stroke="#2C5F8A" stroke-width="1" x1="550" y1="310" x2="895" y2="310"/>
<text class="pk" x="560" y="328">PK  id</text>
<text class="at" x="560" y="348">     type_activite</text>
<text class="at" x="560" y="368">     nb_sequences</text>
<text class="at" x="560" y="388">     volume_horaire_calcule</text>
<text class="at" x="560" y="408">     annee_academique</text>
<text class="at" x="560" y="428">     statut_validation</text>
<text class="at" x="560" y="448">     valide_le</text>
<text class="at" x="560" y="468">     cree_a</text>
<text class="fk" x="560" y="488">FK  ressource_id  →  RESSOURCE.id</text>
<text class="fk" x="560" y="508">FK  enseignant_id  →  ENSEIGNANT.id</text>
<text class="fk" x="560" y="528">FK  annee_id  →  ANNEE_ACADEMIQUE.id</text>
<text class="fk" x="560" y="548">FK  valide_par  →  UTILISATEUR.id</text>

<rect class="tb" x="175" y="620" width="295" height="130" rx="3"/>
<rect class="th" x="175" y="620" width="295" height="30"  rx="3"/>
<text class="tn" x="323" y="640">CONFIGURATION_COEFFICIENT</text>
<line stroke="#2C5F8A" stroke-width="1" x1="175" y1="650" x2="470" y2="650"/>
<text class="pk" x="185" y="668">PK  id</text>
<text class="at" x="185" y="688">     niveau_complexite</text>
<text class="at" x="185" y="708">     type_activite</text>
<text class="at" x="185" y="728">     coefficient</text>
<text class="lg" x="185" y="745">UNIQUE (niveau_complexite, type_activite)</text>

<rect class="tb" x="490" y="620" width="270" height="130" rx="3"/>
<rect class="th" x="490" y="620" width="270" height="30"  rx="3"/>
<text class="tn" x="625" y="640">QUOTA_STATUTAIRE</text>
<line stroke="#2C5F8A" stroke-width="1" x1="490" y1="650" x2="760" y2="650"/>
<text class="pk" x="500" y="668">PK  id</text>
<text class="at" x="500" y="688">     grade</text>
<text class="at" x="500" y="708">     statut</text>
<text class="at" x="500" y="728">     nb_heures_quota</text>
<text class="lg" x="500" y="745">UNIQUE (grade, statut)</text>

<!-- LÉGENDE -->
<rect x="18" y="795" width="14" height="14" fill="#1a5276" rx="2"/>
<text x="38" y="806" font-size="11" font-family="Arial" fill="#444">En-tête de table</text>
<text x="170" y="806" font-size="11" font-family="Arial" fill="#7D2D00" font-weight="bold" text-decoration="underline">PK</text>
<text x="190" y="806" font-size="11" font-family="Arial" fill="#444">Clé primaire (soulignée)</text>
<text x="370" y="806" font-size="11" font-family="Arial" fill="#1a5276" font-style="italic">FK</text>
<text x="390" y="806" font-size="11" font-family="Arial" fill="#444">Clé étrangère</text>
<line x1="490" y1="800" x2="530" y2="800" stroke="#1a5276" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#fk)"/>
<text x="540" y="806" font-size="11" font-family="Arial" fill="#444">Relation de référence</text>
</svg>"""

new_content = re.sub(r'<svg id="svg".*?</svg>', mcd_svg, content, flags=re.DOTALL)
new_content = re.sub(r'<svg width="1260" height="840".*?</svg>', mld_svg, new_content, flags=re.DOTALL)

# Let's also add viewBox and max-width to the other SVGs to make sure they are responsive and clean!
new_content = re.sub(r'<svg width="800" height="300">', r'<svg width="100%" height="auto" viewBox="0 0 800 300" style="max-width: 800px;">', new_content)
new_content = re.sub(r'<svg width="620" height="50">', r'<svg width="100%" height="auto" viewBox="0 0 620 50" style="max-width: 620px;">', new_content)
new_content = re.sub(r'<svg width="620" height="550">', r'<svg width="100%" height="auto" viewBox="0 0 620 550" style="max-width: 620px;">', new_content)
new_content = re.sub(r'<svg width="620" height="470">', r'<svg width="100%" height="auto" viewBox="0 0 620 470" style="max-width: 620px;">', new_content)
new_content = re.sub(r'<svg width="620" height="590">', r'<svg width="100%" height="auto" viewBox="0 0 620 590" style="max-width: 620px;">', new_content)

with open('Rapport_Final_Groupe11.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SVGs replaced successfully.")
