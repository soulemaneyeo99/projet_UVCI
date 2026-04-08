import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.endpoints import auth, teachers, courses, activities, exports, dashboard, academic_years, users, config
from app.db.database import engine, SessionLocal, get_db
from app.models import models


def run_seed():
    """Auto-seed the DB on startup so Render/prod envs have demo data."""
    db = SessionLocal()
    try:
        from app.models.models import User
        if db.query(User).count() == 0:
            from app.models.models import Teacher, Course, AcademicYear, Activity, Resource
            from app.core.security import get_password_hash
            from app.services.calculator import calculate_volume_horaire
            import random
            random.seed(42)

            def upsert_user(email, password, role):
                u = db.query(User).filter(User.email == email).first()
                if not u:
                    u = User(email=email, hashed_password=get_password_hash(password), role=role, est_actif=True)
                    db.add(u)
                    db.flush()
                return u

            # 1. Exactement 3 users principaux (Admin, Secretary, Teacher base)
            admin_u = upsert_user("admin@uvci.ci", "admin123", "admin")
            sec_u = upsert_user("secretaire@uvci.ci", "secretaire123", "secretary")
            # The first teacher will use this user

            # 2. Exactement 3 Années Académiques
            ay1 = AcademicYear(libelle="2023-2024", date_debut="2023-09-01", date_fin="2024-07-31", status=False)
            ay2 = AcademicYear(libelle="2024-2025", date_debut="2024-09-01", date_fin="2025-07-31", status=False)
            ay3 = AcademicYear(libelle="2025-2026", date_debut="2025-09-01", date_fin="2026-07-31", status=True)
            db.add_all([ay1, ay2, ay3])
            db.flush()

            # 3. Exactement 5 Enseignants
            teachers_data = [
                ("Kouame","Jean-Pierre","Professeur","Permanent","Informatique",5000.0,"jkouame@uvci.ci"),
                ("Bamba","Aminata","Maître de Conférences","Permanent","Mathematiques",4500.0,"abamba@uvci.ci"),
                ("Ouattara","Ibrahim","Maître-Assistant","Permanent","Sciences Economiques",3500.0,"iouattara@uvci.ci"),
                ("Koffi","Marie","Assistant","Vacataire","Informatique",2500.0,"mkoffi@uvci.ci"),
                ("Diabate","Seydou","Maître-Assistant","Permanent","Droit",3500.0,"sdiabate@uvci.ci"),
            ]
            created_teachers = []
            for idx, (nom, prenom, grade, statut, dept, taux, email) in enumerate(teachers_data):
                if idx == 0:
                    u = upsert_user(email, "teacher123", "teacher")
                else:
                    u = upsert_user(email, "teacher123", "teacher")
                t = Teacher(nom=nom, prenom=prenom, grade=grade, statut=statut,
                            departement=dept, taux_horaire=taux, email=email, user_id=u.id)
                db.add(t)
                db.flush()
                created_teachers.append(t)

            # 4. Exactement 10 Cours
            courses_data = [
                ("Programmation Python","Informatique","L1","S1"),
                ("Algorithmes et Structures de Donnees","Informatique","L2","S1"),
                ("Base de Donnees","Informatique","L2","S2"),
                ("Developpement Web","Informatique","L3","S1"),
                ("Intelligence Artificielle","Informatique","M1","S1"),
                ("Analyse Mathematique","Mathematiques","L1","S1"),
                ("Algebre Lineaire","Mathematiques","L1","S2"),
                ("Statistiques","Mathematiques","L2","S1"),
                ("Economie Generale","Sciences Economiques","L1","S1"),
                ("Droit des Affaires","Droit","L2","S2"),
            ]
            created_courses = []
            for intitule, filiere, niveau, semestre in courses_data:
                c = Course(intitule=intitule, filiere=filiere, niveau=niveau, semestre=semestre)
                db.add(c)
                db.flush()
                created_courses.append(c)

            # 5. Exactement 20 Ressources et 30 Activités
            act_configs = [
                # teacher_idx, course_idx, type, niveau, nb_seq
                (0,0,"creation",2,5), (0,1,"creation",3,3), (1,5,"creation",1,8),
                (2,8,"mise_a_jour",2,4), (3,3,"creation",1,6), (4,4,"creation",3,2),
                (0,6,"mise_a_jour",1,10), (1,7,"creation",2,7), (2,0,"mise_a_jour",3,3),
                (1,1,"creation",2,5), (2,2,"creation",1,8), (3,9,"mise_a_jour",2,4),
                (0,2,"creation",1,4), (1,3,"mise_a_jour",2,2), (2,4,"creation",3,3),
                (3,5,"mise_a_jour",1,5), (4,6,"creation",2,6), (0,7,"mise_a_jour",3,2),
                (1,8,"creation",1,3), (2,9,"mise_a_jour",2,5)
            ]  # 20 resources
            
            created_resources = []
            for t_idx, c_idx, t_act, n_comp, n_seq in act_configs:
                t = created_teachers[t_idx % 5]
                c = created_courses[c_idx % 10]
                r = Resource(type=t_act, niveau_complexite=n_comp, course_id=c.id, teacher_id=t.id)
                db.add(r)
                db.flush()
                created_resources.append((r, t, n_seq))

            # Let's create 30 activities from these 20 resources (some resources have multiple activities)
            statuses = ["en_attente","valide","valide","rejetee","valide"]
            count_act = 0
            while count_act < 30:
                for r, t, n_seq in created_resources:
                    if count_act >= 30:
                        break
                    vol = calculate_volume_horaire(r.type, r.niveau_complexite, n_seq)
                    a = Activity(type=r.type, resource_id=r.id, teacher_id=t.id, nb_sequences=n_seq,
                                 volume_horaire_calcule=vol, academic_year_id=ay3.id, annee_academique=ay3.libelle,
                                 validation_status=statuses[count_act % len(statuses)])
                    if a.validation_status == "valide":
                        a.validated_by = admin_u.id
                    db.add(a)
                    count_act += 1

            db.commit()
            print("Base de donnees initialisee avec les donnees de demonstration")
    except Exception as e:
        db.rollback()
        print(f"Seed warning: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    run_seed()
    yield


app = FastAPI(
    title="GestionHeures UVCI API",
    version="1.0.0",
    description="API de gestion des heures pedagogiques - Universite Virtuelle de Cote d'Ivoire",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,           prefix="/auth",           tags=["Authentication"])
app.include_router(users.router,          prefix="/users",          tags=["Users"])
app.include_router(config.router,         prefix="/config",         tags=["Config"])
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


@app.post("/seed", tags=["Dev"])
def seed_data(db: Session = Depends(get_db)):
    run_seed()
    return {"message": "Seed execute"}
