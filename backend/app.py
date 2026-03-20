"""
app.py — AcademIQ v2 Flask Application
REST API + GraphQL endpoint
Databases: SQLite | MySQL | PostgreSQL
"""

import os, sys, json, uuid, csv, io
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS

# ── ensure backend/ is on path ────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from database import db
import knowledge_base as kb

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
app.config.from_object(Config)
CORS(app)

db.init_app(app)

# ── import models AFTER db init ───────────────────────────────────────────────
with app.app_context():
    from models import Student, Subject, Extracurricular, AnalysisResult, AuditLog
    db.create_all()
    print(f"✅ Database ready [{Config.DB_TYPE.upper()}]: {Config.SQLALCHEMY_DATABASE_URI[:60]}…")

# ── GraphQL ───────────────────────────────────────────────────────────────────
try:
    from graphql_schema import schema as gql_schema
    GQL_AVAILABLE = True
except Exception as e:
    GQL_AVAILABLE = False
    print(f"⚠️  GraphQL not available: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def make_id():
    return str(uuid.uuid4())[:8].upper()

def log_action(action, entity=None, entity_id=None, detail=None):
    with app.app_context():
        try:
            entry = AuditLog(
                action=action, entity=entity, entity_id=entity_id,
                detail=detail, ip_address=request.remote_addr
            )
            db.session.add(entry)
            db.session.commit()
        except Exception:
            db.session.rollback()

def build_and_save_analysis(student, subjects_data, extra_list):
    """Run inference engine and persist AnalysisResult row."""
    analysis = kb.analyze_student({
        "name":               student.name,
        "grade_level":        student.grade_level,
        "attendance_rate":    student.attendance_rate,
        "study_hours_per_day":student.study_hours,
        "learning_style":     student.learning_style,
        "subjects":           subjects_data,
        "extracurriculars":   extra_list,
    })

    # Remove old analysis if exists
    if student.analysis:
        db.session.delete(student.analysis)
        db.session.flush()

    ar = AnalysisResult(
        student_id        = student.id,
        gpa               = analysis["gpa"],
        performance_level = analysis["performance_level"],
        performance_label = analysis["performance_label"],
        performance_color = analysis["performance_color"],
        problems_detected = json.dumps(analysis["problems_detected"]),
        strengths         = json.dumps(analysis["strengths"]),
        weak_subjects     = json.dumps(analysis["weak_subjects"]),
        advice_json       = json.dumps(analysis["advice"]),
        summary           = analysis["summary"],
    )
    db.session.add(ar)
    return analysis

# ─────────────────────────────────────────────────────────────────────────────
# FRONTEND
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("../frontend", path)

# ─────────────────────────────────────────────────────────────────────────────
# REST API — ANALYZE (stateless, no DB)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Instant analysis — no persistence."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload"}), 400
    result = kb.analyze_student(data)
    log_action("ANALYZE", detail=data.get("name", "unknown"))
    return jsonify({"success": True, "analysis": result})

# ─────────────────────────────────────────────────────────────────────────────
# REST API — STUDENTS CRUD
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/students", methods=["POST"])
def create_student():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400

    student = Student(
        id             = make_id(),
        name           = data["name"],
        grade_level    = data.get("grade_level"),
        attendance_rate= data.get("attendance_rate", 0),
        study_hours    = data.get("study_hours_per_day", 0),
        learning_style = data.get("learning_style"),
    )
    db.session.add(student)
    db.session.flush()

    # Subjects
    subjects_data = data.get("subjects", [])
    for s in subjects_data:
        sb = Subject(
            student_id   = student.id,
            subject_name = s.get("subject_name", ""),
            score        = s.get("score", 0),
            difficulty   = s.get("difficulty", "medium"),
        )
        db.session.add(sb)

    # Extracurriculars
    extra_list = data.get("extracurriculars", [])
    for e in extra_list:
        ec = Extracurricular(student_id=student.id, name=e)
        db.session.add(ec)

    # Analysis
    analysis = build_and_save_analysis(student, subjects_data, extra_list)

    # Update subject grades from analysis
    enriched = {s["subject_name"]: s for s in analysis.get("enriched_subjects", [])}
    for sub in student.subjects:
        if sub.subject_name in enriched:
            e = enriched[sub.subject_name]
            sub.grade      = e.get("grade")
            sub.gpa_points = e.get("gpa_points", 0)
            sub.is_weak    = e.get("is_weak", False)

    db.session.commit()
    log_action("CREATE", "student", student.id, student.name)

    return jsonify({"success": True, "student_id": student.id, "analysis": analysis}), 201


@app.route("/api/students", methods=["GET"])
def list_students():
    page     = request.args.get("page",  1,   type=int)
    per_page = request.args.get("limit", 20,  type=int)
    search   = request.args.get("search", "").strip()
    level    = request.args.get("level",  "").strip()

    q = Student.query
    if search:
        q = q.filter(Student.name.ilike(f"%{search}%"))
    if level:
        q = q.join(AnalysisResult).filter(AnalysisResult.performance_level == level)

    total   = q.count()
    students= q.order_by(Student.created_at.desc()) \
               .offset((page-1)*per_page).limit(per_page).all()

    return jsonify({
        "success":  True,
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "students": [{
            "id":               s.id,
            "name":             s.name,
            "grade_level":      s.grade_level,
            "attendance_rate":  s.attendance_rate,
            "study_hours":      s.study_hours,
            "created_at":       s.created_at.isoformat() if s.created_at else None,
            "gpa":              s.analysis.gpa if s.analysis else None,
            "performance_level":s.analysis.performance_level if s.analysis else None,
            "performance_label":s.analysis.performance_label if s.analysis else None,
            "performance_color":s.analysis.performance_color if s.analysis else None,
        } for s in students]
    })


@app.route("/api/students/<sid>", methods=["GET"])
def get_student(sid):
    student = Student.query.get_or_404(sid)
    log_action("READ", "student", sid)
    return jsonify({"success": True, "student": student.to_dict()})


@app.route("/api/students/<sid>", methods=["PUT"])
def update_student(sid):
    student = Student.query.get_or_404(sid)
    data    = request.get_json()

    student.name           = data.get("name",            student.name)
    student.grade_level    = data.get("grade_level",     student.grade_level)
    student.attendance_rate= data.get("attendance_rate", student.attendance_rate)
    student.study_hours    = data.get("study_hours_per_day", student.study_hours)
    student.learning_style = data.get("learning_style",  student.learning_style)
    student.updated_at     = datetime.utcnow()

    # Re-run analysis
    subjects_data = data.get("subjects", [s.to_dict() for s in student.subjects])
    extra_list    = data.get("extracurriculars", [e.name for e in student.extracurriculars])
    analysis = build_and_save_analysis(student, subjects_data, extra_list)

    db.session.commit()
    log_action("UPDATE", "student", sid)
    return jsonify({"success": True, "analysis": analysis})


@app.route("/api/students/<sid>", methods=["DELETE"])
def delete_student(sid):
    student = Student.query.get_or_404(sid)
    db.session.delete(student)
    db.session.commit()
    log_action("DELETE", "student", sid)
    return jsonify({"success": True, "deleted": sid})

# ─────────────────────────────────────────────────────────────────────────────
# REST API — BULK OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/students/bulk-analyze", methods=["POST"])
def bulk_analyze():
    """Analyze multiple students in one request (no persistence)."""
    payload = request.get_json()
    if not isinstance(payload, list):
        return jsonify({"error": "Expected a JSON array of students"}), 400
    results = [{"name": s.get("name"), "analysis": kb.analyze_student(s)} for s in payload]
    return jsonify({"success": True, "count": len(results), "results": results})

# ─────────────────────────────────────────────────────────────────────────────
# REST API — STATISTICS
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def get_stats():
    from sqlalchemy import func
    total = Student.query.count()
    avg_gpa = db.session.query(func.avg(AnalysisResult.gpa)).scalar() or 0
    avg_att = db.session.query(func.avg(Student.attendance_rate)).scalar() or 0

    level_counts = {}
    for lvl in ["excellent","good","average","below_average","critical"]:
        level_counts[lvl] = AnalysisResult.query.filter_by(performance_level=lvl).count()

    problems = {}
    for ar in AnalysisResult.query.all():
        for p in json.loads(ar.problems_detected or "[]"):
            problems[p] = problems.get(p, 0) + 1

    subject_avgs = db.session.query(
        Subject.subject_name,
        func.avg(Subject.score).label("avg_score"),
        func.count(Subject.id).label("count")
    ).group_by(Subject.subject_name).all()

    return jsonify({
        "success":           True,
        "total_students":    total,
        "avg_gpa":           round(float(avg_gpa), 2),
        "avg_attendance":    round(float(avg_att), 1),
        "performance_levels":level_counts,
        "problem_frequency": problems,
        "subject_averages":  [{"subject": r[0], "avg_score": round(float(r[1]),1), "count": r[2]}
                               for r in subject_avgs],
    })

# ─────────────────────────────────────────────────────────────────────────────
# REST API — EXPORT CSV
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    students = Student.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID","Name","Grade","Attendance%","StudyHrs","GPA","Level","Created"])
    for s in students:
        ar = s.analysis
        writer.writerow([
            s.id, s.name, s.grade_level or "",
            s.attendance_rate, s.study_hours,
            round(ar.gpa,2) if ar else "",
            ar.performance_label if ar else "",
            s.created_at.strftime("%Y-%m-%d") if s.created_at else "",
        ])
    log_action("EXPORT", "students", detail="CSV export")
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=academiq_students.csv"}
    )

