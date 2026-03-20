"""
graphql_schema.py — GraphQL Schema
Exposes Student data + Analysis via /api/graphql
"""

import graphene
from graphene import ObjectType, String, Float, Boolean, Int, List, Field


class SubjectType(ObjectType):
    subject_name = String()
    score        = Float()
    grade        = String()
    gpa_points   = Float()
    difficulty   = String()
    is_weak      = Boolean()


class AdviceType(ObjectType):
    key          = String()
    title        = String()
    icon         = String()
    priority     = String()
    description  = String()
    action_steps = List(String)


class AnalysisType(ObjectType):
    gpa               = Float()
    performance_level = String()
    performance_label = String()
    performance_color = String()
    problems_detected = List(String)
    strengths         = List(String)
    weak_subjects     = List(String)
    advice            = List(AdviceType)
    summary           = String()


class StudentType(ObjectType):
    id               = String()
    name             = String()
    grade_level      = String()
    attendance_rate  = Float()
    study_hours      = Float()
    learning_style   = String()
    subjects         = List(SubjectType)
    extracurriculars = List(String)
    analysis         = Field(AnalysisType)
    created_at       = String()


class StatsType(ObjectType):
    total_students      = Int()
    avg_gpa             = Float()
    avg_attendance      = Float()
    excellent_count     = Int()
    good_count          = Int()
    average_count       = Int()
    below_average_count = Int()
    critical_count      = Int()
    most_common_problem = String()


class Query(ObjectType):
    students     = List(StudentType, limit=Int(default_value=50), offset=Int(default_value=0))
    student      = Field(StudentType, id=String(required=True))
    stats        = Field(StatsType)
    search       = List(StudentType, name=String(), performance_level=String())

    @staticmethod
    def resolve_students(root, info, limit, offset):
        from models import Student
        rows = Student.query.order_by(Student.created_at.desc()).limit(limit).offset(offset).all()
        return [_student_to_gql(r) for r in rows]

    @staticmethod
    def resolve_student(root, info, id):
        from models import Student
        row = Student.query.get(id)
        return _student_to_gql(row) if row else None

    @staticmethod
    def resolve_stats(root, info):
        from models import Student, AnalysisResult
        import json
        total   = Student.query.count()
        avg_gpa = db_avg(AnalysisResult, AnalysisResult.gpa)
        avg_att = db_avg(Student, Student.attendance_rate)
        counts  = {}
        for lvl in ["excellent", "good", "average", "below_average", "critical"]:
            counts[lvl] = AnalysisResult.query.filter_by(performance_level=lvl).count()

        problems: dict = {}
        for ar in AnalysisResult.query.all():
            for p in json.loads(ar.problems_detected or "[]"):
                problems[p] = problems.get(p, 0) + 1
        mcp = max(problems.items(), key=lambda x: x[1])[0] if problems else "none"

        return StatsType(
            total_students      = total,
            avg_gpa             = round(avg_gpa, 2) if avg_gpa else 0.0,
            avg_attendance      = round(avg_att, 2) if avg_att else 0.0,
            excellent_count     = counts["excellent"],
            good_count          = counts["good"],
            average_count       = counts["average"],
            below_average_count = counts["below_average"],
            critical_count      = counts["critical"],
            most_common_problem = mcp,
        )

    @staticmethod
    def resolve_search(root, info, name=None, performance_level=None):
        from models import Student, AnalysisResult
        q = Student.query
        if name:
            q = q.filter(Student.name.ilike(f"%{name}%"))
        if performance_level:
            q = q.join(AnalysisResult).filter(
                AnalysisResult.performance_level == performance_level
            )
        return [_student_to_gql(r) for r in q.limit(50).all()]


def db_avg(model, col):
    from database import db
    from sqlalchemy import func
    result = db.session.query(func.avg(col)).scalar()
    return float(result) if result else 0.0


def _student_to_gql(row):
    if not row:
        return None
    d = row.to_dict()
    analysis = d.get("analysis") or {}
    advice_raw = analysis.get("advice", [])
    advice_objs = [
        AdviceType(
            key=a.get("key", ""),
            title=a.get("title", ""),
            icon=a.get("icon", ""),
            priority=a.get("priority", ""),
            description=a.get("description", ""),
            action_steps=a.get("action_steps", []),
        ) for a in advice_raw
    ]
    analysis_obj = AnalysisType(
        gpa=analysis.get("gpa", 0),
        performance_level=analysis.get("performance_level", ""),
        performance_label=analysis.get("performance_label", ""),
        performance_color=analysis.get("performance_color", ""),
        problems_detected=analysis.get("problems_detected", []),
        strengths=analysis.get("strengths", []),
        weak_subjects=analysis.get("weak_subjects", []),
        advice=advice_objs,
        summary=analysis.get("summary", ""),
    ) if analysis else None

    subjects_objs = [
        SubjectType(**s) for s in d.get("subjects", [])
    ]

    return StudentType(
        id=d["id"],
        name=d["name"],
        grade_level=d.get("grade_level"),
        attendance_rate=d.get("attendance_rate"),
        study_hours=d.get("study_hours"),
        learning_style=d.get("learning_style"),
        subjects=subjects_objs,
        extracurriculars=d.get("extracurriculars", []),
        analysis=analysis_obj,
        created_at=d.get("created_at"),
    )


schema = graphene.Schema(query=Query)