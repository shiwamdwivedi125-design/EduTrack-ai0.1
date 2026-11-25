import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { LoadingSpinner } from '../components/Common';
import { attendanceAPI, studentsAPI, subjectsAPI, analyticsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { CalendarCheck, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function AttendanceManagement() {
  const { user } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [studentAttendance, setStudentAttendance] = useState(null);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [form, setForm] = useState({ student_id: '', subject_id: '', date: new Date().toISOString().split('T')[0], is_present: true });
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      if (user?.role === 'student') {
        const prof = await studentsAPI.myProfile();
        const res = await attendanceAPI.student(prof.data.id);
        setStudentAttendance(res.data);
      } else {
        const [subRes, stuRes, attAn] = await Promise.all([
          subjectsAPI.list(),
          studentsAPI.list({ page: 1, page_size: 50 }),
          analyticsAPI.attendance(),
        ]);
        setSubjects(subRes.data || []);
        setStudents(stuRes.data.items || []);
        setAnalytics(attAn.data);
      }
    } catch {
      toast.error('Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleMarkAttendance = async (e) => {
    e.preventDefault();
    try {
      await attendanceAPI.add({
        student_id: Number(form.student_id),
        subject_id: Number(form.subject_id),
        date: form.date,
        is_present: form.is_present,
      });
      toast.success('Attendance recorded');
      loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to record attendance');
    }
  };

  const handleInspectStudent = async (sid) => {
    setSelectedStudentId(sid);
    if (!sid) return setStudentAttendance(null);
    try {
      const res = await attendanceAPI.student(sid);
      setStudentAttendance(res.data);
    } catch {
      toast.error('Failed to fetch student attendance');
    }
  };

  if (loading) {
    return <DashboardLayout title="Attendance Management"><LoadingSpinner /></DashboardLayout>;
  }

  return (
    <DashboardLayout title="Attendance Management">
      {user?.role !== 'student' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Mark Daily Attendance Form */}
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <CalendarCheck className="w-5 h-5 text-blue-600" /> Mark Daily Attendance
            </h3>
            <form onSubmit={handleMarkAttendance} className="space-y-3">
              <div>
                <label className="label">Student</label>
                <select required className="input" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })}>
                  <option value="">Select student...</option>
                  {students.map((s) => <option key={s.id} value={s.id}>{s.student_id} — {s.full_name}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Subject</label>
                <select required className="input" value={form.subject_id} onChange={(e) => setForm({ ...form, subject_id: e.target.value })}>
                  <option value="">Select subject...</option>
                  {subjects.map((s) => <option key={s.id} value={s.id}>{s.code} — {s.name}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Date</label>
                <input type="date" required className="input" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
              </div>
              <div className="flex items-center gap-4 py-1">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="radio" checked={form.is_present === true} onChange={() => setForm({ ...form, is_present: true })} /> Present
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="radio" checked={form.is_present === false} onChange={() => setForm({ ...form, is_present: false })} /> Absent
                </label>
              </div>
              <button type="submit" className="btn-primary w-full justify-center">Save Attendance</button>
            </form>
          </div>

          {/* Distribution Chart */}
          <div className="card lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-slate-800">College Attendance Distribution</h3>
                <p className="text-xs text-slate-500">Overall Average: {analytics?.overall_attendance}% • Below 75%: {analytics?.students_below_75} students</p>
              </div>
            </div>
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics?.distribution || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#2563eb" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Inspect Student Selector (Admin/Teacher) */}
      {user?.role !== 'student' && (
        <div className="card mb-6 flex flex-wrap items-center justify-between gap-4">
          <h3 className="font-semibold text-slate-800">Subject-wise Student Attendance Lookup</h3>
          <select className="input w-72" value={selectedStudentId} onChange={(e) => handleInspectStudent(e.target.value)}>
            <option value="">Choose a student to inspect...</option>
            {students.map((s) => <option key={s.id} value={s.id}>{s.student_id} — {s.full_name}</option>)}
          </select>
        </div>
      )}

      {/* Student Subject-wise Attendance Table */}
      {studentAttendance && (
        <div className="card mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-800">Subject-wise Attendance Breakdown</h3>
              <p className="text-xs text-slate-500">
                Overall: {studentAttendance.overall_present}/{studentAttendance.overall_total} classes ({studentAttendance.overall_attendance}%)
              </p>
            </div>
            <span className={studentAttendance.overall_attendance < 75 ? 'badge-red' : 'badge-green'}>
              {studentAttendance.overall_attendance < 75 ? 'Low Attendance Alert' : 'Good Standing'}
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b">
                <tr>
                  <th className="table-header">Subject</th>
                  <th className="table-header">Conducted</th>
                  <th className="table-header">Present</th>
                  <th className="table-header">Absent</th>
                  <th className="table-header">Percentage</th>
                  <th className="table-header">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {studentAttendance.subjects.map((sub) => (
                  <tr key={sub.subject_id}>
                    <td className="table-cell font-medium">{sub.subject_code} — {sub.subject_name}</td>
                    <td className="table-cell">{sub.total_classes}</td>
                    <td className="table-cell">{sub.present_classes}</td>
                    <td className="table-cell">{sub.absent_classes}</td>
                    <td className="table-cell font-semibold">{sub.attendance_percentage}%</td>
                    <td className="table-cell">
                      <span className={sub.status === 'critical' ? 'badge-red' : sub.status === 'warning' ? 'badge-yellow' : 'badge-green'}>
                        {sub.status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Low Attendance Alerts Table */}
      {user?.role !== 'student' && analytics?.low_attendance_students?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" /> Low Attendance Alerts (&lt; 75%)
          </h3>
          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b">
                <tr>
                  <th className="table-header">Student ID</th>
                  <th className="table-header">Name</th>
                  <th className="table-header">Present / Total</th>
                  <th className="table-header">Attendance %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {analytics.low_attendance_students.map((st) => (
                  <tr key={st.student_id}>
                    <td className="table-cell font-medium">{st.student_code}</td>
                    <td className="table-cell">{st.name}</td>
                    <td className="table-cell">{st.present_classes} / {st.total_classes}</td>
                    <td className="table-cell"><span className="badge-red">{st.attendance_percentage}%</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
