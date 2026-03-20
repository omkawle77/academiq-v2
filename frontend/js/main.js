/* main.js — AcademIQ v2 */

var currentAnalysis = null;
var currentFormData = null;
var rowCount = 0;
var SECTIONS = ['home','assess','results','history','graphql','stats'];

function showSection(name) {
  SECTIONS.forEach(function(s) {
    var el = document.getElementById(s);
    if (el) el.style.display = 'none';
  });
  document.querySelectorAll('.nav-links button').forEach(function(b) {
    b.classList.remove('active');
  });
  var el = document.getElementById(name);
  if (el) el.style.display = 'block';
  var nb = document.getElementById('nav-' + name);
  if (nb) nb.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function addRow(name, score, diff) {
  name  = name  !== undefined ? name  : '';
  score = score !== undefined ? score : '';
  diff  = diff  !== undefined ? diff  : 'medium';
  rowCount++;
  var id = rowCount;
  var tbody = document.getElementById('subjects-tbody');
  var tr = document.createElement('tr');
  tr.id = 'row-' + id;
  tr.innerHTML =
    '<td><input type="text" placeholder="e.g. Mathematics" value="' + name + '" class="sub-name"></td>' +
    '<td><input type="number" placeholder="0-100" min="0" max="100" value="' + score + '" class="sub-score"></td>' +
    '<td><select class="sub-diff">' +
      '<option value="easy"'   + (diff==='easy'   ? ' selected' : '') + '>Easy</option>' +
      '<option value="medium"' + (diff==='medium' ? ' selected' : '') + '>Medium</option>' +
      '<option value="hard"'   + (diff==='hard'   ? ' selected' : '') + '>Hard</option>' +
    '</select></td>' +
    '<td><button class="btn-del" onclick="removeRow(' + id + ')">Remove</button></td>';
  tbody.appendChild(tr);
}

function removeRow(id) {
  var row = document.getElementById('row-' + id);
  if (row) row.remove();
}

function toggleTag(el) { el.classList.toggle('selected'); }

function getSubjects() {
  var rows = document.querySelectorAll('#subjects-tbody tr');
  var result = [];
  rows.forEach(function(r) {
    var nameEl  = r.querySelector('.sub-name');
    var scoreEl = r.querySelector('.sub-score');
    var diffEl  = r.querySelector('.sub-diff');
    var n = nameEl  ? nameEl.value.trim()  : '';
    var s = scoreEl ? parseFloat(scoreEl.value) || 0 : 0;
    var d = diffEl  ? diffEl.value : 'medium';
    if (n) result.push({ subject_name: n, score: s, difficulty: d });
  });
  return result;
}

function getExtras() {
  var result = [];
  document.querySelectorAll('.tag.selected').forEach(function(t) {
    result.push(t.textContent.trim());
  });
  return result;
}

function addDefaultRows() {
  addRow('Mathematics', '', 'hard');
  addRow('English',     '', 'medium');
  addRow('Science',     '', 'medium');
}

function resetForm() {
  document.getElementById('f-name').value       = '';
  document.getElementById('f-grade').value      = '';
  document.getElementById('f-attendance').value = '';
  document.getElementById('f-study').value      = '';
  document.getElementById('f-style').value      = '';
  document.querySelectorAll('.tag.selected').forEach(function(t) { t.classList.remove('selected'); });
  document.getElementById('subjects-tbody').innerHTML = '';
  rowCount = 0;
  addDefaultRows();
}

async function submitForm() {
  var name       = document.getElementById('f-name').value.trim();
  var attendance = parseFloat(document.getElementById('f-attendance').value);
  var study      = parseFloat(document.getElementById('f-study').value) || 0;

  if (!name) { showToast('Please enter your name.', 'error'); return; }
  if (isNaN(attendance) || attendance < 0 || attendance > 100) {
    showToast('Enter a valid attendance rate (0 to 100).', 'error'); return;
  }
  var subjects = getSubjects();
  if (!subjects.length) { showToast('Add at least one subject.', 'error'); return; }

  currentFormData = {
    name: name,
    grade_level: document.getElementById('f-grade').value,
    attendance_rate: attendance,
    study_hours_per_day: study,
    learning_style: document.getElementById('f-style').value,
    subjects: subjects,
    extracurriculars: getExtras()
  };

  setLoading(true);
  try {
    var data = await API.analyze(currentFormData);
    setLoading(false);
    if (data.success) {
      currentAnalysis = data.analysis;
      renderResults(data.analysis, name);
      showSection('results');
      var saveBtn = document.getElementById('save-btn');
      saveBtn.disabled    = false;
      saveBtn.textContent = 'Save Record';
    } else {
      showToast('Analysis failed: ' + (data.error || 'Unknown error'), 'error');
    }
  } catch (e) {
    setLoading(false);
    showToast('Cannot reach server. Is Flask running on port 5000?', 'error');
  }
}

function setBar(id, pct, color) {
  var el = document.getElementById(id);
  if (el) { el.style.width = pct + '%'; el.style.background = color; }
}

function renderResults(a, name) {
  document.getElementById('res-name').textContent    = name.toUpperCase();
  document.getElementById('res-summary').textContent = a.summary || '';

  var levelEl = document.getElementById('res-level');
  levelEl.textContent = '// ' + (a.performance_label || '').toUpperCase();
  levelEl.style.color = a.performance_color || '#111111';

  var gpaEl = document.getElementById('res-gpa');
  gpaEl.textContent = typeof a.gpa === 'number' ? a.gpa.toFixed(2) : '0.00';
  gpaEl.style.color = a.performance_color || '#111111';

  var att = a.attendance_rate || a.attendance || 0;
  document.getElementById('m-att').textContent      = att + '%';
  document.getElementById('m-study').textContent    = (a.study_hours || 0) + 'h';
  document.getElementById('m-subcount').textContent = (a.enriched_subjects || []).length;
  document.getElementById('m-advice').textContent   = (a.advice || []).length;

  setTimeout(function() {
    setBar('m-att-bar',   att,                                                    '#1a7a4a');
    setBar('m-study-bar', Math.min(((a.study_hours || 0) / 8) * 100, 100),       '#0d7377');
    setBar('m-sub-bar',   Math.min(((a.enriched_subjects||[]).length/8)*100,100), '#d4820a');
    setBar('m-adv-bar',   100,                                                    '#e84141');
  }, 100);

  var subEl = document.getElementById('res-subjects');
  var subs  = a.enriched_subjects || [];
  if (!subs.length) {
    subEl.innerHTML = '<p style="color:#555555">No subjects found.</p>';
  } else {
    var subHTML = '';
    subs.forEach(function(s) {
      var c = s.score >= 80 ? '#1a7a4a' : (s.score >= 60 ? '#d4820a' : '#e84141');
      subHTML +=
        '<div class="sub-bar-item">' +
          '<div class="sub-bar-meta">' +
            '<span>' + s.subject_name + '</span>' +
            '<span class="grade" style="color:' + c + '">' + s.score + '/100 ' + (s.grade||'') + '</span>' +
          '</div>' +
          '<div class="sub-bar-track">' +
            '<div class="sub-bar-fill" data-w="' + s.score + '" style="width:0%;background:' + c + '"></div>' +
          '</div>' +
        '</div>';
    });
    subEl.innerHTML = subHTML;
    setTimeout(function() {
      document.querySelectorAll('.sub-bar-fill[data-w]').forEach(function(el) {
        el.style.width = el.getAttribute('data-w') + '%';
      });
    }, 150);
  }

  var PLABELS = {
    low_gpa:'Low GPA Detected',
    poor_attendance:'Below-Average Attendance',
    weak_subjects:'Weak Subjects Identified',
    low_study_hours:'Insufficient Study Time',
    no_extracurricular:'No Extracurricular Activity'
  };
  var issueHTML = '';
  (a.problems_detected || []).forEach(function(p) {
    issueHTML += '<div class="issue-item">Warning: ' + (PLABELS[p] || p) + '</div>';
  });
  (a.strengths || []).forEach(function(s) {
    issueHTML += '<div class="strength-item">Strong: ' + s + '</div>';
  });
  if (!issueHTML) issueHTML = '<div class="strength-item">No critical issues detected.</div>';
  document.getElementById('res-issues').innerHTML = issueHTML;

  var advEl  = document.getElementById('res-advice');
  var advice = a.advice || [];
  if (!advice.length) {
    advEl.innerHTML = '<p style="padding:2rem;color:#555555">No advice generated.</p>';
    return;
  }
  var advHTML = '';
  advice.forEach(function(adv) {
    var steps = '';
    (adv.action_steps || []).forEach(function(step, j) {
      steps += '<div class="adv-step"><div class="step-dot">' + (j+1) + '</div><div>' + step + '</div></div>';
    });
    advHTML +=
      '<div class="advice-card" onclick="this.classList.toggle(\'expanded\')">' +
        '<div class="adv-priority prio-' + (adv.priority||'medium') + '">[ ' + (adv.priority||'medium').toUpperCase() + ' PRIORITY ]</div>' +
        '<span class="adv-icon">' + (adv.icon||'') + '</span>' +
        '<div class="adv-title">' + (adv.title||'') + '</div>' +
        '<div class="adv-desc">'  + (adv.description||'') + '</div>' +
        '<div class="adv-expand">' + steps + '</div>' +
      '</div>';
  });
  advEl.innerHTML = advHTML;
}

async function saveRecord() {
  if (!currentFormData) return;
  var btn = document.getElementById('save-btn');
  btn.disabled = true; btn.textContent = 'Saving...';
  try {
    var data = await API.createStudent(currentFormData);
    if (data.success) {
      showToast('Saved! ID: ' + data.student_id, 'success');
      btn.textContent = 'Saved';
    } else {
      showToast('Save failed.', 'error');
      btn.disabled = false; btn.textContent = 'Save Record';
    }
  } catch (e) {
    showToast('Server unreachable.', 'error');
    btn.disabled = false; btn.textContent = 'Save Record';
  }
}

async function loadHistory() {
  var search = document.getElementById('h-search') ? document.getElementById('h-search').value : '';
  var level  = document.getElementById('h-level')  ? document.getElementById('h-level').value  : '';
  var wrap   = document.getElementById('students-table-body');
  if (!wrap) return;
  wrap.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:2rem;color:#555555">Loading...</td></tr>';
  try {
    var params = { limit: 50 };
    if (search) params.search = search;
    if (level)  params.level  = level;
    var data = await API.listStudents(params);
    if (!data.success || !data.students || !data.students.length) {
      wrap.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:3rem;color:#555555">No records found. Analyze and save a student first.</td></tr>';
      return;
    }
    var totalEl = document.getElementById('history-total');
    if (totalEl) totalEl.textContent = data.total + ' record' + (data.total!==1?'s':'');
    var rows = '';
    data.students.forEach(function(s) {
      var color = s.performance_color || '#111111';
      var gpa   = typeof s.gpa === 'number' ? s.gpa.toFixed(2) : '—';
      var date  = s.created_at ? new Date(s.created_at).toLocaleDateString() : '—';
      rows +=
        '<tr>' +
          '<td style="font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem;color:#555555">' + s.id + '</td>' +
          '<td><strong>' + s.name + '</strong></td>' +
          '<td>' + (s.grade_level||'—') + '</td>' +
          '<td style="font-family:\'IBM Plex Mono\',monospace;font-weight:600;color:'+color+'">' + gpa + '</td>' +
          '<td style="color:'+color+';font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem;font-weight:600">' + (s.performance_label||'—') + '</td>' +
          '<td>' + (s.attendance_rate!=null ? s.attendance_rate+'%' : '—') + '</td>' +
          '<td style="color:#555555">' + date + '</td>' +
          '<td>' +
            '<button class="btn-view" onclick="viewRecord(\'' + s.id + '\')">View</button> ' +
            '<button class="btn-delete" onclick="deleteRecord(\'' + s.id + '\',this)">Delete</button>' +
          '</td>' +
        '</tr>';
    });
    wrap.innerHTML = rows;
  } catch (e) {
    wrap.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:2rem;color:#e84141">Server unreachable. Is Flask running?</td></tr>';
  }
}

async function viewRecord(id) {
  setLoading(true);
  try {
    var data = await API.getStudent(id);
    setLoading(false);
    if (data.success) {
      renderResults(data.student.analysis, data.student.name);
      showSection('results');
      var btn = document.getElementById('save-btn');
      btn.textContent = 'Already Saved'; btn.disabled = true;
    }
  } catch (e) { setLoading(false); showToast('Cannot load record.', 'error'); }
}

async function deleteRecord(id, btn) {
  if (!confirm('Delete student ' + id + '? This cannot be undone.')) return;
  btn.textContent = '...';
  try {
    await API.deleteStudent(id);
    showToast('Record deleted.', 'success');
    loadHistory();
  } catch (e) { showToast('Delete failed.', 'error'); }
}

async function loadStats() {
  try {
    var data = await API.getStats();
    if (!data.success) return;
    document.getElementById('stat-total').textContent = data.total_students || 0;
    document.getElementById('stat-gpa').textContent   = data.avg_gpa ? parseFloat(data.avg_gpa).toFixed(2) : '0.00';
    document.getElementById('stat-att').textContent   = data.avg_attendance ? parseFloat(data.avg_attendance).toFixed(1)+'%' : '0%';
    var lv = data.performance_levels || {};
    document.getElementById('stat-exc').textContent  = lv.excellent || 0;
    document.getElementById('stat-crit').textContent = lv.critical  || 0;
    var freq = data.problem_frequency || {};
    var entries = Object.entries(freq).sort(function(a,b){return b[1]-a[1];});
    document.getElementById('stat-top-prob').textContent = entries.length ? entries[0][0].replace(/_/g,' ').toUpperCase() : 'NONE';
    renderStatsCharts(data);
  } catch (e) { /* server may be off */ }
}

var GQL_PRESETS = {
  'All Students': '{\n  students(limit: 10) {\n    id name gradeLevel\n    analysis { gpa performanceLabel }\n  }\n}',
  'Stats': '{\n  stats {\n    totalStudents avgGpa avgAttendance\n    excellentCount criticalCount mostCommonProblem\n  }\n}',
  'Search': '{\n  search(name: "") {\n    id name\n    analysis { gpa performanceLabel }\n  }\n}',
  'Single Student': '{\n  student(id: "REPLACE_WITH_ID") {\n    id name gradeLevel attendanceRate\n    analysis { gpa performanceLabel summary\n      advice { title priority }\n    }\n  }\n}'
};

function loadPreset(name) {
  var el = document.getElementById('gql-query');
  if (el) el.value = GQL_PRESETS[name] || '';
}

async function runGraphQL() {
  var query  = document.getElementById('gql-query').value.trim();
  var result = document.getElementById('gql-result');
  if (!query) return;
  result.textContent = 'Running...';
  try {
    var data = await API.graphql(query);
    result.textContent = JSON.stringify(data, null, 2);
  } catch (e) { result.textContent = 'Error: ' + e.message; }
}

async function loadDbInfo() {
  try {
    var data = await API.getDbInfo();
    if (data.success) {
      var badge = document.getElementById('db-badge');
      if (badge) badge.textContent = data.db_type.toUpperCase();
    }
  } catch (e) { /* offline */ }
}

function setLoading(on) {
  var el = document.getElementById('loading');
  if (on) { el.classList.add('active'); } else { el.classList.remove('active'); }
}

function showToast(msg, type) {
  type = type || 'success';
  var t = document.getElementById('toast');
  document.getElementById('toast-msg').textContent = msg;
  t.className = 'toast ' + type + ' show';
  setTimeout(function() { t.classList.remove('show'); }, 3500);
}

document.addEventListener('DOMContentLoaded', function() {
  addDefaultRows();
  loadDbInfo();
  showSection('home');
  var gqlEl = document.getElementById('gql-query');
  if (gqlEl) gqlEl.value = GQL_PRESETS['All Students'];
});