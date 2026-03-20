"""knowledge_base.py — AI Engine: Frames + Semantic Nets"""

STUDENT_FRAME = {"slots": {"student_id":None,"name":None,"grade_level":None,"gpa":None,
    "attendance_rate":None,"study_hours_per_day":None,"subjects":[],"extracurriculars":[],
    "learning_style":None,"performance_level":None}}

PERFORMANCE_LEVEL_FRAME = {"levels":{
    "excellent":     {"min_gpa":3.7,"min_attendance":90,"label":"Excellent",    "color":"#22c55e"},
    "good":          {"min_gpa":3.0,"min_attendance":80,"label":"Good",         "color":"#84cc16"},
    "average":       {"min_gpa":2.5,"min_attendance":70,"label":"Average",      "color":"#eab308"},
    "below_average": {"min_gpa":2.0,"min_attendance":60,"label":"Below Average","color":"#f97316"},
    "critical":      {"min_gpa":0.0,"min_attendance":0, "label":"Critical",     "color":"#ef4444"},
}}

SEMANTIC_NET_EDGES = [
    ("low_gpa",           "tutoring",           "is_resolved_by"),
    ("low_gpa",           "study_schedule",     "is_resolved_by"),
    ("low_gpa",           "active_recall",      "is_resolved_by"),
    ("low_gpa",           "peer_learning",      "is_resolved_by"),
    ("poor_attendance",   "attendance_plan",    "is_resolved_by"),
    ("poor_attendance",   "counseling",         "is_resolved_by"),
    ("poor_attendance",   "wellness",           "is_resolved_by"),
    ("weak_subjects",     "tutoring",           "is_resolved_by"),
    ("weak_subjects",     "spaced_repetition",  "is_resolved_by"),
    ("weak_subjects",     "active_recall",      "is_resolved_by"),
    ("low_study_hours",   "study_schedule",     "is_resolved_by"),
    ("low_study_hours",   "goal_setting",       "is_resolved_by"),
    ("no_extracurricular","extracurricular_join","is_resolved_by"),
    ("critical",          "counseling",         "requires"),
    ("below_average",     "goal_setting",       "requires"),
    ("good",              "advanced_courses",   "should_consider"),
    ("excellent",         "maintain_excellence","should_practice"),
    ("excellent",         "advanced_courses",   "should_consider"),
]

ADVICE_DB = {
    "tutoring":           {"title":"Get Subject-Specific Tutoring","icon":"🎓","priority":"high",
        "description":"Work with a tutor 2–3×/week on your weakest subjects.",
        "action_steps":["Identify your 2 weakest subjects from your scores.",
            "Approach your subject teacher for extra help sessions.",
            "Join a peer tutoring program if available.",
            "Use Khan Academy or Coursera for guided lessons."]},
    "study_schedule":     {"title":"Build a Structured Study Schedule","icon":"📅","priority":"high",
        "description":"A consistent, time-blocked schedule dramatically improves retention.",
        "action_steps":["Dedicate fixed daily slots for each subject.",
            "Use the Pomodoro technique: 25 min study, 5 min break.",
            "Review notes within 24 hours of each class.",
            "Plan harder subjects for your peak energy hours."]},
    "attendance_plan":    {"title":"Improve Your Attendance","icon":"✅","priority":"critical",
        "description":"Regular attendance is directly correlated with GPA.",
        "action_steps":["Set a daily alarm and prepare materials the night before.",
            "Notify teachers in advance if absence is unavoidable.",
            "Create an attendance log to track and motivate yourself.",
            "Address any underlying barriers with a counselor."]},
    "goal_setting":       {"title":"Set SMART Academic Goals","icon":"🎯","priority":"medium",
        "description":"Specific, Measurable, Achievable, Relevant, Time-bound goals keep you focused.",
        "action_steps":["Write 3 academic goals for this semester.",
            "Break each goal into weekly milestones.",
            "Review goals every Sunday and adjust.",
            "Celebrate small wins to stay motivated."]},
    "peer_learning":      {"title":"Form a Study Group","icon":"👥","priority":"medium",
        "description":"Explaining concepts to peers deepens understanding.",
        "action_steps":["Find 3–4 motivated classmates with similar goals.",
            "Meet 2× per week for focused 90-minute sessions.",
            "Rotate who leads each session's topic.",
            "Quiz each other using practice questions."]},
    "counseling":         {"title":"Seek Academic Counseling","icon":"💬","priority":"critical",
        "description":"Academic advisors provide personalized roadmaps and support resources.",
        "action_steps":["Schedule an appointment with your advisor this week.",
            "Discuss your struggles openly and honestly.",
            "Ask about tutoring programs, extensions, or support services.",
            "Follow up with a monthly check-in."]},
    "active_recall":      {"title":"Practice Active Recall","icon":"🧠","priority":"high",
        "description":"Testing yourself is far more effective than re-reading notes.",
        "action_steps":["After reading, close the book and recall key points.",
            "Use flashcards (Anki) for vocabulary and formulas.",
            "Complete past exam papers under timed conditions.",
            "Use the Feynman Technique: explain topics simply."]},
    "spaced_repetition":  {"title":"Apply Spaced Repetition","icon":"🔄","priority":"high",
        "description":"Reviewing at increasing intervals cements long-term memory.",
        "action_steps":["Install Anki and create decks for each subject.",
            "Review new material after 1 day, 3 days, 1 week, 2 weeks.",
            "Spend 15–20 min daily on spaced reviews.",
            "Prioritize cards you get wrong more frequently."]},
    "wellness":           {"title":"Prioritize Sleep & Mental Wellness","icon":"🌿","priority":"high",
        "description":"Sleep deprivation reduces cognitive function. Wellness is foundational.",
        "action_steps":["Aim for 7–9 hours of quality sleep nightly.",
            "Exercise for at least 30 minutes, 3× per week.",
            "Practice 10 min of mindfulness daily.",
            "Limit screen time 1 hour before bed."]},
    "extracurricular_join":{"title":"Join an Extracurricular Activity","icon":"🏆","priority":"low",
        "description":"Balanced students report higher motivation and better social skills.",
        "action_steps":["Explore clubs, sports, or arts programs at your school.",
            "Commit to one activity for at least one semester.",
            "Leadership roles strengthen your profile.",
            "Ensure it complements, not competes with, your studies."]},
    "maintain_excellence":{"title":"Maintain and Elevate Your Excellence","icon":"⭐","priority":"medium",
        "description":"Sustaining top performance requires deliberate challenge.",
        "action_steps":["Set higher benchmark targets for each subject.",
            "Mentor struggling peers—teaching reinforces mastery.",
            "Explore competitions, olympiads, or research projects.",
            "Document achievements for future applications."]},
    "advanced_courses":   {"title":"Challenge Yourself with Advanced Courses","icon":"🚀","priority":"medium",
        "description":"High performers benefit from deeper, more challenging coursework.",
        "action_steps":["Enroll in AP, honors, or elective advanced modules.",
            "Explore online platforms like Coursera or edX.",
            "Discuss with your teacher about going beyond the syllabus.",
            "Start an independent research or passion project."]},
}

