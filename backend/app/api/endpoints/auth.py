from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, Teacher
from app.schemas.schemas import UserLogin
from app.core import security

router = APIRouter()


@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()

    if not user or not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    if not user.est_actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte a été désactivé. Contactez l'administrateur.",
        )

    teacher = db.query(Teacher).filter(Teacher.user_id == user.id).first()

    access_token = security.create_access_token(
        user_id=user.id,
        role=user.role,
        email=user.email,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "email": user.email,
        "teacher_id": teacher.id if teacher else None,
    }


@router.get("/me")
def get_me(current_user: User = Depends(security.get_current_user)):
    """Returns the current authenticated user's profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "est_actif": current_user.est_actif,
    }
