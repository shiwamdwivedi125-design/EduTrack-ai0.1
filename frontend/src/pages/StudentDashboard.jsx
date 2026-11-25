import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../layouts/DashboardLayout';
import { KPICard, LoadingSpinner } from '../components/Common';
import { studentsAPI, placementAPI, goalsAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Award, CalendarCheck, AlertTriangle, Briefcase, Brain, Trophy } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar } from 'recharts';

export default function StudentDashboard() {
  const [summary, setSummary] = useState(null);
  const [placement, setPlacement] = useState(null);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const profRes = await studentsAPI.myProfile();
        const sid = profRes.data.id;
        const [sumRes, plRes, gRes] = await Promise.all([
          studentsAPI.academicSummary(sid),
          placementAPI.get(sid).catch(() => ({ data: null })),
          goalsAPI.list().catch(() => ({ data: { goals: [] } })),
        ]);
        setSummary(sumRes.data);
        setPlacement(plRes.data);
        setGoals(gRes.data?.goals || []);
      } catch {
        toast.error('Failed to load student dashboard');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return <DashboardLayout title="Student Dashboard"><LoadingSpinner /></DashboardLayout>;
  }

  const student = summary?.student || {};
  const attList = summary?.attendance || [];
  const overallAtt = attList.length
    ? (attList.reduce((acc, a) => acc + a.attendance_percentage, 0) / attList.length).toFixed(1)
    : 0;
  const risk = summary?.risk || {};

  return (
    <DashboardLayout title="Student Dashboard">
      {/* Profile Banner */}
      <div className="bg-gradient-to-r from-blue-700 to-indigo-800 rounded-2xl p-6 text-white mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">{student.full_name}</h2>
          <p className="text-blue-100 text-sm mt-1">
            ID: {student.student_id} • Roll: {student.roll_number} • {student.department} • Semester {student.current_semester}
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/study-planner" className="bg-white text-blue-800 px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-1.5 hover:bg-blue-50">
            <Brain className="w-4 h-4" /> AI Study Planner
          </Link>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard title="Current CGPA" value={summary?.current_cgpa ?? 0} subtitle="Out of 10.0" icon={Award} color="blue" />
        <KPICard title="Average Attendance" value={`${overallAtt}%`} subtitle="Target: 75%+" icon={CalendarCheck} color="green" />
        <KPICard title="Risk Status" value={(risk.risk_level || 'low').toUpperCase()} subtitle={`Score: ${risk.risk_score ?? 0}/100`} icon={AlertTriangle} color={risk.risk_level === 'high' ? 'red' : risk.risk_level === 'moderate' ? 'amber' : 'green'} />
        <KPICard title="Placement Readiness" value={`${placement?.overall_readiness ?? 0}%`} icon={Briefcase} color="purple" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Before vs After Semester Comparison (SGPA & CGPA)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary?.cgpa_history || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="semester" />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Line type="monotone" dataKey="sgpa" name="SGPA" stroke="#2563eb" strokeWidth={3} />
                <Line type="monotone" dataKey="cgpa" name="CGPA" stroke="#10b981" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Subject-wise Attendance (%)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={attList}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="subject_code" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="attendance_percentage" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Explainable Alerts & Goals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">Academic Alerts & Recommendations</h3>
          {(!risk.reasons || risk.reasons.length === 0) ? (
            <p className="text-sm text-emerald-700 bg-emerald-50 p-4 rounded-lg">Great job! You currently have no academic risk alerts.</p>
          ) : (
            <div className="space-y-3">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Reasons</p>
                <ul className="list-disc pl-5 text-sm text-red-700 space-y-1">
                  {risk.reasons.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Recommended Actions</p>
                <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                  {(risk.recommendations || []).map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
              <p className="text-xs text-slate-400 italic">{risk.disclaimer}</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
              <Trophy className="w-4 h-4 text-amber-500" /> Weekly Goals
            </h3>
            <Link to="/goals" className="text-xs text-blue-600 hover:underline font-medium">Manage Goals →</Link>
          </div>
          {goals.length === 0 ? (
            <p className="text-sm text-slate-500 py-4">No goals set yet. Create weekly study goals to earn achievement badges!</p>
          ) : (
            <div className="space-y-2">
              {goals.slice(0, 4).map((g) => (
                <div key={g.id} className="p-3 rounded-lg bg-slate-50 flex items-center justify-between text-sm">
                  <span>{g.title}</span>
                  <span className={g.is_completed ? 'badge-green' : 'badge-blue'}>
                    {g.is_completed ? 'Completed' : 'In Progress'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
