import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { LoadingSpinner } from '../components/Common';
import { goalsAPI, studentsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Trophy, Plus, CheckCircle2, Trash2, Award } from 'lucide-react';

export default function GoalsAndAchievements() {
  const { user } = useAuth();
  const [goals, setGoals] = useState([]);
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState({ title: '', description: '', target_value: '8.5', goal_type: 'cgpa', deadline: '', student_id: '' });
  const [loading, setLoading] = useState(true);

  const loadGoals = async () => {
    setLoading(true);
    try {
      const res = await goalsAPI.list();
      setGoals(res.data?.goals || []);
      if (user?.role !== 'student') {
        const stRes = await studentsAPI.list({ page: 1, page_size: 20 });
        setStudents(stRes.data.items || []);
        if (stRes.data.items?.length > 0) setForm((f) => ({ ...f, student_id: stRes.data.items[0].id }));
      }
    } catch {
      toast.error('Failed to load goals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGoals();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await goalsAPI.create({
        ...form,
        target_value: form.target_value ? Number(form.target_value) : null,
        student_id: user?.role === 'student' ? undefined : Number(form.student_id),
      });
      toast.success('Goal created!');
      setForm({ ...form, title: '', description: '' });
      loadGoals();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create goal');
    }
  };

  const handleComplete = async (id) => {
    try {
      const res = await goalsAPI.complete(id);
      toast.success(res.data.message);
      loadGoals();
    } catch {
      toast.error('Failed to update goal');
    }
  };

  const handleDelete = async (id) => {
    try {
      await goalsAPI.delete(id);
      toast.success('Goal deleted');
      loadGoals();
    } catch {
      toast.error('Failed to delete');
    }
  };

  const completedCount = goals.filter((g) => g.is_completed).length;

  const badges = [
    { name: 'Goal Setter', desc: 'Created your first academic goal', earned: goals.length >= 1, icon: '🎯' },
    { name: 'Achiever', desc: 'Completed at least 1 study goal', earned: completedCount >= 1, icon: '🏆' },
    { name: 'Consistent Learner', desc: 'Completed 3+ academic goals', earned: completedCount >= 3, icon: '⭐' },
    { name: 'Goal Champion', desc: 'Completed 5+ academic goals', earned: completedCount >= 5, icon: '🥇' },
  ];

  if (loading) {
    return <DashboardLayout title="Goals & Achievements"><LoadingSpinner /></DashboardLayout>;
  }

  return (
    <DashboardLayout title="Goals & Achievements">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Goal */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Plus className="w-4 h-4 text-blue-600" /> Set New Academic Goal
          </h3>
          <form onSubmit={handleCreate} className="space-y-3">
            {user?.role !== 'student' && (
              <div>
                <label className="label">Assign to Student</label>
                <select className="input" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })}>
                  {students.map((s) => <option key={s.id} value={s.id}>{s.student_id} — {s.full_name}</option>)}
                </select>
              </div>
            )}
            <div>
              <label className="label">Goal Title</label>
              <input required className="input" placeholder="e.g. Score 8.5+ SGPA this semester" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div>
              <label className="label">Description</label>
              <textarea rows={2} className="input" placeholder="Action steps..." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Goal Type</label>
                <select className="input" value={form.goal_type} onChange={(e) => setForm({ ...form, goal_type: e.target.value })}>
                  <option value="cgpa">CGPA / SGPA</option>
                  <option value="attendance">Attendance %</option>
                  <option value="marks">Subject Marks</option>
                  <option value="skill">Skill / Project</option>
                </select>
              </div>
              <div>
                <label className="label">Target Value</label>
                <input type="number" step="0.1" className="input" value={form.target_value} onChange={(e) => setForm({ ...form, target_value: e.target.value })} />
              </div>
            </div>
            <div>
              <label className="label">Deadline</label>
              <input type="date" className="input" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} />
            </div>
            <button type="submit" className="btn-primary w-full justify-center">Create Goal</button>
          </form>
        </div>

        {/* Goals List & Badges */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-500" /> Achievement Badges
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {badges.map((b) => (
                <div key={b.name} className={`p-3 rounded-xl border text-center ${b.earned ? 'bg-amber-50 border-amber-200' : 'bg-slate-50 border-slate-200 opacity-50'}`}>
                  <div className="text-2xl mb-1">{b.icon}</div>
                  <p className="font-semibold text-xs text-slate-900">{b.name}</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">{b.desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <Trophy className="w-5 h-5 text-blue-600" /> My Study Goals ({completedCount}/{goals.length} completed)
            </h3>
            {goals.length === 0 ? (
              <p className="text-sm text-slate-500 py-6 text-center">No goals created yet.</p>
            ) : (
              <div className="space-y-3">
                {goals.map((g) => (
                  <div key={g.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-900">{g.title}</span>
                        <span className="badge-blue uppercase">{g.goal_type}</span>
                        {g.is_completed && <span className="badge-green">{g.badge_earned || 'Completed'}</span>}
                      </div>
                      {g.description && <p className="text-xs text-slate-500 mt-1">{g.description}</p>}
                      {g.deadline && <p className="text-[11px] text-slate-400 mt-1">Deadline: {g.deadline}</p>}
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {!g.is_completed && (
                        <button onClick={() => handleComplete(g.id)} className="btn-secondary text-xs py-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Complete
                        </button>
                      )}
                      <button onClick={() => handleDelete(g.id)} className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
