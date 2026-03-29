from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.models import Teacher, Course, Activity, Resource

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_teachers = db.query(Teacher).count()
    total_courses = db.query(Course).count()

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_activities = db.query(Activity).filter(Activity.created_at >= month_start).all()
    heures_ce_mois = sum(a.volume_horaire_calcule for a in monthly_activities)

    all_activities = db.query(Activity).all()
    volume_total = sum(a.volume_horaire_calcule for a in all_activities)

    en_attente = db.query(Activity).filter(Activity.validation_status == "en_attente").count()

    active_teacher_ids = db.query(Activity.teacher_id).distinct().all()
    enseignants_actifs = len(active_teacher_ids)

    # Recent activities (last 10)
    recent_acts = (
        db.query(Activity).order_by(Activity.created_at.desc()).limit(10).all()
    )
    recent_activities = []
    for act in recent_acts:
        teacher = db.query(Teacher).filter(Teacher.id == act.teacher_id).first()
        resource = db.query(Resource).filter(Resource.id == act.resource_id).first()
        course_intitule = None
        if resource:
            from app.models.models import Course as CourseModel
            course = db.query(CourseModel).filter(CourseModel.id == resource.course_id).first()
            if course:
                course_intitule = course.intitule
        recent_activities.append({
            "id": act.id,
            "teacher_nom": f"{teacher.prenom} {teacher.nom}" if teacher else "Inconnu",
            "teacher_departement": teacher.departement if teacher else "",
            "course_intitule": course_intitule or "Cours non défini",
            "type": act.type,
            "volume_horaire": act.volume_horaire_calcule,
            "validation_status": act.validation_status or "en_attente",
            "created_at": act.created_at.isoformat() if act.created_at else None,
        })

    # Top 5 teachers by total volume
    teachers = db.query(Teacher).all()
    teacher_volumes = []
    for t in teachers:
        acts = db.query(Activity).filter(Activity.teacher_id == t.id).all()
        vol = sum(a.volume_horaire_calcule for a in acts)
        teacher_volumes.append({
            "id": t.id,
            "nom": t.nom,
            "prenom": t.prenom,
            "departement": t.departement,
            "grade": t.grade,
            "volume_total": round(vol, 1),
            "nb_activites": len(acts),
        })
    teacher_volumes.sort(key=lambda x: x["volume_total"], reverse=True)
    top_teachers = teacher_volumes[:5]

    # Volume aggregated by department
    dept_volumes: dict = {}
    for t in teachers:
        dept = t.departement or "Autre"
        acts = db.query(Activity).filter(Activity.teacher_id == t.id).all()
        vol = sum(a.volume_horaire_calcule for a in acts)
        dept_volumes[dept] = dept_volumes.get(dept, 0) + vol
    dept_chart = [{"departement": k, "volume": round(v, 1)} for k, v in dept_volumes.items()]

    # Monthly volume for the last 6 months
    month_names = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
                   "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    monthly_data = []
    for i in range(5, -1, -1):
        # Step back i full months from the 1st of the current month
        month_date = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        m_start = month_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1, day=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1, day=1)

        m_acts = db.query(Activity).filter(
            Activity.created_at >= m_start,
            Activity.created_at < m_end,
        ).all()
        m_vol = sum(a.volume_horaire_calcule for a in m_acts)
        monthly_data.append({
            "mois": month_names[m_start.month - 1],
            "volume": round(m_vol, 1),
        })

    return {
        "total_teachers": total_teachers,
        "total_courses": total_courses,
        "heures_ce_mois": round(heures_ce_mois, 1),
        "volume_total": round(volume_total, 1),
        "en_attente": en_attente,
        "enseignants_actifs": enseignants_actifs,
        "recent_activities": recent_activities,
        "top_teachers": top_teachers,
        "dept_chart": dept_chart,
        "monthly_data": monthly_data,
    }


@router.get("/teacher-stats/{teacher_id}")
def get_teacher_stats(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        return {"error": "Teacher not found"}

    activities = db.query(Activity).filter(Activity.teacher_id == teacher_id).all()
    volume_total = sum(a.volume_horaire_calcule for a in activities)

    SEUIL_STATUTAIRE = 192.0
    heures_complementaires = max(0.0, volume_total - SEUIL_STATUTAIRE)

    now = datetime.utcnow()
    if now.month >= 9:
        sem_start = now.replace(month=9, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        sem_start = now.replace(month=2, day=1, hour=0, minute=0, second=0, microsecond=0)

    sem_activities = [a for a in activities if a.created_at and a.created_at >= sem_start]
    activites_semestre = len(sem_activities)

    charge_pct = min(100, int((volume_total / SEUIL_STATUTAIRE) * 100)) if SEUIL_STATUTAIRE > 0 else 0

    month_names = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
                   "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    monthly_data = []
    for i in range(5, -1, -1):
        month_date = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        m_start = month_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1, day=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1, day=1)

        m_acts = [a for a in activities if a.created_at and m_start <= a.created_at < m_end]
        m_vol = sum(a.volume_horaire_calcule for a in m_acts)
        monthly_data.append({
            "mois": month_names[m_start.month - 1],
            "volume": round(m_vol, 1),
        })

    return {
        "teacher": {
            "id": teacher.id,
            "nom": teacher.nom,
            "prenom": teacher.prenom,
            "grade": teacher.grade,
            "departement": teacher.departement,
            "email": teacher.email,
            "statut": teacher.statut,
            "taux_horaire": teacher.taux_horaire,
        },
        "volume_total": round(volume_total, 1),
        "heures_complementaires": round(heures_complementaires, 1),
        "activites_semestre": activites_semestre,
        "charge_pct": charge_pct,
        "seuil_statutaire": SEUIL_STATUTAIRE,
        "monthly_data": monthly_data,
    }
