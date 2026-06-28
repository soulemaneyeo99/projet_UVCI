
--  Exécution :  sqlite3 sql_app.db < schema_uvci_sqlite.sql
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- 0. Nettoyage (ordre inverse des dépendances)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS coefficient_configs;
DROP TABLE IF EXISTS quotas_statutaires;
DROP TABLE IF EXISTS academic_years;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS users;


-- =====================================================================
-- 1. USERS — Comptes d'authentification
-- =====================================================================
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,  -- haché bcrypt, jamais en clair
    role            VARCHAR(20)  NOT NULL DEFAULT 'teacher',
    est_actif       BOOLEAN      NOT NULL DEFAULT 1,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_role  CHECK (role IN ('admin', 'secretary', 'teacher'))
);

CREATE UNIQUE INDEX ix_users_email ON users (email);


-- =====================================================================
-- 2. TEACHERS — Profil métier de l'enseignant (lié 1:1 à un compte users)
-- =====================================================================
CREATE TABLE teachers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nom          VARCHAR(100) NOT NULL,
    prenom       VARCHAR(100) NOT NULL,
    grade        VARCHAR(100) NOT NULL,
    statut       VARCHAR(20)  NOT NULL,
    departement  VARCHAR(150) NOT NULL,
    taux_horaire REAL         NOT NULL DEFAULT 0.0,
    email        VARCHAR(255) NOT NULL,
    telephone    VARCHAR(30),
    user_id      INTEGER,

    CONSTRAINT uq_teachers_email       UNIQUE (email),
    CONSTRAINT uq_teachers_user        UNIQUE (user_id),   -- relation 1:1 compte ↔ enseignant
    CONSTRAINT ck_teachers_statut      CHECK (statut IN ('Permanent', 'Vacataire')),
    CONSTRAINT ck_teachers_taux        CHECK (taux_horaire >= 0),
    CONSTRAINT fk_teachers_user        FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_teachers_user_id ON teachers (user_id);


-- =====================================================================
-- 3. COURSES — Catalogue pédagogique
-- =====================================================================
CREATE TABLE courses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    intitule   VARCHAR(255) NOT NULL,
    filiere    VARCHAR(150) NOT NULL,
    niveau     VARCHAR(10)  NOT NULL,
    semestre   VARCHAR(20)  NOT NULL,
    nb_heures  INTEGER,
    nb_credits INTEGER,

    CONSTRAINT ck_courses_niveau    CHECK (niveau IN ('L1', 'L2', 'L3', 'M1', 'M2')),
    CONSTRAINT ck_courses_nb_heures CHECK (nb_heures  IS NULL OR nb_heures  >= 0),
    CONSTRAINT ck_courses_credits   CHECK (nb_credits IS NULL OR nb_credits >= 0)
);


-- =====================================================================
-- 4. ACADEMIC_YEARS — Années académiques
-- =====================================================================
CREATE TABLE academic_years (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle    VARCHAR(20) NOT NULL,
    date_debut VARCHAR(20),               -- dates stockées en texte (ISO « 2025-09-01 »)
    date_fin   VARCHAR(20),
    status     BOOLEAN     NOT NULL DEFAULT 0,  -- 1 = année active

    CONSTRAINT uq_academic_years_lib UNIQUE (libelle)
);


