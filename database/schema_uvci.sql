-- =====================================================================
--  UVCI — GESTION DES HEURES DES ENSEIGNANTS
--  Script de création de la base de données (DDL)
-- ---------------------------------------------------------------------
--  SGBD cible      : PostgreSQL 14+
--  Encodage        : UTF-8
--  Projet          : Projet Collectif Tutoré — PCT25-26_DAS-N°11
--  Année           : 2025 – 2026
--  Version         : 1.0
-- ---------------------------------------------------------------------
--  Conventions de nommage :
--    - tables ......... pluriel, snake_case          (users, activities)
--    - clés primaires . pk_<table>
--    - clés étrangères  fk_<table>_<colonne>
--    - unicité ........ uq_<table>_<colonnes>
--    - contraintes CHECK ck_<table>_<colonne>
--    - index .......... ix_<table>_<colonne>
--
--  Le script est idempotent (DROP ... IF EXISTS) et transactionnel :
--  il s'exécute intégralement ou pas du tout.
--
--  Exécution :  psql -U <user> -d <base> -f schema_uvci.sql
-- =====================================================================

BEGIN;

SET client_encoding = 'UTF8';

-- ---------------------------------------------------------------------
-- 0. Nettoyage (ordre inverse des dépendances)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS activities          CASCADE;
DROP TABLE IF EXISTS resources           CASCADE;
DROP TABLE IF EXISTS coefficient_configs CASCADE;
DROP TABLE IF EXISTS quotas_statutaires  CASCADE;
DROP TABLE IF EXISTS academic_years      CASCADE;
DROP TABLE IF EXISTS courses             CASCADE;
DROP TABLE IF EXISTS teachers            CASCADE;
DROP TABLE IF EXISTS users               CASCADE;


