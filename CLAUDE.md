# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UVCI Gestion des Heures — a full-stack web app for managing teacher hours at UVCI, replacing manual Excel workflows with an automated system.

## Commands

### Frontend (`/frontend`)

```bash
cd frontend
npm run dev       # Dev server at localhost:3000
npm run build     # Production build
npm run lint      # ESLint
```

### Backend (`/backend`)

```bash
# Activate virtual environment first
source venv/bin/activate

# Start API server (localhost:8000)
cd backend
uvicorn app.main:app --reload

# Smoke test end-to-end (login admin seedé + flux complet)
python verify_backend.py
```

> **Important:** This project uses **Next.js 16** with React 19 — APIs, conventions, and file structure may differ from older versions. Check `node_modules/next/dist/docs/` before writing frontend code. Heed deprecation notices.

## Architecture

Monorepo with two independent apps:

```
frontend/    # Next.js 16 + TypeScript + Tailwind CSS 4
backend/     # Python FastAPI + SQLAlchemy + SQLite
venv/        # Python virtual environment (shared)
```

### Backend Structure

- **`app/main.py`** — FastAPI app entry, CORS config, router registration, auto-seed at startup
- **`app/models/models.py`** — SQLAlchemy ORM models (User, Teacher, Course, Resource, Activity, AcademicYear, **CoefficientConfig**, **QuotaStatutaire**)
- **`app/schemas/schemas.py`** — Pydantic request/response schemas
- **`app/api/endpoints/`** — Route handlers: `auth`, `users`, `config`, `teachers`, `courses`, `activities`, `exports`, `dashboard`, `academic_years`
- **`app/services/calculator.py`** — Hour calculation engine (lit `CoefficientConfig` avec fallback sur le barème officiel hardcodé)
- **`app/core/security.py`** — JWT generation/verification, bcrypt hashing, RBAC guards (`require_admin`, `require_secretary`, `require_admin_or_secretary`, `require_authenticated`)
- **`app/db/database.py`** — SQLAlchemy engine setup (`sqlite:///./sql_app.db`)

**Hour calculation — barème officiel UVCI** (Vhtc = Ic × S, voir `OFFICIAL_BAREME` dans `calculator.py`) :

| Niveau | Création (Ic) | Mise à jour (Ic = ½ création) |
|--------|---------------|-------------------------------|
| 1 (contenus simples + quiz) | 0.40 | 0.20 |
| 2 (+25% activités interactives) | 0.75 | 0.375 |
| 3 (serious games, simulations) | 1.50 | 0.75 |

Les coefficients sont seedés dans `CoefficientConfig` au premier démarrage et peuvent être ajustés par l'admin via `PUT /config/coefficients`. Le calculator interroge cette table à chaque appel (fallback sur les constantes officielles si la table est vide).

### Frontend Structure

- **`src/app/`** — Next.js App Router pages, organisées par rôle :
  - `/dashboard/**` (admin), `/secretaire/**` (secrétaire), `/enseignant/**` (enseignant)
  - `/login`, `/` publics
- **`src/middleware.ts`** — garde route côté Edge selon cookie `role`
- **`src/components/layout/`** — `MainLayout`, `Sidebar`, `Navbar`
- **`src/context/AuthContext.tsx`** — Global auth state (JWT stored in localStorage + cookies pour le middleware)
- **`src/lib/api.ts`** — Axios instance with JWT interceptor (auto-attaches Bearer token)
- **`src/app/globals.css`** — CSS custom properties for design tokens

### Data Model Relationships

```
User (1:1) Teacher
Teacher (1:n) Resource (1:n) Activity
Course (1:n) Resource
AcademicYear (1:n) Activity
CoefficientConfig    # paramétrage admin : (niveau, type) → coefficient
QuotaStatutaire      # paramétrage admin : (grade, statut) → quota annuel
```

### Authentication Flow

1. Email + password → JWT token (**8h** d'expiration, `ACCESS_TOKEN_EXPIRE_MINUTES=480`)
2. Token stocké en `localStorage` ET cookie (`token`, `role`) pour le middleware Next.js
3. Axios attache automatiquement `Authorization: Bearer <token>` à chaque requête

> La reconnaissance faciale mentionnée dans le cahier des charges initial **n'a pas été retenue** par l'UVCI ; le code ne l'implémente pas.

### RBAC

| Endpoint | Accès |
|---|---|
| `POST /users/`, `PUT /users/*`, `PATCH /users/*` | admin uniquement |
| `PUT /config/coefficients`, `PUT /config/quotas` | admin uniquement |
| `POST /activities/`, `PUT /activities/{id}/validate` | admin OR secretary |
| `GET /dashboard/stats` | admin OR secretary |
| `GET /dashboard/teacher-stats/{id}` | admin/secretary, OU l'enseignant lui-même |
| `GET /activities/`, `/activities/teacher/{id}`, `/activities/volume/{id}` | authentifié ; les enseignants ne voient que leurs propres données |

## Key Configuration Notes

- TypeScript path alias: `@/*` → `./src/*`
- **CORS** : origines configurées via `CORS_ORIGINS` (CSV, ex. `https://app.vercel.app,http://localhost:3000`). Par défaut localhost:3000 seulement.
- **SECRET_KEY** : à définir en env. En dev, une clé éphémère est générée avec avertissement (les tokens sont invalidés au redémarrage). En prod Render, `render.yaml` génère la valeur automatiquement.
- Database: SQLite for dev (`sql_app.db`), PostgreSQL recommended for production
- User roles: `admin`, `secretary`, `teacher` — RBAC backend complet (cf. tableau ci-dessus)
- Seed automatique au premier démarrage : 3 users (admin/secretary/teacher), 5 enseignants, 10 cours, 20 ressources, 30 activités, 3 années académiques, 6 coefficients officiels, 8 quotas par défaut.

### Comptes seedés (dev/démo)

| Rôle | Email | Mot de passe |
|---|---|---|
| admin | `admin@uvci.ci` | `admin123` |
| secretary | `secretaire@uvci.ci` | `secretaire123` |
| teacher | `jkouame@uvci.ci` (et 4 autres) | `teacher123` |
