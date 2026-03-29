# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UVCI Gestion des Heures — a full-stack web app for managing teacher hours at UVCI, replacing manual Excel workflows with an automated system featuring facial recognition authentication.

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

# Run integration tests
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

- **`app/main.py`** — FastAPI app entry, CORS config, router registration
- **`app/models/models.py`** — SQLAlchemy ORM models (User, Teacher, Course, Resource, Activity, AcademicYear)
- **`app/schemas/schemas.py`** — Pydantic request/response schemas
- **`app/api/endpoints/`** — Route handlers: `auth`, `teachers`, `courses`, `activities`, `exports`, `dashboard`
- **`app/services/calculator.py`** — Hour calculation engine (complexity-based rates)
- **`app/core/security.py`** — JWT generation/verification, bcrypt hashing
- **`app/db/database.py`** — SQLAlchemy engine setup (`sqlite:///./sql_app.db`)

**Hour calculation rates** (from `calculator.py`):
- Level 1: 0.40 h/sequence (creation), ×0.5 for updates
- Level 2: 0.75 h/sequence
- Level 3: 1.50 h/sequence

### Frontend Structure

- **`src/app/`** — Next.js App Router pages (dashboard, teachers, activities, reports)
- **`src/components/layout/`** — `MainLayout`, `Sidebar`, `Navbar`
- **`src/context/AuthContext.tsx`** — Global auth state (JWT stored in localStorage)
- **`src/lib/api.ts`** — Axios instance with JWT interceptor (auto-attaches Bearer token)
- **`src/app/globals.css`** — CSS custom properties for design tokens

### Data Model Relationships

```
User (1:1) Teacher
Teacher (1:n) Resources
Teacher (1:n) Activities
Course (1:n) Resources
Resource (1:n) Activities
AcademicYear (1:n) Activities
```

### Authentication Flow

1. Email + password → JWT token (24h expiry)
2. Face recognition verification (FaceAPI / dlib)
3. Token stored in localStorage, attached via Axios interceptor

## Key Configuration Notes

- TypeScript path alias: `@/*` → `./src/*`
- CORS currently allows all origins (`allow_origins=["*"]`) — dev only
- JWT secret is hardcoded in `app/core/security.py` — use env vars for production
- Database: SQLite for dev (`sql_app.db`), PostgreSQL recommended for production
- User roles defined: `admin`, `secretary`, `teacher` — backend enforcement is partial
