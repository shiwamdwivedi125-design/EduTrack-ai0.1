import React, { useEffect, useState } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { KPICard, LoadingSpinner } from '../components/Common';
import { subjectsAPI, alertsAPI, interventionsAPI, analyticsAPI } from '../services/api';
import toast from 'react-hot-toast';
import { BookOpen, AlertTriangle, ClipboardCheck, Users, Plus } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function TeacherDashboard() {
  const [subjects, setSubjects] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [interventions, setInterventions] = useState([]);
  const [perf, setPerf] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ student_id: '', title: '', description: '', action_taken: '', follow_up_date: '' });

  const loadData = async () => {
    setLoading(true);
    try {
      const [subRes, alRes, ivRes, pfRes] = await Promise.all([
        subjectsAPI.list(),
        alertsAPI.list(),
        interventionsAPI.list(),
        analyticsAPI.performance(),
      ]);
      setSubjects(subRes.data || []);
      setAlerts(alRes.data?.alerts || []);
      setInterventions(ivRes.data?.interventions || []);
      setPerf(pfRes.data);
    } catch {
      toast.error('Failed to load teacher dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAssignIntervention = async (e) => {
    e.preventDefault();
    try {
      await interventionsAPI.create({
        ...form,
        student_id: Number(form.student_id),
      });
      toast.success('Intervention task assigned!');
      setShowModal(false);
      setForm({ student_id: '', title: '', description: '', action_taken: '', follow_up_date: '' });
      loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to assign intervention');
    }
  };

  const handleCompleteIntervention = async (id) => {
    try {
      await interventionsAPI.update(id, { status: 'completed' });
      toast.success('Marked as completed');
      loadData();
    } catch {
      toast.error('Failed to update');
    }
  };

  if (loading) {
    return <DashboardLayout title="Teacher Dashboard"><LoadingSpinner /></DashboardLayout>;
  }

  return (
    <DashboardLayout title="Teacher Dashboard">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard title="Assigned Subjects" value={subjects.length} icon={BookOpen} color="blue" />
        <KPICard title="Students Needing Support" value={alerts.length} icon={AlertTriangle} color="red" />
        <KPICard title="Active Interventions" value={interventions.filter((i) => i.status !== 'completed').length} icon={ClipboardCheck} color="amber" />
        <KPICard title="Avg Subject Score" value={`${perf?.avg_percentage ?? 0}%`} icon={Users} color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Subject-wise Performance */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Subject-wise Average Percentage</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={(perf?.subject_performance || []).slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="subject" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="avg_percentage" fill="#2563eb" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Early Warning Students */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800">Students Needing Academic Support</h3>
            <button onClick={() => setShowModal(true)} className="btn-primary text-xs">
              <Plus className="w-4 h-4" /> Assign Intervention
            </button>
          </div>
          <div className="space-y-2.5 max-h-64 overflow-y-auto">
            {alerts.slice(0, 12).map((a) => (
              <div key={a.id} className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div>
                  <p className="font-medium text-sm text-slate-800">{a.student_name} ({a.student_code})</p>
                  <p className="text-xs text-slate-500">{a.reasons?.[0]}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={a.risk_level === 'high' ? 'badge-red' : 'badge-yellow'}>
                    {a.risk_level} ({a.risk_score})
                  </span>
                  <button
                    onClick={() => {
                      setForm({ ...form, student_id: String(a.student_id), title: `Support for ${a.student_name}` });
                      setShowModal(true);
                    }}
                    className="text-xs text-blue-600 hover:underline font-medium"
                  >
                    Intervene
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Teacher Interventions Tracker */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4">Teacher Intervention Tracker</h3>
        {interventions.length === 0 ? (
          <p className="text-sm text-slate-500 py-6 text-center">No interventions assigned yet. Click "Assign Intervention" to create one.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="table-header">Student</th>
                  <th className="table-header">Title</th>
                  <th className="table-header">Action</th>
                  <th className="table-header">Follow-up</th>
                  <th className="table-header">Status</th>
                  <th className="table-header">Update</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {interventions.map((iv) => (
                  <tr key={iv.id}>
                    <td className="table-cell font-medium">{iv.student_name} ({iv.student_code})</td>
                    <td className="table-cell">{iv.title}</td>
                    <td className="table-cell text-slate-500">{iv.action_taken || iv.description}</td>
                    <td className="table-cell">{iv.follow_up_date || '—'}</td>
                    <td className="table-cell">
                      <span className={iv.status === 'completed' ? 'badge-green' : 'badge-yellow'}>{iv.status}</span>
                    </td>
                    <td className="table-cell">
                      {iv.status !== 'completed' && (
                        <button onClick={() => handleCompleteIntervention(iv.id)} className="text-xs text-blue-600 hover:underline">
                          Mark Done
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Assign Intervention Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
            <h3 className="font-bold text-lg mb-4">Assign Improvement Task / Intervention</h3>
            <form onSubmit={handleAssignIntervention} className="space-y-3">
              <div>
                <label className="label">Student DB ID</label>
                <input
                  type="number"
                  required
                  value={form.student_id}
                  onChange={(e) => setForm({ ...form, student_id: e.target.value })}
                  className="input"
                  placeholder="e.g. 1"
                />
              </div>
              <div>
                <label className="label">Intervention Title</label>
                <input
                  type="text"
                  required
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="input"
                  placeholder="Extra tutoring in DBMS"
                />
              </div>
              <div>
                <label className="label">Recommended Action</label>
                <textarea
                  value={form.action_taken}
                  onChange={(e) => setForm({ ...form, action_taken: e.target.value })}
                  className="input"
                  rows={2}
                  placeholder="Complete weekly practice sheets"
                />
              </div>
              <div>
                <label className="label">Follow-up Date</label>
                <input
                  type="date"
                  value={form.follow_up_date}
                  onChange={(e) => setForm({ ...form, follow_up_date: e.target.value })}
                  className="input"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary">Assign Task</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
