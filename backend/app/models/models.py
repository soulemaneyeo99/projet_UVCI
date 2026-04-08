from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="teacher")  # admin, secretary, teacher
    est_actif = Column(Boolean, default=True)
    face_encoding = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    teacher = relationship("Teacher", back_populates="user", uselist=False)


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    statut = Column(String, nullable=False)
    departement = Column(String, nullable=False)
    taux_horaire = Column(Float, default=0.0)
    email = Column(String, unique=True, nullable=False)
    telephone = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="teacher")
    resources = relationship("Resource", back_populates="teacher")
    activities = relationship("Activity", back_populates="teacher")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    intitule = Column(String, nullable=False)
    filiere = Column(String, nullable=False)
    niveau = Column(String, nullable=False)  # L1, L2, L3, M1, M2
    semestre = Column(String, nullable=False)
    nb_heures = Column(Integer, nullable=True)
    nb_credits = Column(Integer, nullable=True)

    resources = relationship("Resource", back_populates="course")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # video, quiz, activite_interactive, document
    niveau_complexite = Column(Integer, default=1)  # 1, 2, 3
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    date_creation = Column(DateTime, server_default=func.now())

    course = relationship("Course", back_populates="resources")
    teacher = relationship("Teacher", back_populates="resources")
    activities = relationship("Activity", back_populates="resource")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # creation, mise_a_jour
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    nb_sequences = Column(Integer, default=1)
    volume_horaire_calcule = Column(Float, default=0.0)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=True)
    annee_academique = Column(String, nullable=True)
    validation_status = Column(String, default="en_attente")  # en_attente, valide, rejetee
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    resource = relationship("Resource", back_populates="activities")
    teacher = relationship("Teacher", back_populates="activities")
    academic_year = relationship("AcademicYear", back_populates="activities")


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    libelle = Column(String, nullable=False)
    date_debut = Column(String, nullable=True)
    date_fin = Column(String, nullable=True)
    status = Column(Boolean, default=False)  # True = année active

    activities = relationship("Activity", back_populates="academic_year")


class CoefficientConfig(Base):
    """Taux horaire par niveau de complexité et type d'activité — paramétrable par l'Admin."""
    __tablename__ = "coefficient_configs"

    id = Column(Integer, primary_key=True, index=True)
    niveau_complexite = Column(Integer, nullable=False)  # 1, 2, 3
    type_activite = Column(String, nullable=False)       # creation, mise_a_jour
    coefficient = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("niveau_complexite", "type_activite", name="uq_coeff_niveau_type"),
    )


class QuotaStatutaire(Base):
    """Quota horaire annuel par grade et statut — paramétrable par l'Admin."""
    __tablename__ = "quotas_statutaires"

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(String, nullable=False)
    statut = Column(String, nullable=False)   # Permanent, Vacataire
    quota_heures = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("grade", "statut", name="uq_quota_grade_statut"),
    )
