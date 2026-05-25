from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.models.models import Teacher, Course, Activity, Resource, User, QuotaStatutaire
from app.core.security import require_admin_or_secretary, get_current_user

router = APIRouter()


MONTH_NAMES_FR = [
    "Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
    "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc",
]


def _month_offset(d: datetime, months_back: int) -> datetime:
    """Retourne le 1er du mois situé `months_back` mois avant `d` (arithmétique calendaire propre)."""
    y, m = d.year, d.month - months_back
    while m <= 0:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return datetime(y, m, 1)


def _build_monthly_series(activities, now: datetime, nb_months: int = 6) -> list:
    """Construit la série mensuelle des volumes horaires sur les `nb_months` derniers mois (inclus le mois courant)."""
    series = []
    for i in range(nb_months - 1, -1, -1):
        m_start = _month_offset(now, i)
        m_end = _month_offset(now, i - 1)
        vol = sum(
            a.volume_horaire_calcule
            for a in activities
            if a.created_at and m_start <= a.created_at < m_end
        )
        series.append({
            "mois": MONTH_NAMES_FR[m_start.month - 1],
            "volume": round(vol, 1),
        })
    return series


# Quota statutaire par défaut si la table QuotaStatutaire ne contient pas
# la combinaison (grade, statut) demandée.
DEFAULT_QUOTA_HEURES = 192.0


def _resolve_quota(teacher: Teacher, db: Session) -> float:
    """Retourne le quota annuel applicable pour un enseignant.

    Source : table `QuotaStatutaire` (paramétrable via PUT /config/quotas).
    Fallback : 192h (norme académique standard).
    """
    if not teacher.grade or not teacher.statut:
        return DEFAULT_QUOTA_HEURES
    row = (
        db.query(QuotaStatutaire)
        .filter(
            QuotaStatutaire.grade == teacher.grade,
            QuotaStatutaire.statut == teacher.statut,
        )
        .first()
    )
    return row.quota_heures if row else DEFAULT_QUOTA_HEURES


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_secretary),
):
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
            course = db.query(Course).filter(Course.id == resource.course_id).first()
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

    # Volume mensuel sur les 6 derniers mois
    monthly_data = _build_monthly_series(all_activities, now)

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
def get_teacher_stats(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")

    if current_user.role == "teacher" and teacher.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez consulter que vos propres statistiques",
        )

    activities = db.query(Activity).filter(Activity.teacher_id == teacher_id).all()
    volume_total = sum(a.volume_horaire_calcule for a in activities)

    seuil_statutaire = _resolve_quota(teacher, db)
    heures_complementaires = max(0.0, volume_total - seuil_statutaire)

    now = datetime.utcnow()
    if now.month >= 9:
        sem_start = now.replace(month=9, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        sem_start = now.replace(month=2, day=1, hour=0, minute=0, second=0, microsecond=0)

    sem_activities = [a for a in activities if a.created_at and a.created_at >= sem_start]
    activites_semestre = len(sem_activities)

    charge_pct = min(100, int((volume_total / seuil_statutaire) * 100)) if seuil_statutaire > 0 else 0

    monthly_data = _build_monthly_series(activities, now)

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
        "seuil_statutaire": seuil_statutaire,
        "monthly_data": monthly_data,
    }
