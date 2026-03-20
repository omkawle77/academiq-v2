# 🎓 AcademIQ v2 — Student Academic Performance Advisor

> AI-Powered Academic Analysis · Multi-Database Support · REST + GraphQL API · Brutalist Editorial UI

---

## 📌 Overview

**AcademIQ v2** is a full-stack web application that analyzes student academic performance using artificial intelligence techniques — specifically **Semantic Networks** and **Knowledge Frames**. Students input their subject scores, attendance, study habits, and learning style, and the system generates a personalized, prioritized action plan.

Built with **Python Flask** on the backend and a custom **HTML/CSS/JS** single-page frontend.

---

## 🖥️ Live Demo

Run locally at: `http://localhost:5000`

| Page | Description |
|------|-------------|
| **Home** | Landing page with feature overview |
| **Assess** | Student profile input form |
| **Results** | AI-generated performance report |
| **Records** | Database of all saved students |
| **Stats** | Analytics dashboard with Chart.js charts |
| **GraphQL** | Interactive API query explorer |

---

## 📁 Project Structure

```
academiq_v2/
├── .env                          ← Database and app configuration
├── README.md
├── setup.sh                      ← Auto-setup script
│
├── backend/
│   ├── app.py                    ← Flask app — REST API + GraphQL
│   ├── config.py                 ← Multi-database configuration
│   ├── database.py               ← SQLAlchemy instance
│   ├── models.py                 ← ORM models: Student, Subject, AnalysisResult, AuditLog
│   ├── knowledge_base.py         ← AI engine: Semantic Nets + Knowledge Frames
│   ├── graphql_schema.py         ← GraphQL schema using Graphene
│   └── requirements.txt          ← Python dependencies
│
├── frontend/
│   ├── index.html                ← Single-page app (6 sections, all JS embedded)
│   ├── css/
│   │   └── style.css             ← Brutalist editorial design system
│   └── js/
│       ├── api.js                ← All fetch() API calls
│       ├── charts.js             ← Chart.js visualizations
│       └── main.js               ← App logic and routing
│
└── database/
    ├── schema.sql                ← MySQL / PostgreSQL DDL
    └── seed.sql                  ← Sample student data
```

---

## 🚀 Quick Start

### Requirements

- Python 3.11 or higher
- pip

### Step 1 — Install Dependencies

```bash
cd academiq_v2/backend
pip install flask flask-cors flask-sqlalchemy graphene python-dotenv PyMySQL
```

### Step 2 — Run the Server

```bash
python app.py
```

### Step 3 — Open Browser

```
http://localhost:5000
```

---

## 🗄️ Database Configuration

The app supports three databases. Set `DB_TYPE` in the `.env` file.

### SQLite (Default — Zero Setup)

```env
DB_TYPE=sqlite
```

No installation needed. Database file is created automatically at `database/academiq.db`.

### MySQL

```env
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DATABASE=academiq
```

```bash
mysql -u root -p -e "CREATE DATABASE academiq;"
mysql -u root -p academiq < database/schema.sql
```

### PostgreSQL

```env
DB_TYPE=postgresql
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=yourpassword
PG_DATABASE=academiq
```

```bash
psql -U postgres -c "CREATE DATABASE academiq;"
psql -U postgres -d academiq -f database/schema.sql
```

---

## 🌐 REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Stateless analysis — no database save |
| POST | `/api/students` | Create and save student record |
| GET | `/api/students` | List all students with pagination and search |
| GET | `/api/students/:id` | Get full student record by ID |
| PUT | `/api/students/:id` | Update student and re-run analysis |
| DELETE | `/api/students/:id` | Delete student record permanently |
| POST | `/api/students/bulk-analyze` | Analyze multiple students at once |
| GET | `/api/stats` | Aggregated system statistics |
| GET | `/api/export/csv` | Download all students as CSV file |
| GET | `/api/audit` | Audit log of all API actions |
| GET/POST | `/api/graphql` | GraphQL endpoint |
| GET | `/api/db-info` | Current database type and schema info |

### Example — Analyze a Student

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Santos",
    "grade_level": "Grade 11",
    "attendance_rate": 85,
    "study_hours_per_day": 3,
    "learning_style": "visual",
    "subjects": [
      {"subject_name": "Mathematics", "score": 72, "difficulty": "hard"},
      {"subject_name": "English", "score": 88, "difficulty": "medium"},
      {"subject_name": "Science", "score": 65, "difficulty": "medium"}
    ],
    "extracurriculars": ["Sports", "Coding Club"]
  }'