-- =====================================================================
-- 1. UTILISATEURS (comptes d'authentification)
-- =====================================================================
CREATE TABLE users (
    id              INTEGER       GENERATED ALWAYS AS IDENTITY,
    email           VARCHAR(255)  NOT NULL,
    hashed_password VARCHAR(255)  NOT NULL,
    role            VARCHAR(20)   NOT NULL DEFAULT 'teacher',
    est_actif       BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT pk_users      PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_role  CHECK (role IN ('admin', 'secretary', 'teacher'))
);

CREATE INDEX ix_users_email ON users (email);

COMMENT ON TABLE  users                 IS 'Comptes d''authentification (admin, secrétaire, enseignant).';
COMMENT ON COLUMN users.hashed_password IS 'Mot de passe haché avec bcrypt — jamais stocké en clair.';
COMMENT ON COLUMN users.role            IS 'Rôle RBAC : admin | secretary | teacher.';
COMMENT ON COLUMN users.est_actif       IS 'Compte actif (TRUE) ou désactivé (FALSE) sans suppression.';


-- =====================================================================
-- 2. ENSEIGNANTS (profil métier, lié 1:1 à un compte utilisateur)
-- =====================================================================
CREATE TABLE teachers (
    id           INTEGER       GENERATED ALWAYS AS IDENTITY,
    nom          VARCHAR(100)  NOT NULL,
    prenom       VARCHAR(100)  NOT NULL,
    grade        VARCHAR(100)  NOT NULL,
    statut       VARCHAR(20)   NOT NULL,
    departement  VARCHAR(150)  NOT NULL,
    taux_horaire NUMERIC(8,2)  NOT NULL DEFAULT 0.00,
    email        VARCHAR(255)  NOT NULL,
    telephone    VARCHAR(30),
    user_id      INTEGER,

    CONSTRAINT pk_teachers             PRIMARY KEY (id),
    CONSTRAINT uq_teachers_email       UNIQUE (email),
    CONSTRAINT uq_teachers_user        UNIQUE (user_id),
    CONSTRAINT ck_teachers_statut      CHECK (statut IN ('Permanent', 'Vacataire')),
    CONSTRAINT ck_teachers_taux_horaire CHECK (taux_horaire >= 0),
    CONSTRAINT fk_teachers_user        FOREIGN KEY (user_id)
        REFERENCES users (id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX ix_teachers_user_id     ON teachers (user_id);
CREATE INDEX ix_teachers_departement ON teachers (departement);

COMMENT ON TABLE  teachers              IS 'Enseignants : profil métier rattaché à un compte users.';
COMMENT ON COLUMN teachers.statut       IS 'Statut administratif : Permanent | Vacataire.';
COMMENT ON COLUMN teachers.taux_horaire IS 'Taux horaire de rémunération (FCFA / heure).';
COMMENT ON COLUMN teachers.user_id      IS 'Compte d''authentification associé (NULL si non encore créé).';


-- =====================================================================
-- 3. COURS (catalogue pédagogique)
-- =====================================================================
CREATE TABLE courses (
    id         INTEGER       GENERATED ALWAYS AS IDENTITY,
    intitule   VARCHAR(255)  NOT NULL,
    filiere    VARCHAR(150)  NOT NULL,
    niveau     VARCHAR(10)   NOT NULL,
    semestre   VARCHAR(20)   NOT NULL,
    nb_heures  INTEGER,
    nb_credits INTEGER,

    CONSTRAINT pk_courses           PRIMARY KEY (id),
    CONSTRAINT ck_courses_niveau    CHECK (niveau IN ('L1', 'L2', 'L3', 'M1', 'M2')),
    CONSTRAINT ck_courses_nb_heures CHECK (nb_heures  IS NULL OR nb_heures  >= 0),
    CONSTRAINT ck_courses_credits   CHECK (nb_credits IS NULL OR nb_credits >= 0)
);

CREATE INDEX ix_courses_filiere ON courses (filiere);
CREATE INDEX ix_courses_niveau  ON courses (niveau);

COMMENT ON TABLE  courses        IS 'Catalogue des cours (UE) pour lesquels des ressources sont produites.';
COMMENT ON COLUMN courses.niveau IS 'Niveau académique : L1, L2, L3, M1, M2.';


-- =====================================================================
-- 4. ANNÉES ACADÉMIQUES
-- =====================================================================
CREATE TABLE academic_years (
    id         INTEGER      GENERATED ALWAYS AS IDENTITY,
    libelle    VARCHAR(20)  NOT NULL,
    date_debut DATE,
    date_fin   DATE,
    status     BOOLEAN      NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_academic_years      PRIMARY KEY (id),
    CONSTRAINT uq_academic_years_lib  UNIQUE (libelle),
    CONSTRAINT ck_academic_years_dates CHECK (
        date_debut IS NULL OR date_fin IS NULL OR date_fin >= date_debut
    )
);

-- Une seule année peut être active à la fois (index partiel unique).
CREATE UNIQUE INDEX uq_academic_years_active
    ON academic_years (status) WHERE status = TRUE;

COMMENT ON TABLE  academic_years        IS 'Années académiques de rattachement des activités.';
COMMENT ON COLUMN academic_years.libelle IS 'Libellé, ex. « 2025-2026 ».';
COMMENT ON COLUMN academic_years.status  IS 'TRUE = année courante active (une seule à la fois).';


-- =====================================================================
-- 5. RESSOURCES PÉDAGOGIQUES (combinaison enseignant / cours / type / niveau)
-- =====================================================================
CREATE TABLE resources (
    id               INTEGER      GENERATED ALWAYS AS IDENTITY,
    type             VARCHAR(30)  NOT NULL,
    niveau_complexite SMALLINT    NOT NULL DEFAULT 1,
    course_id        INTEGER      NOT NULL,
    teacher_id       INTEGER      NOT NULL,
    date_creation    TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT pk_resources          PRIMARY KEY (id),
    CONSTRAINT uq_resources_business UNIQUE (teacher_id, course_id, type, niveau_complexite),
    CONSTRAINT ck_resources_type     CHECK (type IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_resources_niveau   CHECK (niveau_complexite IN (1, 2, 3)),
    CONSTRAINT fk_resources_course   FOREIGN KEY (course_id)
        REFERENCES courses (id)  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_resources_teacher  FOREIGN KEY (teacher_id)
        REFERENCES teachers (id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX ix_resources_course_id  ON resources (course_id);
CREATE INDEX ix_resources_teacher_id ON resources (teacher_id);

COMMENT ON TABLE  resources                   IS 'Référentiel des combinaisons enseignant / cours / type d''activité / niveau.';
COMMENT ON COLUMN resources.type              IS 'Type d''activité associé à la ressource : creation | mise_a_jour.';
COMMENT ON COLUMN resources.niveau_complexite IS 'Niveau de complexité 1, 2 ou 3 — détermine le coefficient horaire.';


-- =====================================================================
-- 6. ACTIVITÉS (création / mise à jour d'une ressource → volume horaire)
-- =====================================================================
CREATE TABLE activities (
    id                    INTEGER      GENERATED ALWAYS AS IDENTITY,
    type                  VARCHAR(20)  NOT NULL,
    resource_id           INTEGER      NOT NULL,
    teacher_id            INTEGER      NOT NULL,
    nb_sequences          INTEGER      NOT NULL DEFAULT 1,
    volume_horaire_calcule NUMERIC(8,3) NOT NULL DEFAULT 0.000,
    academic_year_id      INTEGER,
    annee_academique      VARCHAR(20),
    validation_status     VARCHAR(20)  NOT NULL DEFAULT 'en_attente',
    validated_by          INTEGER,
    validated_at          TIMESTAMPTZ,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT pk_activities             PRIMARY KEY (id),
    CONSTRAINT ck_activities_type        CHECK (type IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_activities_status      CHECK (validation_status IN ('en_attente', 'valide', 'rejetee')),
    CONSTRAINT ck_activities_sequences   CHECK (nb_sequences > 0),
    CONSTRAINT ck_activities_volume      CHECK (volume_horaire_calcule >= 0),
    CONSTRAINT fk_activities_resource    FOREIGN KEY (resource_id)
        REFERENCES resources (id)       ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_activities_teacher     FOREIGN KEY (teacher_id)
        REFERENCES teachers (id)        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_activities_year        FOREIGN KEY (academic_year_id)
        REFERENCES academic_years (id)  ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_activities_validator   FOREIGN KEY (validated_by)
        REFERENCES users (id)           ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX ix_activities_resource_id ON activities (resource_id);
CREATE INDEX ix_activities_teacher_id  ON activities (teacher_id);
CREATE INDEX ix_activities_year_id     ON activities (academic_year_id);
CREATE INDEX ix_activities_status      ON activities (validation_status);

COMMENT ON TABLE  activities                        IS 'Actes pédagogiques générant un volume horaire (Vhtc = Ic × S).';
COMMENT ON COLUMN activities.type                   IS 'creation (coefficient plein) | mise_a_jour (demi-coefficient).';
COMMENT ON COLUMN activities.nb_sequences           IS 'Nombre de séquences (S) produites.';
COMMENT ON COLUMN activities.volume_horaire_calcule IS 'Volume horaire calculé Vhtc = Ic × S.';
COMMENT ON COLUMN activities.validation_status      IS 'Cycle de validation : en_attente | valide | rejetee.';


-- =====================================================================
-- 7. CONFIGURATION DES COEFFICIENTS (barème officiel, paramétrable admin)
-- =====================================================================
CREATE TABLE coefficient_configs (
    id                INTEGER      GENERATED ALWAYS AS IDENTITY,
    niveau_complexite SMALLINT     NOT NULL,
    type_activite     VARCHAR(20)  NOT NULL,
    coefficient       NUMERIC(6,3) NOT NULL,

    CONSTRAINT pk_coefficient_configs    PRIMARY KEY (id),
    CONSTRAINT uq_coeff_niveau_type      UNIQUE (niveau_complexite, type_activite),
    CONSTRAINT ck_coeff_niveau           CHECK (niveau_complexite IN (1, 2, 3)),
    CONSTRAINT ck_coeff_type             CHECK (type_activite IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_coeff_value            CHECK (coefficient >= 0)
);

COMMENT ON TABLE  coefficient_configs IS 'Barème officiel UVCI : (niveau, type) → coefficient Ic, paramétrable par l''admin.';


-- =====================================================================
-- 8. QUOTAS STATUTAIRES (quota horaire annuel par grade et statut)
-- =====================================================================
CREATE TABLE quotas_statutaires (
    id           INTEGER      GENERATED ALWAYS AS IDENTITY,
    grade        VARCHAR(100) NOT NULL,
    statut       VARCHAR(20)  NOT NULL,
    quota_heures NUMERIC(8,2) NOT NULL,

    CONSTRAINT pk_quotas_statutaires  PRIMARY KEY (id),
    CONSTRAINT uq_quota_grade_statut  UNIQUE (grade, statut),
    CONSTRAINT ck_quota_statut        CHECK (statut IN ('Permanent', 'Vacataire')),
    CONSTRAINT ck_quota_value         CHECK (quota_heures >= 0)
);

COMMENT ON TABLE  quotas_statutaires IS 'Quota horaire annuel dû par grade et statut, paramétrable par l''admin.';


-- =====================================================================
-- 9. DONNÉES DE RÉFÉRENCE (barème officiel + quotas par défaut)
-- =====================================================================

-- Barème officiel UVCI : Vhtc = Ic × S ; mise à jour = ½ × création.
INSERT INTO coefficient_configs (niveau_complexite, type_activite, coefficient) VALUES
    (1, 'creation',    0.400),
    (1, 'mise_a_jour', 0.200),
    (2, 'creation',    0.750),
    (2, 'mise_a_jour', 0.375),
    (3, 'creation',    1.500),
    (3, 'mise_a_jour', 0.750);

-- Quotas statutaires par défaut : 192 h (permanents), 96 h (vacataires).
INSERT INTO quotas_statutaires (grade, statut, quota_heures) VALUES
    ('Professeur',            'Permanent', 192.00),
    ('Maître de Conférences', 'Permanent', 192.00),
    ('Maître-Assistant',      'Permanent', 192.00),
    ('Assistant',             'Permanent', 192.00),
    ('Professeur',            'Vacataire',  96.00),
    ('Maître de Conférences', 'Vacataire',  96.00),
    ('Maître-Assistant',      'Vacataire',  96.00),
    ('Assistant',             'Vacataire',  96.00);

COMMIT;

-- =====================================================================
-- FIN DU SCRIPT
-- =====================================================================
