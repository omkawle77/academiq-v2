-- =============================================================
--  AcademIQ v2 — Sample Seed Data
-- =============================================================

INSERT INTO students (id, name, grade_level, attendance_rate, study_hours, learning_style)
VALUES
  ('STU00001', 'Maria Santos',    'Grade 11',          92.0, 4.0, 'visual'),
  ('STU00002', 'James Reyes',     '2nd Year College',  61.0, 1.5, 'auditory'),
  ('STU00003', 'Aisha Mohammed',  'Grade 12',          85.0, 3.5, 'reading'),
  ('STU00004', 'Carlos Mendez',   '1st Year College',  75.0, 2.5, 'kinesthetic'),
  ('STU00005', 'Priya Sharma',    'Grade 10',          97.0, 5.0, 'reading');

INSERT INTO subjects (student_id, subject_name, score, grade, gpa_points, difficulty, is_weak) VALUES
  ('STU00001','Mathematics',88,'B',3.0,'hard',0),
  ('STU00001','English',92,'A',4.0,'medium',0),
  ('STU00001','Science',85,'B',3.0,'hard',0),
  ('STU00001','History',78,'C',2.3,'medium',0),
  ('STU00002','Mathematics',52,'F',0.0,'hard',1),
  ('STU00002','English',65,'D',1.0,'medium',0),
  ('STU00002','Science',58,'F',0.0,'hard',1),
  ('STU00003','Mathematics',90,'A',4.0,'hard',0),
  ('STU00003','English',88,'B',3.0,'medium',0),
  ('STU00003','Chemistry',82,'B',3.0,'hard',0),
  ('STU00004','Mathematics',70,'C',2.0,'hard',0),
  ('STU00004','English',74,'C',2.3,'medium',0),
  ('STU00004','Programming',80,'B',3.0,'medium',0),
  ('STU00005','Mathematics',98,'A',4.0,'hard',0),
  ('STU00005','Physics',96,'A',4.0,'hard',0),
  ('STU00005','Chemistry',94,'A',4.0,'hard',0),
  ('STU00005','English',91,'A',4.0,'medium',0);

INSERT INTO extracurriculars (student_id, name) VALUES
  ('STU00001','🎨 Art'),
  ('STU00001','📸 Photography'),
  ('STU00003','💻 Coding Club'),
  ('STU00004','🏀 Sports'),
  ('STU00005','🧪 Science Club'),
  ('STU00005','🌍 Debate');