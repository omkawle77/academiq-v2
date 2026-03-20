/* charts.js — AcademIQ v2 Chart rendering */

var chartInstances = {};

function destroyChart(id) {
  if (chartInstances[id]) {
    chartInstances[id].destroy();
    delete chartInstances[id];
  }
}

function renderStatsCharts(data) {
  var INK   = '#111111';
  var CORAL = '#e84141';
  var BG    = '#f5f2eb';
  var TEAL  = '#0d7377';
  var AMBER = '#d4820a';
  var GREEN = '#1a7a4a';
  var ORANGE = '#f97316';

  /* --- Chart 1: Performance Distribution (Doughnut) --- */
  destroyChart('chart-levels');
  var levelsEl = document.getElementById('chart-levels');
  if (levelsEl) {
    var lv = data.performance_levels || {};
    chartInstances['chart-levels'] = new Chart(levelsEl, {
      type: 'doughnut',
      data: {
        labels: ['Excellent', 'Good', 'Average', 'Below Avg', 'Critical'],
        datasets: [{
          data: [
            lv.excellent     || 0,
            lv.good          || 0,
            lv.average       || 0,
            lv.below_average || 0,
            lv.critical      || 0
          ],
          backgroundColor: [GREEN, TEAL, AMBER, ORANGE, CORAL],
          borderColor: BG,
          borderWidth: 3
        }]
      },
      options: {
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              font: { family: 'IBM Plex Mono', size: 10 },
              padding: 10,
              color: INK
            }
          }
        }
      }
    });
  }

  /* --- Chart 2: Subject Averages (Horizontal Bar) --- */
  destroyChart('chart-subjects');
  var subjectsEl = document.getElementById('chart-subjects');
  if (subjectsEl) {
    var subjectData = data.subject_averages || {};
    var subLabels   = Object.keys(subjectData);
    var subValues   = Object.values(subjectData).map(function(v) { return parseFloat(v) || 0; });
    var subColors   = subValues.map(function(v) {
      return v >= 80 ? GREEN : (v >= 60 ? AMBER : CORAL);
    });
    if (!subLabels.length) {
      subLabels = ['No Data'];
      subValues = [0];
      subColors = [INK];
    }
    chartInstances['chart-subjects'] = new Chart(subjectsEl, {
      type: 'bar',
      data: {
        labels: subLabels,
        datasets: [{
          label: 'Avg Score',
          data: subValues,
          backgroundColor: subColors,
          borderColor: INK,
          borderWidth: 2
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: {
          x: {
            min: 0, max: 100,
            grid: { color: 'rgba(17,17,17,0.08)' },
            ticks: { font: { family: 'IBM Plex Mono', size: 10 }, color: INK }
          },
          y: {
            grid: { display: false },
            ticks: { font: { family: 'Libre Baskerville', size: 11 }, color: INK }
          }
        }
      }
    });
  }

  /* --- Chart 3: Problem Frequency (Bar) --- */
  destroyChart('chart-problems');
  var problemsEl = document.getElementById('chart-problems');
  if (problemsEl) {
    var freq    = data.problem_frequency || {};
    var pLabels = Object.keys(freq).map(function(k) {
      return k.replace(/_/g,' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
    });
    var pValues = Object.values(freq).map(function(v) { return parseInt(v) || 0; });
    if (!pLabels.length) {
      pLabels = ['No Data'];
      pValues = [0];
    }
    chartInstances['chart-problems'] = new Chart(problemsEl, {
      type: 'bar',
      data: {
        labels: pLabels,
        datasets: [{
          label: 'Count',
          data: pValues,
          backgroundColor: CORAL,
          borderColor: INK,
          borderWidth: 2
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, font: { family: 'IBM Plex Mono', size: 10 }, color: INK },
            grid: { color: 'rgba(17,17,17,0.08)' }
          },
          x: {
            grid: { display: false },
            ticks: { font: { family: 'Libre Baskerville', size: 10 }, color: INK }
          }
        }
      }
    });
  }
}
