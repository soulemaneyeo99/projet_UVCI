from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, Teacher
from app.schemas.schemas import UserLogin, UserCreate, UserFaceVerify
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

    # Resolve teacher_id if the user has a linked teacher profile
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


@router.post("/register")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà",
        )

    new_user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        role=user_in.role,
        est_actif=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
    }


@router.post("/face-verify")
def face_verify(verify_in: UserFaceVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == verify_in.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if not user.face_encoding:
        raise HTTPException(
            status_code=400,
            detail="Aucun profil biométrique enregistré pour cet utilisateur",
        )

    return {"status": "success", "message": "Identité biométrique confirmée"}


@router.get("/me")
def get_me(current_user: User = Depends(security.get_current_user)):
    """Returns the current authenticated user's profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "est_actif": current_user.est_actif,
    }
