"""
models.py — SQLAlchemy ORM Models
Compatible with SQLite, MySQL, PostgreSQL
"""

from datetime import datetime
from database import db


class Student(db.Model):
    __tablename__ = "students"

    id             = db.Column(db.String(12),  primary_key=True)
    name           = db.Column(db.String(120),  nullable=False)
    grade_level    = db.Column(db.String(50),   nullable=True)
    attendance_rate= db.Column(db.Float,        default=0.0)
    study_hours    = db.Column(db.Float,        default=0.0)
    learning_style = db.Column(db.String(50),   nullable=True)
    created_at     = db.Column(db.DateTime,     default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime,     default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subjects        = db.relationship("Subject",       back_populates="student", cascade="all, delete-orphan")
    extracurriculars= db.relationship("Extracurricular",back_populates="student", cascade="all, delete-orphan")
    analysis        = db.relationship("AnalysisResult", back_populates="student",
                                      uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":             self.id,
            "name":           self.name,
            "grade_level":    self.grade_level,
            "attendance_rate":self.attendance_rate,
            "study_hours":    self.study_hours,
            "learning_style": self.learning_style,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
            "subjects":       [s.to_dict() for s in self.subjects],
            "extracurriculars":[e.name for e in self.extracurriculars],
            "analysis":       self.analysis.to_dict() if self.analysis else None,
        }


class Subject(db.Model):
    __tablename__ = "subjects"

    id           = db.Column(db.Integer,    primary_key=True, autoincrement=True)
    student_id   = db.Column(db.String(12), db.ForeignKey("students.id"), nullable=False)
    subject_name = db.Column(db.String(100),nullable=False)
    score        = db.Column(db.Float,      default=0.0)
    grade        = db.Column(db.String(2),  nullable=True)
    gpa_points   = db.Column(db.Float,      default=0.0)
    difficulty   = db.Column(db.String(20), default="medium")
    is_weak      = db.Column(db.Boolean,    default=False)

    student = db.relationship("Student", back_populates="subjects")

    def to_dict(self):
        return {
            "subject_name": self.subject_name,
            "score":        self.score,
            "grade":        self.grade,
            "gpa_points":   self.gpa_points,
            "difficulty":   self.difficulty,
            "is_weak":      self.is_weak,
        }


class Extracurricular(db.Model):
    __tablename__ = "extracurriculars"

    id         = db.Column(db.Integer,    primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(12), db.ForeignKey("students.id"), nullable=False)
    name       = db.Column(db.String(100),nullable=False)

    student = db.relationship("Student", back_populates="extracurriculars")


class AnalysisResult(db.Model):
    __tablename__ = "analysis_results"

    id                = db.Column(db.Integer,    primary_key=True, autoincrement=True)
    student_id        = db.Column(db.String(12), db.ForeignKey("students.id"), nullable=False, unique=True)
    gpa               = db.Column(db.Float,      default=0.0)
    performance_level = db.Column(db.String(30), nullable=True)
    performance_label = db.Column(db.String(30), nullable=True)
    performance_color = db.Column(db.String(10), nullable=True)
    problems_detected = db.Column(db.Text,       nullable=True)   # JSON string
    strengths         = db.Column(db.Text,       nullable=True)   # JSON string
    weak_subjects     = db.Column(db.Text,       nullable=True)   # JSON string
    advice_json       = db.Column(db.Text,       nullable=True)   # Full advice JSON
    summary           = db.Column(db.Text,       nullable=True)
    created_at        = db.Column(db.DateTime,   default=datetime.utcnow)

    student = db.relationship("Student", back_populates="analysis")

    def to_dict(self):
        import json
        return {
            "gpa":               self.gpa,
            "performance_level": self.performance_level,
            "performance_label": self.performance_label,
            "performance_color": self.performance_color,
            "problems_detected": json.loads(self.problems_detected or "[]"),
            "strengths":         json.loads(self.strengths or "[]"),
            "weak_subjects":     json.loads(self.weak_subjects or "[]"),
            "advice":            json.loads(self.advice_json or "[]"),
            "summary":           self.summary,
        }


class AuditLog(db.Model):
    """Audit trail for every API action."""
    __tablename__ = "audit_logs"

    id         = db.Column(db.Integer,    primary_key=True, autoincrement=True)
    action     = db.Column(db.String(50), nullable=False)   # CREATE | READ | DELETE | ANALYZE
    entity     = db.Column(db.String(50), nullable=True)    # student | analysis
    entity_id  = db.Column(db.String(12), nullable=True)
    detail     = db.Column(db.Text,       nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime,   default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "action":     self.action,
            "entity":     self.entity,
            "entity_id":  self.entity_id,
            "detail":     self.detail,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }