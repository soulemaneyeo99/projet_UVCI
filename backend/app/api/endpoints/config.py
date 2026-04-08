from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import CoefficientConfig, QuotaStatutaire
from app.schemas.schemas import CoefficientConfigOut, CoefficientConfigUpdate, QuotaStatutaireOut, QuotaStatutaireUpdate
from app.core.security import require_admin, require_authenticated

router = APIRouter()


# ---------------------------------------------------------------------------
# Coefficients
# ---------------------------------------------------------------------------

@router.get("/coefficients", response_model=List[CoefficientConfigOut])
def get_coefficients(
    db: Session = Depends(get_db),
    _=Depends(require_authenticated),
):
    """Lecture des coefficients horaires (tous les utilisateurs authentifiés)."""
    return db.query(CoefficientConfig).order_by(
        CoefficientConfig.niveau_complexite, CoefficientConfig.type_activite
    ).all()


@router.put("/coefficients", response_model=List[CoefficientConfigOut])
def update_coefficients(
    updates: List[CoefficientConfigUpdate],
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Modifier les coefficients horaires (Admin seulement)."""
    for upd in updates:
        config = db.query(CoefficientConfig).filter(
            CoefficientConfig.niveau_complexite == upd.niveau_complexite,
            CoefficientConfig.type_activite == upd.type_activite,
        ).first()

        if config:
            config.coefficient = upd.coefficient
        else:
            config = CoefficientConfig(
                niveau_complexite=upd.niveau_complexite,
                type_activite=upd.type_activite,
                coefficient=upd.coefficient,
            )
            db.add(config)

    db.commit()
    return db.query(CoefficientConfig).order_by(
        CoefficientConfig.niveau_complexite, CoefficientConfig.type_activite
    ).all()


# ---------------------------------------------------------------------------
# Quotas statutaires
# ---------------------------------------------------------------------------

@router.get("/quotas", response_model=List[QuotaStatutaireOut])
def get_quotas(
    db: Session = Depends(get_db),
    _=Depends(require_authenticated),
):
    """Lecture des quotas statutaires par grade (tous les utilisateurs authentifiés)."""
    return db.query(QuotaStatutaire).order_by(QuotaStatutaire.grade, QuotaStatutaire.statut).all()


@router.put("/quotas", response_model=List[QuotaStatutaireOut])
def update_quotas(
    updates: List[QuotaStatutaireUpdate],
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Modifier les quotas statutaires (Admin seulement)."""
    for upd in updates:
        quota = db.query(QuotaStatutaire).filter(
            QuotaStatutaire.grade == upd.grade,
            QuotaStatutaire.statut == upd.statut,
        ).first()

        if quota:
            quota.quota_heures = upd.quota_heures
        else:
            quota = QuotaStatutaire(
                grade=upd.grade,
                statut=upd.statut,
                quota_heures=upd.quota_heures,
            )
            db.add(quota)

    db.commit()
    return db.query(QuotaStatutaire).order_by(QuotaStatutaire.grade, QuotaStatutaire.statut).all()
