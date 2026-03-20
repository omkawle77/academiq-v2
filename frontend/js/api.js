/* api.js — All backend fetch calls */
const BASE = 'http://localhost:5000/api';

const API = {
  async analyze(data) {
    const r = await fetch(`${BASE}/analyze`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return r.json();
  },

  async createStudent(data) {
    const r = await fetch(`${BASE}/students`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return r.json();
  },

  async listStudents(params = {}) {
    const qs = new URLSearchParams(params).toString();
    const r = await fetch(`${BASE}/students?${qs}`);
    return r.json();
  },

  async getStudent(id) {
    const r = await fetch(`${BASE}/students/${id}`);
    return r.json();
  },

  async deleteStudent(id) {
    const r = await fetch(`${BASE}/students/${id}`, { method: 'DELETE' });
    return r.json();
  },

  async getStats() {
    const r = await fetch(`${BASE}/stats`);
    return r.json();
  },

  async getDbInfo() {
    const r = await fetch(`${BASE}/db-info`);
    return r.json();
  },

  async graphql(query, variables = {}) {
    const r = await fetch(`${BASE}/graphql`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, variables })
    });
    return r.json();
  },

  exportCsvUrl() { return `${BASE}/export/csv`; },

  async getAudit(limit = 20) {
    const r = await fetch(`${BASE}/audit?limit=${limit}`);
    return r.json();
  }
};