-- =====================================================================
-- 5. RESOURCES — Ressources pédagogiques (enseignant × cours × type × niveau)
-- =====================================================================
CREATE TABLE resources (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    type              VARCHAR(30) NOT NULL,   -- type d'activité associé : creation | mise_a_jour
    niveau_complexite INTEGER     NOT NULL DEFAULT 1,
    course_id         INTEGER     NOT NULL,
    teacher_id        INTEGER     NOT NULL,
    date_creation     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Clé métier : une ressource = une combinaison unique (enseignant × cours × type × niveau).
    CONSTRAINT uq_resources_business UNIQUE (teacher_id, course_id, type, niveau_complexite),
    CONSTRAINT ck_resources_type    CHECK (type IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_resources_niveau  CHECK (niveau_complexite IN (1, 2, 3)),
    CONSTRAINT fk_resources_course  FOREIGN KEY (course_id)
        REFERENCES courses (id)  ON DELETE RESTRICT,
    CONSTRAINT fk_resources_teacher FOREIGN KEY (teacher_id)
        REFERENCES teachers (id) ON DELETE RESTRICT
);

CREATE INDEX ix_resources_course_id  ON resources (course_id);
CREATE INDEX ix_resources_teacher_id ON resources (teacher_id);


-- =====================================================================
-- 6. ACTIVITIES — Activités et volumes horaires calculés (Vhtc = Ic × S)
-- =====================================================================
CREATE TABLE activities (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    type                   VARCHAR(20) NOT NULL,
    resource_id            INTEGER     NOT NULL,
    teacher_id             INTEGER     NOT NULL,
    nb_sequences           INTEGER     NOT NULL DEFAULT 1,
    volume_horaire_calcule REAL        NOT NULL DEFAULT 0.0,
    academic_year_id       INTEGER,
    annee_academique       VARCHAR(20),
    validation_status      VARCHAR(20) NOT NULL DEFAULT 'en_attente',
    validated_by           INTEGER,
    validated_at           DATETIME,
    created_at             DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_activities_type      CHECK (type IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_activities_status    CHECK (validation_status IN ('en_attente', 'valide', 'rejetee')),
    CONSTRAINT ck_activities_sequences CHECK (nb_sequences > 0),
    CONSTRAINT ck_activities_volume    CHECK (volume_horaire_calcule >= 0),
    CONSTRAINT fk_activities_resource  FOREIGN KEY (resource_id)
        REFERENCES resources (id)      ON DELETE CASCADE,
    CONSTRAINT fk_activities_teacher   FOREIGN KEY (teacher_id)
        REFERENCES teachers (id)       ON DELETE RESTRICT,
    CONSTRAINT fk_activities_year      FOREIGN KEY (academic_year_id)
        REFERENCES academic_years (id) ON DELETE SET NULL,
    CONSTRAINT fk_activities_validator FOREIGN KEY (validated_by)
        REFERENCES users (id)          ON DELETE SET NULL
);

CREATE INDEX ix_activities_resource_id ON activities (resource_id);
CREATE INDEX ix_activities_teacher_id  ON activities (teacher_id);
CREATE INDEX ix_activities_year_id     ON activities (academic_year_id);
CREATE INDEX ix_activities_status      ON activities (validation_status);


-- =====================================================================
-- 7. COEFFICIENT_CONFIGS — Barème officiel UVCI (paramétrable admin)
-- =====================================================================
CREATE TABLE coefficient_configs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    niveau_complexite INTEGER     NOT NULL,
    type_activite     VARCHAR(20) NOT NULL,
    coefficient       REAL        NOT NULL,

    CONSTRAINT uq_coeff_niveau_type UNIQUE (niveau_complexite, type_activite),
    CONSTRAINT ck_coeff_niveau      CHECK (niveau_complexite IN (1, 2, 3)),
    CONSTRAINT ck_coeff_type        CHECK (type_activite IN ('creation', 'mise_a_jour')),
    CONSTRAINT ck_coeff_value       CHECK (coefficient >= 0)
);


-- =====================================================================
-- 8. QUOTAS_STATUTAIRES — Quotas horaires annuels (paramétrable admin)
-- =====================================================================
CREATE TABLE quotas_statutaires (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    grade        VARCHAR(100) NOT NULL,
    statut       VARCHAR(20)  NOT NULL,
    quota_heures REAL         NOT NULL,

    CONSTRAINT uq_quota_grade_statut UNIQUE (grade, statut),
    CONSTRAINT ck_quota_statut       CHECK (statut IN ('Permanent', 'Vacataire')),
    CONSTRAINT ck_quota_value        CHECK (quota_heures >= 0)
);


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
    ('Professeur',            'Permanent', 192.0),
    ('Maître de Conférences', 'Permanent', 192.0),
    ('Maître-Assistant',      'Permanent', 192.0),
    ('Assistant',             'Permanent', 192.0),
    ('Professeur',            'Vacataire',  96.0),
    ('Maître de Conférences', 'Vacataire',  96.0),
    ('Maître-Assistant',      'Vacataire',  96.0),
    ('Assistant',             'Vacataire',  96.0);

-- =====================================================================
-- FIN DU SCRIPT
-- =====================================================================
