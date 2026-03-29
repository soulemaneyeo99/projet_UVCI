from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.models import Teacher, Activity
from app.schemas.schemas import TeacherCreate, TeacherUpdate, Teacher as TeacherSchema

router = APIRouter()


def _teacher_with_volume(teacher: Teacher, db: Session) -> TeacherSchema:
    acts = db.query(Activity).filter(Activity.teacher_id == teacher.id).all()
    vol = round(sum(a.volume_horaire_calcule for a in acts), 1)
    return TeacherSchema(
        id=teacher.id,
        nom=teacher.nom,
        prenom=teacher.prenom,
        grade=teacher.grade,
        statut=teacher.statut,
        departement=teacher.departement,
        taux_horaire=teacher.taux_horaire,
        email=teacher.email,
        telephone=teacher.telephone,
        user_id=teacher.user_id,
        volume_horaire_total=vol,
    )


@router.get("/", response_model=List[TeacherSchema])
def list_teachers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    grade: Optional[str] = None,
    statut: Optional[str] = None,
    departement: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Teacher)
    if search:
        query = query.filter(
            (Teacher.nom.ilike(f"%{search}%"))
            | (Teacher.prenom.ilike(f"%{search}%"))
            | (Teacher.email.ilike(f"%{search}%"))
        )
    if grade:
        query = query.filter(Teacher.grade == grade)
    if statut:
        query = query.filter(Teacher.statut == statut)
    if departement:
        query = query.filter(Teacher.departement == departement)

    teachers = query.offset(skip).limit(limit).all()
    return [_teacher_with_volume(t, db) for t in teachers]


@router.post("/", response_model=TeacherSchema)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    existing = db.query(Teacher).filter(Teacher.email == teacher.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un enseignant avec cet email existe déjà")

    db_teacher = Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return _teacher_with_volume(db_teacher, db)


@router.get("/{teacher_id}", response_model=TeacherSchema)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")
    return _teacher_with_volume(teacher, db)


@router.put("/{teacher_id}", response_model=TeacherSchema)
def update_teacher(
    teacher_id: int, teacher_data: TeacherUpdate, db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")

    for field, value in teacher_data.dict(exclude_unset=True).items():
        setattr(teacher, field, value)

    db.commit()
    db.refresh(teacher)
    return _teacher_with_volume(teacher, db)


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")
    db.delete(teacher)
    db.commit()
    return {"message": "Enseignant supprimé avec succès"}
