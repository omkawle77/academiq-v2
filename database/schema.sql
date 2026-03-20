-- =============================================================
--  AcademIQ v2 — Schema for MySQL / PostgreSQL
--  For SQLite: schema auto-created via SQLAlchemy ORM
--  Run: mysql -u root -p academiq < schema.sql
--       psql -U postgres -d academiq -f schema.sql
-- =============================================================

CREATE TABLE IF NOT EXISTS students (
    id              VARCHAR(12)  PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    grade_level     VARCHAR(50),
    attendance_rate FLOAT        DEFAULT 0.0,
    study_hours     FLOAT        DEFAULT 0.0,
    learning_style  VARCHAR(50),
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subjects (
    id           INT          PRIMARY KEY AUTO_INCREMENT,
    student_id   VARCHAR(12)  NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    score        FLOAT        DEFAULT 0.0,
    grade        VARCHAR(2),
    gpa_points   FLOAT        DEFAULT 0.0,
    difficulty   VARCHAR(20)  DEFAULT 'medium',
    is_weak      BOOLEAN      DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS extracurriculars (
    id         INT         PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(12) NOT NULL,
    name       VARCHAR(100) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id                INT         PRIMARY KEY AUTO_INCREMENT,
    student_id        VARCHAR(12) NOT NULL UNIQUE,
    gpa               FLOAT       DEFAULT 0.0,
    performance_level VARCHAR(30),
    performance_label VARCHAR(30),
    performance_color VARCHAR(10),
    problems_detected TEXT,
    strengths         TEXT,
    weak_subjects     TEXT,
    advice_json       LONGTEXT,
    summary           TEXT,
    created_at        TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id         INT         PRIMARY KEY AUTO_INCREMENT,
    action     VARCHAR(50) NOT NULL,
    entity     VARCHAR(50),
    entity_id  VARCHAR(12),
    detail     TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
CREATE INDEX IF NOT EXISTS idx_analysis_level ON analysis_results(performance_level);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);