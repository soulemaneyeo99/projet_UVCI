from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserOut, UserManage
from app.core.security import require_admin, get_password_hash

router = APIRouter()


@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Liste tous les comptes utilisateurs (Admin seulement)."""
    return db.query(User).order_by(User.id).all()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserManage,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Créer un nouveau compte utilisateur (Admin seulement)."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà")

    if not user_in.password:
        raise HTTPException(status_code=400, detail="Le mot de passe est requis à la création")

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        est_actif=user_in.est_actif,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserManage,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Modifier un compte utilisateur (Admin seulement)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user.email = user_in.email
    user.role = user_in.role
    user.est_actif = user_in.est_actif
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)

    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/desactiver", response_model=UserOut)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Désactiver un compte utilisateur (Admin seulement)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas désactiver votre propre compte")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user.est_actif = False
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/activer", response_model=UserOut)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Réactiver un compte utilisateur (Admin seulement)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user.est_actif = True
    db.commit()
    db.refresh(user)
    return user
