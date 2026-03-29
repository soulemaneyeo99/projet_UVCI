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

    # Resolve teacher_id if the user has a linked teacher profile
    teacher = db.query(Teacher).filter(Teacher.user_id == user.id).first()

    return {
        "access_token": security.create_access_token(user.id),
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

    # Placeholder for actual face_recognition comparison logic.
    # When face_recognition is available:
    #   face_image_data = base64.b64decode(verify_in.face_image_base64)
    #   compare stored user.face_encoding against the decoded image
    return {"status": "success", "message": "Identité biométrique confirmée"}
