from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.models import Activity, Teacher, Course, Resource, AcademicYear
from app.schemas.schemas import ActivityCreate, ActivityOut, ActivityValidate
from app.services.calculator import calculate_volume_horaire

router = APIRouter()


def _build_activity_out(act: Activity, db: Session) -> ActivityOut:
    """Build an ActivityOut response from an Activity ORM row."""
    teacher = db.query(Teacher).filter(Teacher.id == act.teacher_id).first()
    resource = db.query(Resource).filter(Resource.id == act.resource_id).first()

    niveau_complexite = 1
    course_id = 0
    course_intitule = None

    if resource:
        niveau_complexite = resource.niveau_complexite
        course_id = resource.course_id
        course = db.query(Course).filter(Course.id == resource.course_id).first()
        if course:
            course_intitule = course.intitule

    return ActivityOut(
        id=act.id,
        teacher_id=act.teacher_id,
        course_id=course_id,
        type_activite=act.type,
        niveau_complexite=niveau_complexite,
        nb_sequences=act.nb_sequences,
        volume_horaire_calcule=act.volume_horaire_calcule,
        validation_status=act.validation_status or "en_attente",
        created_at=act.created_at,
        teacher_nom=teacher.nom if teacher else None,
        teacher_prenom=teacher.prenom if teacher else None,
        course_intitule=course_intitule,
        annee_academique=act.annee_academique,
    )


@router.post("/", response_model=ActivityOut)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == activity.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")

    course = db.query(Course).filter(Course.id == activity.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Cours non trouvé")

    volume = calculate_volume_horaire(
        activity.type_activite,
        activity.niveau_complexite,
        activity.nb_sequences,
    )

    annee_label = None
    if activity.academic_year_id:
        ay = db.query(AcademicYear).filter(AcademicYear.id == activity.academic_year_id).first()
        if ay:
            annee_label = ay.libelle

    # Create the linked Resource row first
    resource = Resource(
        type=activity.type_activite,
        niveau_complexite=activity.niveau_complexite,
        course_id=activity.course_id,
        teacher_id=activity.teacher_id,
    )
    db.add(resource)
    db.flush()

    db_activity = Activity(
        type=activity.type_activite,
        resource_id=resource.id,
        teacher_id=activity.teacher_id,
        nb_sequences=activity.nb_sequences,
        volume_horaire_calcule=volume,
        academic_year_id=activity.academic_year_id,
        annee_academique=annee_label,
        validation_status="en_attente",
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)

    return ActivityOut(
        id=db_activity.id,
        teacher_id=db_activity.teacher_id,
        course_id=activity.course_id,
        type_activite=db_activity.type,
        niveau_complexite=activity.niveau_complexite,
        nb_sequences=db_activity.nb_sequences,
        volume_horaire_calcule=db_activity.volume_horaire_calcule,
        validation_status=db_activity.validation_status,
        created_at=db_activity.created_at,
        teacher_nom=teacher.nom,
        teacher_prenom=teacher.prenom,
        course_intitule=course.intitule,
        annee_academique=annee_label,
    )


@router.get("/", response_model=List[ActivityOut])
def list_activities(
    skip: int = 0,
    limit: int = 50,
    teacher_id: Optional[int] = None,
    validation_status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Activity)
    if teacher_id:
        query = query.filter(Activity.teacher_id == teacher_id)
    if validation_status:
        query = query.filter(Activity.validation_status == validation_status)

    activities = query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()
    return [_build_activity_out(act, db) for act in activities]


@router.get("/teacher/{teacher_id}", response_model=List[ActivityOut])
def get_teacher_activities(teacher_id: int, db: Session = Depends(get_db)):
    activities = (
        db.query(Activity)
        .filter(Activity.teacher_id == teacher_id)
        .order_by(Activity.created_at.desc())
        .all()
    )
    return [_build_activity_out(act, db) for act in activities]


@router.get("/volume/{teacher_id}")
def get_teacher_volume(teacher_id: int, db: Session = Depends(get_db)):
    activities = db.query(Activity).filter(Activity.teacher_id == teacher_id).all()
    total = sum(a.volume_horaire_calcule for a in activities)
    validated = sum(
        a.volume_horaire_calcule for a in activities if a.validation_status == "valide"
    )
    return {
        "teacher_id": teacher_id,
        "volume_total": round(total, 2),
        "volume_valide": round(validated, 2),
        "nb_activites": len(activities),
    }


@router.put("/{activity_id}/validate")
def validate_activity(
    activity_id: int, data: ActivityValidate, db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")

    activity.validation_status = data.validation_status
    if data.validation_status == "valide":
        activity.validated_at = datetime.utcnow()
    db.commit()
    return {"message": "Statut mis à jour", "status": data.validation_status}
