from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import AcademicYear
from app.schemas.schemas import AcademicYearCreate, AcademicYear as AcademicYearSchema

router = APIRouter()


@router.get("/", response_model=List[AcademicYearSchema])
def list_academic_years(db: Session = Depends(get_db)):
    return db.query(AcademicYear).order_by(AcademicYear.id.desc()).all()


@router.post("/", response_model=AcademicYearSchema)
def create_academic_year(ay: AcademicYearCreate, db: Session = Depends(get_db)):
    db_ay = AcademicYear(**ay.dict())
    db.add(db_ay)
    db.commit()
    db.refresh(db_ay)
    return db_ay


@router.get("/{ay_id}", response_model=AcademicYearSchema)
def get_academic_year(ay_id: int, db: Session = Depends(get_db)):
    ay = db.query(AcademicYear).filter(AcademicYear.id == ay_id).first()
    if not ay:
        raise HTTPException(status_code=404, detail="Année académique non trouvée")
    return ay


@router.put("/{ay_id}", response_model=AcademicYearSchema)
def update_academic_year(
    ay_id: int, ay_data: AcademicYearCreate, db: Session = Depends(get_db)
):
    ay = db.query(AcademicYear).filter(AcademicYear.id == ay_id).first()
    if not ay:
        raise HTTPException(status_code=404, detail="Année académique non trouvée")
    for field, value in ay_data.dict().items():
        setattr(ay, field, value)
    db.commit()
    db.refresh(ay)
    return ay


@router.delete("/{ay_id}")
def delete_academic_year(ay_id: int, db: Session = Depends(get_db)):
    ay = db.query(AcademicYear).filter(AcademicYear.id == ay_id).first()
    if not ay:
        raise HTTPException(status_code=404, detail="Année académique non trouvée")
    db.delete(ay)
    db.commit()
    return {"message": "Année académique supprimée avec succès"}