def score_to_grade(s):
    return "A" if s>=90 else "B" if s>=80 else "C" if s>=70 else "D" if s>=60 else "F"

def score_to_gpa(s):
    return (4.0 if s>=90 else 3.7 if s>=87 else 3.3 if s>=83 else 3.0 if s>=80
            else 2.7 if s>=77 else 2.3 if s>=73 else 2.0 if s>=70
            else 1.7 if s>=67 else 1.0 if s>=60 else 0.0)

def infer_level(gpa, att):
    lvls = PERFORMANCE_LEVEL_FRAME["levels"]
    for k in ["excellent","good","average","below_average","critical"]:
        l = lvls[k]
        if gpa >= l["min_gpa"] and att >= l["min_attendance"]:
            return k
    return "critical"

def identify_problems(data):
    probs = []
    if data.get("gpa",0)               < 2.5:  probs.append("low_gpa")
    if data.get("attendance_rate",100)  < 75:   probs.append("poor_attendance")
    if data.get("study_hours_per_day",8)< 2:    probs.append("low_study_hours")
    if any(s.get("score",100)<60 for s in data.get("subjects",[])):
        probs.append("weak_subjects")
    if not data.get("extracurriculars",[]):
        probs.append("no_extracurricular")
    return probs

def resolve_strategies(problems, level):
    strategies = set()
    for prob in problems:
        for src,dst,rel in SEMANTIC_NET_EDGES:
            if src==prob and rel=="is_resolved_by":
                strategies.add(dst)
    for src,dst,rel in SEMANTIC_NET_EDGES:
        if src==level and rel in ("requires","should_consider","should_practice"):
            strategies.add(dst)
    return list(strategies)

def analyze_student(data):
    subjects = data.get("subjects",[])
    enriched = [{**s,"grade":score_to_grade(s.get("score",0)),
                 "gpa_points":score_to_gpa(s.get("score",0)),
                 "is_weak":s.get("score",0)<60} for s in subjects]
    gpa = round(sum(s["gpa_points"] for s in enriched)/len(enriched),2) if enriched else 0.0
    att = data.get("attendance_rate",0)
    level = infer_level(gpa, att)
    meta  = PERFORMANCE_LEVEL_FRAME["levels"][level]

    updated = {**data,"gpa":gpa,"subjects":enriched}
    problems  = identify_problems(updated)
    strat_keys= resolve_strategies(problems, level)

    prio = {"critical":0,"high":1,"medium":2,"low":3}
    advice = sorted(
        [{"key":k,**ADVICE_DB[k]} for k in strat_keys if k in ADVICE_DB],
        key=lambda a: prio.get(a["priority"],9)
    )

    strengths    = [s["subject_name"] for s in enriched if s.get("score",0)>=80]
    weak_subjects= [s["subject_name"] for s in enriched if s.get("is_weak")]
    name = data.get("name","Student")

    summaries = {
        "excellent":f"{name}, you are performing at an exceptional level with a {gpa:.2f} GPA. Keep pushing boundaries!",
        "good":f"{name}, you're doing well with a {gpa:.2f} GPA. Targeted effort can push you to the top.",
        "average":f"{name}, your {gpa:.2f} GPA shows real potential. Focused work in {', '.join(weak_subjects) or 'key areas'} will make a big difference.",
        "below_average":f"{name}, your {gpa:.2f} GPA needs attention. The right strategies can turn this around quickly.",
        "critical":f"{name}, your academic standing requires urgent action. Following this plan and seeking counseling is critical.",
    }

    return {
        "gpa":gpa,"performance_level":level,"performance_label":meta["label"],
        "performance_color":meta["color"],"problems_detected":problems,
        "enriched_subjects":enriched,"strengths":strengths,"weak_subjects":weak_subjects,
        "advice":advice,"summary":summaries[level],
        "study_hours":data.get("study_hours_per_day",0),"attendance":att,
    }