# ─────────────────────────────────────────────────────────────────────────────
# REST API — AUDIT LOG
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/audit", methods=["GET"])
def get_audit():
    limit = request.args.get("limit", 50, type=int)
    logs  = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return jsonify({"success": True, "logs": [l.to_dict() for l in logs]})

# ─────────────────────────────────────────────────────────────────────────────
# GRAPHQL ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/graphql", methods=["GET","POST"])
def graphql():
    if not GQL_AVAILABLE:
        return jsonify({"error": "GraphQL not available. Run: pip install graphene"}), 503

    data    = request.get_json() or {}
    query   = data.get("query", "")
    variables = data.get("variables", {})

    result = gql_schema.execute(query, variable_values=variables)
    response = {"data": result.data}
    if result.errors:
        response["errors"] = [str(e) for e in result.errors]
    return jsonify(response)

# ─────────────────────────────────────────────────────────────────────────────
# DB INFO ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/db-info", methods=["GET"])
def db_info():
    return jsonify({
        "success": True,
        "db_type": Config.DB_TYPE,
        "tables": ["students","subjects","extracurriculars","analysis_results","audit_logs"],
        "graphql": GQL_AVAILABLE,
        "graphql_endpoint": "/api/graphql",
    })

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════╗
║   🎓 AcademIQ v2 — Backend                      ║
║   DB   : {Config.DB_TYPE.upper():<40}║
║   REST : http://localhost:{Config.FLASK_PORT}/api         ║
║   GQL  : http://localhost:{Config.FLASK_PORT}/api/graphql ║
║   UI   : http://localhost:{Config.FLASK_PORT}             ║
╚══════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host="0.0.0.0", port=Config.FLASK_PORT)