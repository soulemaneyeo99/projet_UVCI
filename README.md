# UVCI — Gestion des Heures

Application web full-stack de **gestion des heures d'enseignement** pour l'Université Virtuelle de Côte d'Ivoire (UVCI). Elle remplace le suivi manuel sous Excel par un système automatisé : saisie des activités pédagogiques, calcul du volume horaire selon le barème officiel, validation par le secrétariat, tableaux de bord et exports (PDF / Excel).

## Stack technique

| Couche | Technologies |
|--------|--------------|
| Frontend | Next.js 16 · React 19 · TypeScript · Tailwind CSS 4 |
| Backend | Python · FastAPI · SQLAlchemy |
| Base de données | SQLite (dev) · PostgreSQL (production) |
| Authentification | JWT (expiration 8 h) · bcrypt · RBAC (admin / secrétaire / enseignant) |
| Déploiement | Render (`render.yaml`) |

## Structure du dépôt

```
backend/     # API FastAPI (modèles, schémas, endpoints, moteur de calcul, sécurité)
frontend/    # Application Next.js (App Router, organisée par rôle)
database/    # schema_uvci.sql — DDL PostgreSQL de référence
render.yaml  # Configuration de déploiement Render
```

## Démarrage rapide

### Backend (API — http://localhost:8000)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

cd backend
uvicorn app.main:app --reload
```

La base SQLite (`sql_app.db`) et les données de démonstration sont **créées automatiquement** au premier démarrage.

### Frontend (http://localhost:3000)

```bash
cd frontend
npm install
npm run dev
```

## Comptes de démonstration

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Administrateur | `admin@uvci.ci` | `admin123` |
| Secrétaire | `secretaire@uvci.ci` | `secretaire123` |
| Enseignant | `jkouame@uvci.ci` | `teacher123` |

## Barème officiel de calcul

Le volume horaire est calculé selon la formule **Vhtc = Ic × S** (Ic = coefficient, S = nombre de séquences) :

| Niveau de complexité | Création (Ic) | Mise à jour (½ création) |
|----------------------|---------------|--------------------------|
| 1 — contenus simples + quiz | 0.40 | 0.20 |
| 2 — +25 % d'activités interactives | 0.75 | 0.375 |
| 3 — serious games, simulations | 1.50 | 0.75 |

Les coefficients sont paramétrables par l'administrateur (`PUT /config/coefficients`).

## Tests & qualité

```bash
# Backend — tests unitaires du moteur de calcul (sans dépendance externe)
cd backend && python test_calculator.py

# Backend — test d'intégration de bout en bout (login, RBAC, calcul, exports)
python verify_backend.py

# Frontend — lint
cd frontend && npm run lint
```

## Rôles & permissions (RBAC)

- **Administrateur** : gestion des utilisateurs, paramétrage (coefficients, quotas), accès complet.
- **Secrétaire** : saisie et validation des activités, tableaux de bord, rapports.
- **Enseignant** : consultation de ses propres activités, profil et récapitulatif.

## Déploiement

Le fichier `render.yaml` configure le déploiement sur [Render](https://render.com). En production, utiliser **PostgreSQL** et définir la variable d'environnement `SECRET_KEY` (générée automatiquement par Render) ainsi que `CORS_ORIGINS`.
