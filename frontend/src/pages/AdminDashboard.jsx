import React, { useEffect, useState } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { KPICard, LoadingSpinner } from '../components/Common';
import { analyticsAPI, alertsAPI } from '../services/api';
import toast from 'react-hot-toast';
import {
  Users, UserCheck, GraduationCap, AlertTriangle, Award,
  CalendarCheck, BookOpen, Building2
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, LineChart, Line, ScatterChart, Scatter, Legend
} from 'recharts';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

export default function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [perf, setPerf] = useState(null);
  const [att, setAtt] = useState(null);
  const [risk, setRisk] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [ov, pf, at, rk, st] = await Promise.all([
        analyticsAPI.overview(),
        analyticsAPI.performance(),
        analyticsAPI.attendance(),
        analyticsAPI.riskSummary(),
        analyticsAPI.stats(),
      ]);
      setOverview(ov.data);
      setPerf(pf.data);
      setAtt(at.data);
      setRisk(rk.data);
      setStats(st.data);
    } catch (err) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  if (loading) {
    return <DashboardLayout title="Admin Dashboard"><LoadingSpinner /></DashboardLayout>;
  }

  // Build Attendance vs Academic Performance scatter data from top_rankings
  const scatterData = (stats?.top_rankings || []).map((r) => ({
    name: r.name,
    attendance: r.attendance_pct,
    cgpa: r.cgpa,
  }));

  // Monthly academic progress (derived from semester performance)
  const monthlyProgress = (perf?.semester_performance || []).map((s, idx) => ({
    month: `Month ${idx + 1} (${s.semester})`,
    avg_sgpa: s.avg_sgpa,
    target: 7.5,
  }));

  return (
    <DashboardLayout title="Admin Dashboard">
      {/* 8 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard title="Total Students" value={overview?.total_students ?? 0} icon={Users} color="blue" />
        <KPICard title="Active Students" value={overview?.active_students ?? 0} icon={UserCheck} color="green" />
        <KPICard title="Completed Students" value={overview?.completed_students ?? 0} icon={GraduationCap} color="indigo" />
        <KPICard title="Students Needing Support" value={overview?.students_needing_support ?? 0} subtitle={`${overview?.high_risk_students ?? 0} High Risk`} icon={AlertTriangle} color="red" />
        <KPICard title="Average CGPA" value={overview?.average_cgpa ?? 0} subtitle="Out of 10.0" icon={Award} color="purple" />
        <KPICard title="Average Attendance" value={`${overview?.average_attendance ?? 0}%`} icon={CalendarCheck} color="green" />
        <KPICard title="Total Teachers" value={overview?.total_teachers ?? 0} icon={BookOpen} color="blue" />
        <KPICard title="Total Departments" value={overview?.total_departments ?? 0} icon={Building2} color="amber" />
      </div>

      {/* 9 Interactive Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* 1. Student Performance Distribution (CGPA) */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Student Performance Distribution (CGPA)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={perf?.cgpa_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Department-wise Performance */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Department-wise Performance (Avg CGPA)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={perf?.department_performance || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="department" />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Bar dataKey="avg_cgpa" fill="#10b981" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Semester-wise CGPA */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Semester-wise SGPA Trend</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={perf?.semester_performance || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="semester" />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Line type="monotone" dataKey="avg_sgpa" stroke="#2563eb" strokeWidth={3} dot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Attendance Distribution */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Attendance Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={att?.distribution || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#f59e0b" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 5. Subject-wise Average Marks */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Subject-wise Average Marks (%)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={(perf?.subject_performance || []).slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="subject" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="avg_percentage" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 6. Monthly Academic Progress */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Academic Progress vs Target</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyProgress}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="avg_sgpa" name="Actual SGPA" stroke="#2563eb" strokeWidth={2} />
                <Line type="monotone" dataKey="target" name="Benchmark" stroke="#10b981" strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 7. Pass vs Fail Distribution */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Pass vs Fail Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={perf?.pass_fail || []} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={85} label>
                  {(perf?.pass_fail || []).map((_, index) => (
                    <Cell key={index} fill={index === 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 8. Attendance vs Academic Performance */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Attendance vs Academic Performance (CGPA)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" dataKey="attendance" name="Attendance %" domain={[40, 100]} />
                <YAxis type="number" dataKey="cgpa" name="CGPA" domain={[0, 10]} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Students" data={scatterData} fill="#2563eb" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 9. Students Needing Support (Risk Distribution) */}
        <div className="card lg:col-span-2">
          <h3 className="font-semibold text-slate-800 mb-4">Students Needing Support (Early Warning Distribution)</h3>
          <div className="grid md:grid-cols-2 gap-6 items-center">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={risk?.distribution || []} dataKey="count" nameKey="level" cx="50%" cy="50%" outerRadius={85} label>
                    {(risk?.distribution || []).map((entry, idx) => (
                      <Cell key={idx} fill={entry.color || COLORS[idx]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-3">
              <p className="text-xs text-slate-500 bg-amber-50 border border-amber-200 rounded-lg p-3">
                {risk?.disclaimer}
              </p>
              <div className="space-y-2 max-h-44 overflow-y-auto">
                {(risk?.top_risk_students || []).slice(0, 5).map((s) => (
                  <div key={s.student_id} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-sm">
                    <div>
                      <p className="font-medium text-slate-800">{s.name} ({s.student_code})</p>
                      <p className="text-xs text-slate-500">{s.reasons?.[0]}</p>
                    </div>
                    <span className={s.risk_level === 'high' ? 'badge-red' : 'badge-yellow'}>
                      {s.risk_level.toUpperCase()} ({s.risk_score})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