```

### Example Response

```json
{
  "success": true,
  "analysis": {
    "gpa": 2.68,
    "performance_level": "average",
    "performance_label": "Average",
    "performance_color": "#eab308",
    "problems_detected": ["weak_subjects", "low_study_hours"],
    "strengths": ["English"],
    "advice": [
      {
        "title": "Build Study Schedule",
        "priority": "high",
        "description": "A consistent schedule dramatically improves retention.",
        "action_steps": [
          "Dedicate fixed daily slots for each subject.",
          "Use Pomodoro: 25 min study, 5 min break.",
          "Review notes within 24 hours of each class.",
          "Plan harder subjects for peak energy hours."
        ]
      }
    ],
    "summary": "Maria, your 2.68 GPA shows real potential. Focused work in Mathematics and Science will make a big difference."
  }
}
```

---

## 🔮 GraphQL API

Endpoint: `POST /api/graphql`

### Get All Students

```graphql
{
  students(limit: 10) {
    id
    name
    gradeLevel
    analysis {
      gpa
      performanceLabel
    }
  }
}
```

### Get System Statistics

```graphql
{
  stats {
    totalStudents
    avgGpa
    avgAttendance
    excellentCount
    criticalCount
    mostCommonProblem
  }
}
```

### Search by Name

```graphql
{
  search(name: "Maria") {
    id
    name
    analysis {
      gpa
      performanceLabel
      summary
    }
  }
}
```

### Get Single Student

```graphql
{
  student(id: "A1B2C3D4") {
    id
    name
    gradeLevel
    attendanceRate
    subjects {
      subjectName
      score
      grade
    }
    analysis {
      gpa
      performanceLabel
      summary
      advice {
        title
        priority
        description
      }
    }
  }
}
```

---

## 🧠 AI Techniques

### 1. Knowledge Frames

Structured data representations that model student profiles:

- **StudentFrame** — slots for name, grade, attendance, study hours, learning style
- **SubjectFrame** — slots for subject name, score, grade, difficulty level, weakness flag
- **PerformanceLevelFrame** — 5 levels: Excellent, Good, Average, Below Average, Critical

Each frame has default values, constraints, and inference procedures.

### 2. Semantic Network

A graph of interconnected knowledge nodes:

**Nodes:**
- 5 Performance Level nodes
- 5 Problem nodes: `low_gpa`, `poor_attendance`, `weak_subjects`, `low_study_hours`, `no_extracurricular`
- 12 Strategy nodes: Study Schedule, Active Recall, Spaced Repetition, SMART Goals, etc.

**Typed Edges (18+):**
- `is_resolved_by` — problem → strategy
- `has_risk` — behavior → problem
- `requires` — strategy → prerequisite
- `should_consider` — level → strategy
- `should_practice` — subject type → technique

### 3. Inference Engine

The `analyze_student()` function in `knowledge_base.py`:

1. Populates frames with student data
2. Detects problems by traversing semantic net edges
3. Identifies strengths from high-scoring subjects
4. Traverses `is_resolved_by` edges to find relevant strategies
5. Ranks advice by priority: Critical → High → Medium → Low
6. Generates a personalized summary string

---

## 🗄️ Database Schema

| Table | Key Columns |
|-------|-------------|
| `students` | id, name, grade_level, attendance_rate, study_hours, learning_style |
| `subjects` | id, student_id (FK), subject_name, score, grade, gpa_points, difficulty, is_weak |
| `extracurriculars` | id, student_id (FK), name |
| `analysis_results` | id, student_id (FK), gpa, performance_level, problems_detected, strengths, advice_json |
| `audit_logs` | id, action, entity, entity_id, detail, ip_address, created_at |

---

## 🎨 Design System

The frontend uses a **Brutalist Editorial** design aesthetic:

| Token | Value |
|-------|-------|
| Background | `#f5f2eb` (cream) |
| Ink | `#111111` (near black) |
| Accent | `#e84141` (coral red) |
| Teal | `#0d7377` |
| Amber | `#d4820a` |
| Green | `#1a7a4a` |
| Display Font | Bebas Neue |
| Body Font | Libre Baskerville |
| Mono Font | IBM Plex Mono |
| Condensed Font | Barlow Condensed |

Design principles: sharp corners, heavy black borders, grid paper background, typographic hierarchy.

---

## 📦 Dependencies

### Backend

```
flask>=3.0.0
flask-cors>=4.0.0
flask-sqlalchemy>=3.1.1
graphene>=3.3.0
python-dotenv>=1.0.0
PyMySQL>=1.1.0
```

### Frontend

- [Chart.js 4.4.0](https://www.chartjs.org/) — Statistics charts
- [Google Fonts](https://fonts.google.com/) — Bebas Neue, Libre Baskerville, IBM Plex Mono, Barlow Condensed

---

## 🔧 Environment Variables

Full `.env` reference:

```env
# Database type: sqlite | mysql | postgresql
DB_TYPE=sqlite

# Flask settings
FLASK_PORT=5000
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# MySQL (only if DB_TYPE=mysql)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=academiq

# PostgreSQL (only if DB_TYPE=postgresql)
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=
PG_DATABASE=academiq
```

---

## 🐛 Common Issues

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: flask` | Run `pip install flask flask-cors flask-sqlalchemy graphene python-dotenv PyMySQL` |
| `No such file app.py` | Make sure you are in the `backend/` folder before running `python app.py` |
| `Address already in use` | Another app is using port 5000. Change `FLASK_PORT=5001` in `.env` |
| `Failed to build greenlet` | You are using Python 3.15+. Install Python 3.11 instead |
| `ModuleNotFoundError: dotenv` | Run `pip install python-dotenv` separately |
| Website pages not opening | Replace `style.css` with the fixed version that removes `display:none` section rules |

---

## 📊 Performance Levels

| Level | GPA Range | Color |
|-------|-----------|-------|
| Excellent | 3.7 – 4.0 | Green |
| Good | 3.0 – 3.69 | Teal |
| Average | 2.5 – 2.99 | Amber |
| Below Average | 2.0 – 2.49 | Orange |
| Critical | Below 2.0 | Red |

---

## 👤 Author

**Om Kawle**
Student Academic Performance Advisor — AcademIQ v2
Built with Python Flask + AI Knowledge Representation Techniques

---

## 📄 License

This project is for educational purposes. Built as a demonstration of AI techniques including Semantic Networks and Knowledge Frames applied to student performance analysis.
