from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    secretary = "secretary"
    teacher = "teacher"


class GradeType(str, Enum):
    assistant = "Assistant"
    maitre_assistant = "Maître-Assistant"
    maitre_conferences = "Maître de Conférences"
    professeur = "Professeur"


class TeacherStatus(str, Enum):
    permanent = "Permanent"
    vacataire = "Vacataire"


class ActivityType(str, Enum):
    creation = "creation"
    mise_a_jour = "mise_a_jour"


class ValidationStatus(str, Enum):
    en_attente = "en_attente"
    valide = "valide"
    rejetee = "rejetee"


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole = UserRole.teacher
    nom: Optional[str] = None
    prenom: Optional[str] = None


class UserManage(BaseModel):
    """Schema used by Admin to create/update a user account."""
    email: str
    password: Optional[str] = None
    role: UserRole = UserRole.teacher
    est_actif: bool = True


class UserLogin(BaseModel):
    email: str
    password: str


class UserFaceVerify(BaseModel):
    email: str
    face_image_base64: str


class UserOut(BaseModel):
    id: int
    email: str
    role: str
    est_actif: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Keep "User" as an alias so existing imports of `User` from schemas still work
class User(UserOut):
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    email: str
    teacher_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Teacher schemas
# ---------------------------------------------------------------------------

class TeacherBase(BaseModel):
    nom: str
    prenom: str
    grade: str
    statut: str
    departement: str
    taux_horaire: float
    email: str
    telephone: Optional[str] = None


class TeacherCreate(TeacherBase):
    user_id: Optional[int] = None


class TeacherUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    grade: Optional[str] = None
    statut: Optional[str] = None
    departement: Optional[str] = None
    taux_horaire: Optional[float] = None
    email: Optional[str] = None
    telephone: Optional[str] = None


class Teacher(TeacherBase):
    id: int
    user_id: Optional[int] = None
    volume_horaire_total: Optional[float] = 0.0

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Course schemas
# ---------------------------------------------------------------------------

class CourseBase(BaseModel):
    intitule: str
    filiere: str
    niveau: str
    semestre: str
    nb_heures: Optional[int] = None
    nb_credits: Optional[int] = None


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Resource schemas
# ---------------------------------------------------------------------------

class ResourceBase(BaseModel):
    type: str
    niveau_complexite: int
    course_id: int
    teacher_id: int


class ResourceCreate(ResourceBase):
    pass


class Resource(ResourceBase):
    id: int
    date_creation: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Academic Year schemas
# ---------------------------------------------------------------------------

class AcademicYearBase(BaseModel):
    libelle: str
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    status: bool = False


class AcademicYearCreate(AcademicYearBase):
    pass


class AcademicYear(AcademicYearBase):
    id: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Activity schemas
# ---------------------------------------------------------------------------

class ActivityBase(BaseModel):
    type: str
    resource_id: int
    teacher_id: int
    nb_sequences: int
    academic_year_id: Optional[int] = None


class ActivityCreate(BaseModel):
    teacher_id: int
    course_id: int
    type_activite: str
    niveau_complexite: int
    nb_sequences: int
    academic_year_id: Optional[int] = None


# Legacy submit schema kept for backward compatibility
class ActivitySubmit(BaseModel):
    type: str
    teacher_id: int
    course_id: int
    niveau_complexite: int
    nb_sequences: int
    academic_year_id: int = 1


class ActivityOut(BaseModel):
    id: int
    teacher_id: int
    course_id: int
    type_activite: str
    niveau_complexite: int
    nb_sequences: int
    volume_horaire_calcule: float
    validation_status: str
    created_at: Optional[datetime] = None
    teacher_nom: Optional[str] = None
    teacher_prenom: Optional[str] = None
    course_intitule: Optional[str] = None
    annee_academique: Optional[str] = None

    class Config:
        from_attributes = True


# Legacy Activity schema kept so existing imports don't break
class Activity(BaseModel):
    id: int
    type: str
    resource_id: int
    teacher_id: int
    nb_sequences: int
    volume_horaire_calcule: float
    academic_year_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ActivityValidate(BaseModel):
    validation_status: str  # "valide", "rejetee", "en_attente"


# ---------------------------------------------------------------------------
# Coefficient & Quota schemas
# ---------------------------------------------------------------------------

class CoefficientConfigOut(BaseModel):
    id: int
    niveau_complexite: int
    type_activite: str
    coefficient: float

    class Config:
        from_attributes = True


class CoefficientConfigUpdate(BaseModel):
    niveau_complexite: int
    type_activite: str
    coefficient: float


class QuotaStatutaireOut(BaseModel):
    id: int
    grade: str
    statut: str
    quota_heures: float

    class Config:
        from_attributes = True


class QuotaStatutaireUpdate(BaseModel):
    grade: str
    statut: str
    quota_heures: float
