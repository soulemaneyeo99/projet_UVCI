import re

# Read the original HTML file
with open('Rapport_Final_Complet.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract SVGs
mcd_svg = re.search(r'(<div class="svg-container"><svg id="svg".*?</div>)', content, re.DOTALL).group(1)
mct_flux_svg = re.search(r'(<div class="svg-container"><svg width="800".*?</div>)', content, re.DOTALL).group(1)
mct_ordo_svg = re.search(r'(<div class="svg-container"><svg width="620".*?</div>)', content, re.DOTALL).group(1)
mld_svg = re.search(r'(<div class="svg-container"><svg width="1260".*?</div>)', content, re.DOTALL).group(1)
sql_code = re.search(r'(<div class="sql-code">.*?</div>\s*</div>)', content, re.DOTALL).group(1)

html_template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Rapport de Projet UVCI - Groupe 11</title>
<style>
    body {{ font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 1.6; color: #000; max-width: 21cm; margin: 0 auto; padding: 2cm; }}
    h1 {{ font-size: 24pt; text-align: center; color: #1a3b5c; margin-top: 50px; text-transform: uppercase; }}
    h2 {{ font-size: 18pt; color: #2980B9; border-bottom: 2px solid #2980B9; margin-top: 50px; page-break-before: always; text-transform: uppercase; }}
    h3 {{ font-size: 14pt; color: #d35400; margin-top: 30px; text-decoration: underline; }}
    h4 {{ font-size: 12pt; font-weight: bold; margin-top: 20px; }}
    p {{ text-align: justify; margin-bottom: 15px; }}
    ul {{ margin-bottom: 15px; }}
    li {{ margin-bottom: 5px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 10pt; }}
    th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
    th {{ background-color: #ecf0f1; }}
    .svg-container {{ text-align: center; margin: 30px 0; page-break-inside: avoid; }}
    .svg-container svg {{ max-width: 100%; height: auto; }}
    .sql-code {{ font-family: 'Courier New', Courier, monospace; font-size: 9pt; background: #f4f6f7; padding: 15px; border: 1px solid #dcdde1; border-radius: 5px; page-break-inside: avoid; }}
    pre {{ background: #f4f6f7; padding: 10px; border: 1px solid #dcdde1; font-size: 10pt; white-space: pre-wrap; }}
    .cover-page {{ display: flex; flex-direction: column; justify-content: space-between; min-height: 90vh; text-align: center; }}
    .cover-header {{ margin-top: 50px; }}
    .cover-title {{ margin: 80px 0; }}
    .cover-members {{ text-align: left; margin: 0 auto; width: 80%; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; }}
    .cover-footer {{ margin-top: auto; margin-bottom: 50px; font-weight: bold; }}
    .part-title {{ font-size: 22pt; text-align: center; color: #2c3e50; margin-top: 40vh; page-break-before: always; page-break-after: always; text-transform: uppercase; border: 4px double #2c3e50; padding: 20px; }}
    @page {{ size: A4; margin: 2cm; }}
</style>
</head>
<body>

    <div class="cover-page">
        <div class="cover-header">
            <h2 style="border: none; page-break-before: avoid; margin-top: 0;">Université Virtuelle de Côte d'Ivoire (UVCI)</h2>
            <p style="font-size: 14pt; font-weight: bold;">Licence en Informatique et Sciences du Numérique</p>
            <p>Spécialité : Développement d'Applications et e-Services (DAS)</p>
        </div>

        <div class="cover-title">
            <h1>RAPPORT DE PROJET DE FIN D'ANNÉE</h1>
            <p style="font-size: 16pt; margin-top: 20px; font-style: italic; font-weight: bold;">Conception et réalisation d'un système de gestion des heures pédagogiques des enseignants</p>
        </div>

        <div class="cover-members">
            <h3 style="margin-top: 0; color: #2c3e50; border-bottom: 1px solid #ccc; padding-bottom: 10px;">Groupe 11 - PCT DAS</h3>
            <p><strong>Encadreur :</strong> M. SANGARE SEYDOU (seydou1.sangare@uvci.edu.ci)</p>
            <ul style="list-style-type: none; padding-left: 0;">
                <li><strong>1.</strong> YEO YANOUGUI SOULEYMANE – 05-95-34-48-14 – yanougui3.yeo@uvci.edu.ci (Formation Initiale)</li>
                <li><strong>2.</strong> TUO CHIGATA JEAN MARC – 07-69-40-24-74 – chigata.tuo@uvci.edu.ci (Formation Initiale)</li>
                <li><strong>3.</strong> SOUMAHORO SOUALIO – 07-07-70-73-49 – soualio.soumahoro@uvci.edu.ci (Formation Continue)</li>
                <li><strong>4.</strong> SEDJI YEDO LINDA COLOMBE TIPHAINE – 07-87-80-10-04 – yedo.sedji@uvci.edu.ci (Formation Continue)</li>
                <li><strong>5.</strong> ASSALE CHIMENE-FLORE – 07-77-23-65-08 – chimeneflore.assale@uvci.edu.ci (Formation Continue)</li>
            </ul>
        </div>

        <div class="cover-footer">
            <p>Année Académique : 2024 - 2025</p>
        </div>
    </div>

    <!-- SECTIONS LIMINAIRES -->
    <h2 style="text-align:center; border:none; color:#2c3e50;">AVANT-PROPOS</h2>
    <p>L'Université Virtuelle de Côte d'Ivoire (UVCI) a pour mission de développer et de vulgariser l'enseignement à distance à travers les technologies de l'information et de la communication. C'est dans ce cadre novateur que s'inscrit notre formation en Licence Informatique et Sciences du Numérique, option Développement d'Applications et e-Services (DAS). Ce projet de fin d'année représente l'aboutissement de nos apprentissages théoriques et pratiques, nous permettant de nous confronter aux réalités de la conception de systèmes d'information professionnels.</p>

    <h2 style="text-align:center; border:none; color:#2c3e50;">DÉDICACE</h2>
    <p>Nous dédions ce travail à nos familles respectives pour leur soutien indéfectible tout au long de notre parcours universitaire. Leurs encouragements ont été une source constante de motivation.</p>

    <h2 style="text-align:center; border:none; color:#2c3e50;">REMERCIEMENTS</h2>
    <p>Nous tenons à exprimer notre profonde gratitude à notre encadreur, Monsieur SANGARE SEYDOU, pour son suivi rigoureux, ses conseils avisés et sa disponibilité. Nos remerciements s'adressent également à l'ensemble du corps professoral et à la direction de l'Université Virtuelle de Côte d'Ivoire pour la qualité de l'enseignement dispensé.</p>

    <h2>INTRODUCTION</h2>
    <h4>Contexte général du projet</h4>
    <p>Au sein de l'Université Virtuelle de Côte d'Ivoire, le modèle pédagogique repose fondamentalement sur la production, la mise à jour et la diffusion de ressources numériques. La gestion administrative des activités du corps enseignant (permanents et vacataires) implique de répertorier ces productions pour évaluer les volumes horaires et, in fine, calculer les rémunérations associées.</p>
    
    <h4>Problématique</h4>
    <p>Actuellement, la déclaration et le suivi des activités pédagogiques manquent d'un système centralisé et automatisé. Le processus manuel engendre des lourdeurs administratives, des risques d'erreurs dans le calcul des quotas horaires, et un manque de visibilité pour les enseignants concernant le statut de leurs déclarations. Comment pouvons-nous optimiser et sécuriser ce processus de bout en bout ?</p>
    
    <h4>Objectifs</h4>
    <p>L'objectif principal de ce projet est de concevoir et de développer une application web permettant de :</p>
    <ul>
        <li>Centraliser les déclarations d'activités pédagogiques des enseignants.</li>
        <li>Automatiser le calcul des volumes horaires via l'application de coefficients prédéfinis.</li>
        <li>Dématérialiser le circuit de validation par l'administration.</li>
        <li>Générer automatiquement les états de paiement après déduction des quotas statutaires.</li>
    </ul>

    <h4>Méthodologie</h4>
    <p>Pour mener à bien ce projet, nous avons adopté la méthode MERISE. Cette approche systémique nous permet d'assurer une séparation rigoureuse entre l'analyse des données et celle des traitements, garantissant ainsi la conception d'un système robuste, cohérent et évolutif.</p>

    <h4>Organisation du rapport</h4>
    <p>Ce rapport est structuré en trois grandes parties. La première partie dresse les généralités et l'étude préalable du projet. La deuxième partie est consacrée à l'étude détaillée en s'appuyant sur les modèles de la méthode MERISE. Enfin, la troisième partie aborde la réalisation technique et le déploiement de la solution.</p>

    <div class="part-title">Première partie : GÉNÉRALITÉS</div>

    <h2>Chapitre I : ÉTUDE PRÉALABLE</h2>
    <h3>I. Présentation générale du projet</h3>
    <h4>1. Contexte du projet</h4>
    <p>La digitalisation des processus administratifs est un enjeu majeur pour les institutions d'enseignement supérieur modernes. À l'UVCI, l'essor continu des effectifs étudiants et la diversification des parcours de formation nécessitent une organisation administrative sans faille, particulièrement en ce qui concerne la gestion des ressources humaines enseignantes et de leurs activités.</p>

    <h4>2. Objectifs et résultats attendus (Cahier des charges)</h4>
    <p>Le cahier des charges impose la création d'un système capable de gérer différents profils d'utilisateurs (Enseignants, Secrétaires, Administrateurs). Les résultats attendus incluent : une interface d'authentification sécurisée, un module de saisie des activités pour les enseignants, un tableau de bord de validation pour l'administration, et un moteur de génération d'exports pour la comptabilité.</p>

    <h3>II. Étude de l'existant</h3>
    <h4>1. Présentation et critique de l'existant</h4>
    <p>Le système actuel repose en grande partie sur l'utilisation de tableurs et d'échanges de courriels. Les enseignants remplissent des fiches de déclaration qui sont ensuite consolidées manuellement. Cette méthode présente de sérieuses limites :</p>
    <ul>
        <li><strong>Redondance et perte de données :</strong> La manipulation manuelle de multiples fichiers augmente le risque d'erreurs.</li>
        <li><strong>Délais de traitement :</strong> Le temps de vérification et de validation est excessivement long.</li>
        <li><strong>Sécurité :</strong> L'absence d'un référentiel centralisé pose des problèmes de confidentialité et d'intégrité des informations financières.</li>
    </ul>

    <h4>2. Ébauche de solution proposée</h4>
    <p>Notre solution est une plateforme web intégrée. Elle offrira un portail en libre-service pour les enseignants, garantissant une transparence totale sur l'état de leurs activités. Pour l'administration, elle proposera des outils de validation en masse et d'automatisation des calculs, réduisant ainsi drastiquement la charge de travail manuel et sécurisant le processus de rémunération.</p>

    <div class="part-title">Deuxième partie : ÉTUDE DÉTAILLÉE</div>

    <h2>Chapitre I : PRÉSENTATION DE LA MÉTHODE MERISE</h2>
    <h3>I. Définition</h3>
    <p>MERISE (Méthode d'Étude et de Réalisation Informatique pour les Systèmes d'Entreprise) est une méthode de conception, de développement et de réalisation de projets informatiques. Elle propose une démarche articulée autour de la séparation des données et des traitements pour assurer une modélisation complète du système d'information.</p>

    <h3>II. Principes généraux</h3>
    <p>La méthode MERISE repose sur une approche systémique. Elle aborde le système d'information de manière globale en étudiant la communication, l'organisation et la mémorisation de l'information. L'indépendance entre les données (qui ont une structure statique) et les traitements (qui sont dynamiques) est son principe fondamental.</p>

    <h3>III. Les trois niveaux d'abstraction</h3>
    <p>La démarche de modélisation s'effectue sur trois niveaux :</p>
    <ul>
        <li><strong>Le niveau Conceptuel :</strong> Il décrit le "Quoi". Que fait le système ? Quelles sont les données manipulées et les règles de gestion indépendamment des contraintes techniques ou organisationnelles.</li>
        <li><strong>Le niveau Logique / Organisationnel :</strong> Il décrit le "Qui, Où, Quand". Il intègre les choix d'organisation du travail et la structuration des données en vue de leur informatisation (sans choix technique précis).</li>
        <li><strong>Le niveau Physique / Opérationnel :</strong> Il décrit le "Comment". C'est l'implémentation technique finale, liée aux outils logiciels et matériels choisis (SGBD, langages).</li>
    </ul>

    <h2>Chapitre II : MODÉLISATION CONCEPTUELLE DES DONNÉES (MCD)</h2>
    <h3>I. Définitions et concepts</h3>
    <p>Le Modèle Conceptuel des Données (MCD) a pour but de formaliser la structure et la sémantique des informations du système. Il repose sur les concepts d'entités (objets de gestion), d'associations (liens entre objets) et de propriétés (attributs décrivant ces objets).</p>

    <h3>II. Formalisme utilisé</h3>
    <p>Nous utilisons le formalisme standard Entité-Association. Les entités sont représentées par des rectangles, les associations par des ovales, et les liens sont porteurs de cardinalités indiquant le nombre minimum et maximum de participations d'une occurrence d'entité à une association.</p>

    <h3>III. Règles de gestion</h3>
    <p>Les règles suivantes ont dicté la construction du MCD :</p>
    <ul>
        <li>Un utilisateur possède un rôle unique qui définit ses droits d'accès.</li>
        <li>Un enseignant est caractérisé par un grade et un statut (permanent ou vacataire) qui déterminent son quota horaire réglementaire.</li>
        <li>Une ressource pédagogique appartient obligatoirement à un et un seul cours.</li>
        <li>Une activité pédagogique est l'action menée sur une ressource (création, mise à jour). Son volume horaire est calculé selon un coefficient.</li>
        <li>Les activités sont regroupées par année académique pour permettre les bilans annuels.</li>
    </ul>

    <h3>IV. Dictionnaire des données</h3>
    <p>Le dictionnaire des données recense l'ensemble des propriétés du système. En voici un extrait représentatif :</p>
    <table>
        <tr><th>Donnée</th><th>Type</th><th>Description</th></tr>
        <tr><td>Matricule / ID Enseignant</td><td>Entier</td><td>Identifiant unique de l'enseignant</td></tr>
        <tr><td>Grade</td><td>Texte</td><td>Grade académique (ex: Maître de Conférences)</td></tr>
        <tr><td>Statut</td><td>Texte</td><td>Permanent ou Vacataire</td></tr>
        <tr><td>Type Activité</td><td>Texte</td><td>Nature de l'intervention (ex: Création vidéo)</td></tr>
        <tr><td>Volume Horaire</td><td>Réel</td><td>Nombre d'heures calculé pour l'activité</td></tr>
        <tr><td>Statut Validation</td><td>Texte</td><td>En attente, Validée ou Rejetée</td></tr>
    </table>

    <h3>V. Structure d'accès théorique</h3>
    <p>Pour éditer l'état de paiement, le système d'information navigue des instances d'<strong>Année Académique</strong> vers les <strong>Activités</strong> validées. De là, il remonte à l'<strong>Enseignant</strong>, consulte ses propriétés de Grade et Statut pour interroger le référentiel des quotas, opère la soustraction, et détermine le montant final.</p>

    <h3>VI. Schéma du MCD</h3>
    {mcd_svg}

    <h2>Chapitre III : MODÉLISATION LOGIQUE DES DONNÉES (MLD)</h2>
    <h3>I. Définition du MLD</h3>
    <p>Le Modèle Logique des Données (MLD) est la traduction du MCD adaptée au paradigme relationnel. Il prépare l'implémentation dans une base de données en résolvant les associations complexes et en définissant les clés étrangères.</p>

    <h3>II. Concepts de base</h3>
    <p>Le MLD s'articule autour de tables (relations), de colonnes (attributs), de clés primaires (identifiants uniques d'une ligne) et de clés étrangères (références à la clé primaire d'une autre table).</p>

    <h3>III. Règle de passage MCD → MLD</h3>
    <p>Le passage s'est effectué selon les règles standards :</p>
    <ul>
        <li>Chaque entité du MCD devient une table. L'identifiant devient la clé primaire.</li>
        <li>Pour les associations de type (1,n) - (0,n) / (1,1), la clé primaire de l'entité côté (0,n) migre comme clé étrangère dans la table issue de l'entité côté (1,1).</li>
        <li>Les associations de type (n,m) se transforment en tables de jointure (non présentes dans notre modèle simplifié qui a été optimisé).</li>
    </ul>

    <h3>IV. Schéma du MLD</h3>
    {mld_svg}

    <h2>Chapitre IV : MODÉLISATION CONCEPTUELLE DES TRAITEMENTS (MCT)</h2>
    <h3>I. Définition</h3>
    <p>Le Modèle Conceptuel des Traitements (MCT) décrit les activités réalisées par le système en réponse aux sollicitations (événements) de l'environnement extérieur, en faisant abstraction des contraintes d'organisation ou de moyens techniques.</p>

    <h3>II. Concepts de base</h3>
    <p>Le MCT utilise les concepts suivants :</p>
    <ul>
        <li><strong>Acteur :</strong> Entité externe (Enseignant, Administration) ou interne interagissant avec le système.</li>
        <li><strong>Événement :</strong> Fait déclencheur d'un traitement.</li>
        <li><strong>Opération :</strong> Ensemble d'actions exécutées sans interruption en réponse à un ou plusieurs événements synchronisés.</li>
        <li><strong>Résultat :</strong> Événement produit par l'achèvement d'une opération.</li>
    </ul>

    <h3>III. Diagrammes utilisés</h3>
    <h4>1. Diagramme des flux</h4>
    <p>Ce diagramme illustre les échanges d'informations entre les acteurs du système.</p>
    {mct_flux_svg}

    <h4>2. Graphe d'ordonnancement</h4>
    <p>Le processus suit l'ordre chronologique de la déclaration à la validation, jusqu'à l'export final.</p>
    
    <h4>3. Schéma global du MCT</h4>
    <p>Les diagrammes suivants détaillent les opérations majeures de notre système.</p>
    {mct_ordo_svg}

    <div class="part-title">Troisième partie : RÉALISATION TECHNIQUE</div>

    <h2>Chapitre I : MISE EN ŒUVRE DE LA BASE DE DONNÉES</h2>
    <h3>I. Modèle Physique de Données (MPD)</h3>
    <p>Le Modèle Physique de Données (MPD) traduit le MLD dans le langage de définition de données (DDL) propre au Système de Gestion de Base de Données choisi. Il inclut les types de données physiques et les contraintes techniques.</p>

    <h3>II. Choix du SGBDR</h3>
    <p>Pour ce projet, notre choix s'est porté sur <strong>PostgreSQL</strong> (bien que les scripts soient compatibles SQLite/MySQL). PostgreSQL est reconnu pour sa robustesse, sa gestion stricte de l'intégrité référentielle et sa capacité à traiter de forts volumes de données transactionnelles en toute sécurité.</p>

    <h3>III. Génération du schéma MPD</h3>
    <p>Le schéma a été généré en veillant à l'optimisation des types (utilisation de VARCHAR pour les chaînes de longueur variable, REAL pour les données financières) et à la mise en place d'index sur les clés étrangères pour accélérer les requêtes de jointure.</p>

    <h3>IV. Scripts SQL de création des tables</h3>
    {sql_code}

    <h3>V. Intégrité référentielle et indexation</h3>
    <p>Comme démontré dans les scripts SQL, l'intégrité est assurée par l'utilisation stricte de clauses <code>FOREIGN KEY</code>, empêchant la création d'activités pour des enseignants inexistants (contrainte d'existence). Des clauses <code>UNIQUE</code> ont été ajoutées pour empêcher les doublons de paramétrage (ex: quota par grade).</p>

    <h2>Chapitre II : INTERFACE UTILISATEUR</h2>
    <h3>I. Choix du langage et des outils</h3>
    <p>Pour répondre aux exigences d'ergonomie et de performance :</p>
    <ul>
        <li><strong>Backend :</strong> Nous avons utilisé <strong>Python</strong> avec le framework <strong>FastAPI</strong>, couplé à l'ORM <strong>SQLAlchemy</strong> pour la gestion de la base de données. FastAPI permet la création d'API RESTful très performantes.</li>
        <li><strong>Frontend :</strong> Nous avons opté pour <strong>Next.js</strong> (React) et <strong>TailwindCSS</strong>, permettant de concevoir des interfaces réactives (Single Page Application) au design moderne et épuré.</li>
    </ul>

    <h3>II. Présentation de quelques IHM</h3>
    <p>L'interface a été pensée pour être intuitive. Elle se décline en plusieurs vues selon les rôles :</p>
    <ul>
        <li><strong>Vue Enseignant :</strong> Un formulaire simplifié permet de déclarer une activité en sélectionnant le cours, le type de ressource et la complexité. Un tableau de bord personnel affiche l'état d'avancement des validations.</li>
        <li><strong>Vue Administration :</strong> Une grille de données (DataGrid) présente l'ensemble des activités en attente. Des boutons d'action rapide permettent d'approuver ou de rejeter les déclarations en un clic. Un module d'export permet de générer les fichiers de paiement au format tableur.</li>
    </ul>

    <h3>III. Connexion à la base de données</h3>
    <p>La connexion entre le frontend et la base de données s'effectue via l'API REST. Le backend gère la couche d'accès aux données grâce à SQLAlchemy, qui traduit les objets Python en requêtes SQL sécurisées, prévenant ainsi les risques d'injections SQL. L'authentification est sécurisée par un système de jetons JWT (JSON Web Tokens).</p>

    <h2>CONCLUSION</h2>
    <h4>Bilan du projet</h4>
    <p>La conception de ce système de gestion des heures pédagogiques pour l'UVCI a été une expérience hautement formatrice. En appliquant rigoureusement la méthodologie MERISE, nous avons pu transformer un besoin administratif complexe en une solution logicielle structurée et fiable. Le passage systématique par les modèles (MCD, MLD, MCT) a garanti l'exhaustivité de l'analyse avant l'écriture de la moindre ligne de code.</p>

    <h4>Difficultés rencontrées</h4>
    <p>La principale difficulté a résidé dans la modélisation précise des règles de calcul des volumes horaires et des quotas, nécessitant de bien séparer le paramétrage (tables de configuration) des données opérationnelles (activités) pour rendre le système dynamique.</p>

    <h4>Perspectives d'amélioration ou d'évolution</h4>
    <p>Le système conçu est évolutif. À l'avenir, il pourrait intégrer un module de signature électronique des états de paiement par les enseignants, ou être interconnecté avec le système comptable global de l'université pour une automatisation complète de la chaîne de valeur.</p>

</body>
</html>
"""

with open('Rapport_Final_Groupe11.html', 'w', encoding='utf-8') as f:
    f.write(html_template)
print("HTML Generated successfully.")
