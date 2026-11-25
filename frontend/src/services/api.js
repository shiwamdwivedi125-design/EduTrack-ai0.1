// API service layer
import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Request interceptor - attach token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor - handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ─── Auth ───────────────────────────────────────────────────────
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
  changePassword: (old_password, new_password) =>
    api.post(`/auth/change-password?old_password=${old_password}&new_password=${new_password}`),
};

// ─── Students ───────────────────────────────────────────────────
export const studentsAPI = {
  list: (params) => api.get('/students', { params }),
  get: (id) => api.get(`/students/${id}`),
  myProfile: () => api.get('/students/me/profile'),
  create: (data) => api.post('/students', data),
  update: (id, data) => api.put(`/students/${id}`, data),
  delete: (id) => api.delete(`/students/${id}`),
  academicSummary: (id) => api.get(`/students/${id}/academic-summary`),
};

// ─── Marks ──────────────────────────────────────────────────────
export const marksAPI = {
  add: (data) => api.post('/marks', data),
  list: (params) => api.get('/marks', { params }),
  studentMarks: (id, params) => api.get(`/marks/student/${id}`, { params }),
  bulkUpload: (records) => api.post('/marks/bulk', { records }),
};

// ─── Attendance ──────────────────────────────────────────────────
export const attendanceAPI = {
  add: (data) => api.post('/attendance', data),
  list: (params) => api.get('/attendance', { params }),
  student: (id) => api.get(`/attendance/student/${id}`),
  bulk: (records) => api.post('/attendance/bulk', { records }),
};

// ─── Analytics ──────────────────────────────────────────────────
export const analyticsAPI = {
  overview: () => api.get('/analytics/overview'),
  performance: (params) => api.get('/analytics/performance', { params }),
  attendance: (params) => api.get('/analytics/attendance', { params }),
  riskSummary: () => api.get('/analytics/risk-summary'),
  stats: () => api.get('/analytics/stats'),
  charts: () => api.get('/analytics/charts'),
};

// ─── Departments ─────────────────────────────────────────────────
export const departmentsAPI = {
  list: () => api.get('/departments'),
  create: (data) => api.post('/departments', data),
};

// ─── Subjects ────────────────────────────────────────────────────
export const subjectsAPI = {
  list: (params) => api.get('/subjects', { params }),
  create: (data) => api.post('/subjects', data),
};

// ─── Semesters ───────────────────────────────────────────────────
export const semestersAPI = {
  list: () => api.get('/semesters'),
  create: (data) => api.post('/semesters', data),
};

// ─── Teachers ────────────────────────────────────────────────────
export const teachersAPI = {
  list: () => api.get('/teachers'),
  create: (data) => api.post('/teachers', data),
};

// ─── ML ──────────────────────────────────────────────────────────
export const mlAPI = {
  predict: (data) => api.post('/ml/predict', data),
  evaluation: () => api.get('/ml/evaluation'),
  featureImportance: () => api.get('/ml/feature-importance'),
};

// ─── Study Plans ─────────────────────────────────────────────────
export const studyPlanAPI = {
  generate: (data) => api.post('/study-plans/generate', data),
  list: () => api.get('/study-plans'),
  get: (id) => api.get(`/study-plans/${id}`),
};

// ─── Goals ───────────────────────────────────────────────────────
export const goalsAPI = {
  list: () => api.get('/goals'),
  create: (data) => api.post('/goals', data),
  complete: (id) => api.put(`/goals/${id}/complete`),
  delete: (id) => api.delete(`/goals/${id}`),
};

// ─── Notifications ───────────────────────────────────────────────
export const notificationsAPI = {
  list: () => api.get('/notifications'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
};

// ─── Alerts ──────────────────────────────────────────────────────
export const alertsAPI = {
  list: () => api.get('/alerts'),
  resolve: (id) => api.put(`/alerts/${id}/resolve`),
};

// ─── Reports ─────────────────────────────────────────────────────
export const reportsAPI = {
  student: (id) => api.get(`/reports/student/${id}`),
  department: (id) => api.get(`/reports/department/${id}`),
  download: (reportType, format = 'pdf', params = {}) =>
    api.get(`/reports/download/${reportType}`, {
      params: { format, ...params },
      responseType: 'blob',
    }),
};

// ─── Interventions ───────────────────────────────────────────────
export const interventionsAPI = {
  list: (params) => api.get('/interventions', { params }),
  create: (data) => api.post('/interventions', data),
  update: (id, data) => api.put(`/interventions/${id}`, data),
};

// ─── Placement ───────────────────────────────────────────────────
export const placementAPI = {
  get: (studentId) => api.get('/placement/me', { params: studentId ? { student_id: studentId } : {} }),
  update: (data) => api.put('/placement/me', data),
  addSkill: (data) => api.post('/placement/skills', data),
  deleteSkill: (id) => api.delete(`/placement/skills/${id}`),
};

// ─── Grading Rules ───────────────────────────────────────────────
export const gradingAPI = {
  list: () => api.get('/grading-rules'),
  create: (data) => api.post('/grading-rules', data),
  delete: (id) => api.delete(`/grading-rules/${id}`),
};

// ─── CSV / Excel Import ──────────────────────────────────────────
export const importAPI = {
  preview: (entityType, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/import/preview?entity_type=${entityType}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  confirm: (entityType, rows) => api.post('/import/confirm', { entity_type: entityType, rows }),
};

// ─── Audit Logs ──────────────────────────────────────────────────
export const auditAPI = {
  list: () => api.get('/audit-logs'),
};

// ─── Users ───────────────────────────────────────────────────────
export const usersAPI = {
  list: () => api.get('/users'),
  update: (id, data) => api.put(`/users/${id}`, data),
};

export default api;
