from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.endpoints import auth, teachers, courses, activities, exports, dashboard, academic_years
from app.db.database import engine, get_db
from app.models import models

# Create all database tables (safe no-op if they already exist)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GestionHeures UVCI API",
    version="1.0.0",
    description="API de gestion des heures pédagogiques – Université Virtuelle de Côte d'Ivoire",
)

# CORS – allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,           prefix="/auth",           tags=["Authentication"])
app.include_router(teachers.router,       prefix="/teachers",       tags=["Teachers"])
app.include_router(courses.router,        prefix="/courses",        tags=["Courses"])
app.include_router(activities.router,     prefix="/activities",     tags=["Activities"])
app.include_router(exports.router,        prefix="/exports",        tags=["Exports"])
app.include_router(dashboard.router,      prefix="/dashboard",      tags=["Dashboard"])
app.include_router(academic_years.router, prefix="/academic-years", tags=["Academic Years"])


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API GestionHeures UVCI", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Seed endpoint – populates the database with demo data for development
# ---------------------------------------------------------------------------

@app.post("/seed", tags=["Dev"])
def seed_data(db: Session = Depends(get_db)):
    from app.models.models import Teacher, Course, AcademicYear, User, Activity, Resource
    from app.core.security import get_password_hash
    from app.services.calculator import calculate_volume_horaire
    import random

    random.seed(42)

    # ── Users ────────────────────────────────────────────────────────────────
    def get_or_create_user(email: str, password: str, role: str) -> User:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(
                email=email,
                hashed_password=get_password_hash(password),
                role=role,
            )
            db.add(u)
            db.flush()
        return u

    get_or_create_user("admin@uvci.ci",       "admin123",       "admin")
    get_or_create_user("secretaire@uvci.ci",  "secretaire123",  "secretary")

    # ── Academic year ────────────────────────────────────────────────────────
    ay = db.query(AcademicYear).filter(AcademicYear.libelle == "2024-2025").first()
    if not ay:
        ay = AcademicYear(
            libelle="2024-2025",
            date_debut="2024-09-01",
            date_fin="2025-07-31",
            status=True,
        )
        db.add(ay)
        db.flush()

    # ── Teachers ─────────────────────────────────────────────────────────────
    teachers_data = [
        ("Kouamé",    "Jean-Pierre",  "Professeur",            "Permanent",  "Informatique",          5000.0, "jkouame@uvci.ci"),
        ("Bamba",     "Aminata",      "Maître de Conférences", "Permanent",  "Mathématiques",         4500.0, "abamba@uvci.ci"),
        ("Ouattara",  "Ibrahim",      "Maître-Assistant",      "Permanent",  "Sciences Économiques",  3500.0, "iouattara@uvci.ci"),
        ("Koffi",     "Marie",        "Assistant",             "Vacataire",  "Informatique",          2500.0, "mkoffi@uvci.ci"),
        ("Diabaté",   "Seydou",       "Maître-Assistant",      "Permanent",  "Droit",                 3500.0, "sdiabaté@uvci.ci"),
        ("Traoré",    "Fatoumata",    "Professeur",            "Permanent",  "Langues",               5000.0, "ftraore@uvci.ci"),
        ("Coulibaly", "Moussa",       "Assistant",             "Vacataire",  "Mathématiques",         2500.0, "mcoulibaly@uvci.ci"),
        ("Yao",       "Evelyne",      "Maître de Conférences", "Permanent",  "Informatique",          4500.0, "eyao@uvci.ci"),
    ]

    created_teachers = []
    for nom, prenom, grade, statut, dept, taux, email in teachers_data:
        t = db.query(Teacher).filter(Teacher.email == email).first()
        if not t:
            u = get_or_create_user(email, "teacher123", "teacher")
            t = Teacher(
                nom=nom, prenom=prenom, grade=grade, statut=statut,
                departement=dept, taux_horaire=taux, email=email,
                user_id=u.id,
            )
            db.add(t)
            db.flush()
        created_teachers.append(t)

    # ── Courses ──────────────────────────────────────────────────────────────
    courses_data = [
        ("Programmation Python",                  "Informatique",         "L1", "S1"),
        ("Algorithmes et Structures de Données",  "Informatique",         "L2", "S1"),
        ("Base de Données",                       "Informatique",         "L2", "S2"),
        ("Développement Web",                     "Informatique",         "L3", "S1"),
        ("Intelligence Artificielle",             "Informatique",         "M1", "S1"),
        ("Analyse Mathématique",                  "Mathématiques",        "L1", "S1"),
        ("Algèbre Linéaire",                      "Mathématiques",        "L1", "S2"),
        ("Statistiques",                          "Mathématiques",        "L2", "S1"),
        ("Économie Générale",                     "Sciences Économiques", "L1", "S1"),
        ("Droit des Affaires",                    "Droit",                "L2", "S2"),
    ]

    created_courses = []
    for intitule, filiere, niveau, semestre in courses_data:
        c = db.query(Course).filter(Course.intitule == intitule).first()
        if not c:
            c = Course(intitule=intitule, filiere=filiere, niveau=niveau, semestre=semestre)
            db.add(c)
            db.flush()
        created_courses.append(c)

    # ── Activities ───────────────────────────────────────────────────────────
    if db.query(Activity).count() == 0:
        act_configs = [
            (0, 0, "creation",   2, 5),
            (0, 1, "creation",   3, 3),
            (1, 5, "creation",   1, 8),
            (2, 8, "mise_a_jour", 2, 4),
            (3, 3, "creation",   1, 6),
            (4, 4, "creation",   3, 2),
            (5, 6, "mise_a_jour", 1, 10),
            (6, 7, "creation",   2, 7),
            (7, 0, "mise_a_jour", 3, 3),
            (1, 1, "creation",   2, 5),
            (2, 2, "creation",   1, 8),
            (3, 9, "mise_a_jour", 2, 4),
        ]

        statuses = ["en_attente", "valide", "valide"]  # bias toward validated

        for teacher_idx, course_idx, type_act, niveau_comp, nb_seq in act_configs:
            if teacher_idx >= len(created_teachers) or course_idx >= len(created_courses):
                continue
            t = created_teachers[teacher_idx]
            c = created_courses[course_idx]
            vol = calculate_volume_horaire(type_act, niveau_comp, nb_seq)

            r = Resource(
                type=type_act,
                niveau_complexite=niveau_comp,
                course_id=c.id,
                teacher_id=t.id,
            )
            db.add(r)
            db.flush()

            a = Activity(
                type=type_act,
                resource_id=r.id,
                teacher_id=t.id,
                nb_sequences=nb_seq,
                volume_horaire_calcule=vol,
                academic_year_id=ay.id,
                annee_academique=ay.libelle,
                validation_status=random.choice(statuses),
            )
            db.add(a)

    db.commit()
    return {"message": "Données de démonstration créées avec succès"}
