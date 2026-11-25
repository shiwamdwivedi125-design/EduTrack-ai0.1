import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { KPICard, LoadingSpinner } from '../components/Common';
import { placementAPI, studentsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Briefcase, Code2, Award, Plus, Trash2 } from 'lucide-react';

export default function PlacementReadiness() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [form, setForm] = useState({
    technical_score: 60, aptitude_score: 60, projects_count: 2,
    internships_count: 0, certifications_count: 1, mock_interviews: 2
  });
  const [newSkill, setNewSkill] = useState('');
  const [loading, setLoading] = useState(true);

  const loadPlacement = async (sid) => {
    setLoading(true);
    try {
      const res = await placementAPI.get(sid || undefined);
      setData(res.data);
      setForm({
        technical_score: res.data.technical_score,
        aptitude_score: res.data.aptitude_score,
        projects_count: res.data.projects_count,
        internships_count: res.data.internships_count,
        certifications_count: res.data.certifications_count,
        mock_interviews: res.data.mock_interviews,
      });
    } catch {
      toast.error('Failed to load placement data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role !== 'student') {
      studentsAPI.list({ page: 1, page_size: 25 }).then((r) => {
        const list = r.data.items || [];
        setStudents(list);
        if (list.length > 0) {
          setSelectedStudentId(list[0].id);
          loadPlacement(list[0].id);
        } else loadPlacement();
      });
    } else {
      loadPlacement();
    }
  }, []);

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await placementAPI.update({
        ...form,
        student_id: selectedStudentId ? Number(selectedStudentId) : undefined,
        technical_score: Number(form.technical_score),
        aptitude_score: Number(form.aptitude_score),
        projects_count: Number(form.projects_count),
        internships_count: Number(form.internships_count),
        certifications_count: Number(form.certifications_count),
        mock_interviews: Number(form.mock_interviews),
      });
      toast.success('Placement readiness updated!');
      loadPlacement(selectedStudentId);
    } catch {
      toast.error('Update failed');
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkill.trim()) return;
    try {
      await placementAPI.addSkill({ skill_name: newSkill.trim(), proficiency_level: 4 });
      setNewSkill('');
      loadPlacement(selectedStudentId);
      toast.success('Skill added');
    } catch {
      toast.error('Could not add skill');
    }
  };

  const handleDeleteSkill = async (id) => {
    try {
      await placementAPI.deleteSkill(id);
      loadPlacement(selectedStudentId);
    } catch {}
  };

  if (loading) {
    return <DashboardLayout title="Placement Readiness Tracker"><LoadingSpinner /></DashboardLayout>;
  }

  return (
    <DashboardLayout title="Placement Readiness Tracker">
      {user?.role !== 'student' && (
        <div className="card mb-6 flex items-center justify-between">
          <span className="font-semibold text-sm text-slate-700">Inspect Student Placement Readiness:</span>
          <select className="input w-72" value={selectedStudentId} onChange={(e) => { setSelectedStudentId(e.target.value); loadPlacement(e.target.value); }}>
            {students.map((s) => <option key={s.id} value={s.id}>{s.student_id} — {s.full_name}</option>)}
          </select>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <KPICard title="Overall Readiness" value={`${data?.overall_readiness ?? 0}%`} icon={Briefcase} color="blue" />
        <KPICard title="CGPA Score" value={`${data?.cgpa_score ?? 0}%`} subtitle={`CGPA: ${data?.cgpa ?? 0}`} icon={Award} color="green" />
        <KPICard title="Technical Score" value={`${data?.technical_score ?? 0}%`} icon={Code2} color="purple" />
        <KPICard title="Aptitude Score" value={`${data?.aptitude_score ?? 0}%`} icon={Briefcase} color="amber" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Update Preparation Metrics</h3>
          <form onSubmit={handleUpdate} className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Technical Score (%)</label>
              <input type="number" min={0} max={100} className="input" value={form.technical_score} onChange={(e) => setForm({ ...form, technical_score: e.target.value })} />
            </div>
            <div>
              <label className="label">Aptitude Score (%)</label>
              <input type="number" min={0} max={100} className="input" value={form.aptitude_score} onChange={(e) => setForm({ ...form, aptitude_score: e.target.value })} />
            </div>
            <div>
              <label className="label">Projects Completed</label>
              <input type="number" min={0} className="input" value={form.projects_count} onChange={(e) => setForm({ ...form, projects_count: e.target.value })} />
            </div>
            <div>
              <label className="label">Internships</label>
              <input type="number" min={0} className="input" value={form.internships_count} onChange={(e) => setForm({ ...form, internships_count: e.target.value })} />
            </div>
            <div>
              <label className="label">Certifications</label>
              <input type="number" min={0} className="input" value={form.certifications_count} onChange={(e) => setForm({ ...form, certifications_count: e.target.value })} />
            </div>
            <div>
              <label className="label">Mock Interviews</label>
              <input type="number" min={0} className="input" value={form.mock_interviews} onChange={(e) => setForm({ ...form, mock_interviews: e.target.value })} />
            </div>
            <div className="col-span-2 pt-2">
              <button type="submit" className="btn-primary">Save Progress</button>
            </div>
          </form>
          <p className="text-xs text-slate-400 mt-4 italic">{data?.disclaimer}</p>
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Technical Skills & Target Companies</h3>
          {user?.role === 'student' && (
            <form onSubmit={handleAddSkill} className="flex gap-2 mb-4">
              <input className="input" placeholder="Add skill (e.g. Python, React, SQL)..." value={newSkill} onChange={(e) => setNewSkill(e.target.value)} />
              <button type="submit" className="btn-primary shrink-0"><Plus className="w-4 h-4" /> Add</button>
            </form>
          )}
          <div className="flex flex-wrap gap-2 mb-6">
            {(data?.skills || []).length === 0 ? (
              <p className="text-xs text-slate-500">No skills added yet.</p>
            ) : (
              data.skills.map((sk) => (
                <span key={sk.id} className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-medium">
                  {sk.skill_name}
                  {user?.role === 'student' && (
                    <button onClick={() => handleDeleteSkill(sk.id)} className="hover:text-red-600"><Trash2 className="w-3 h-3" /></button>
                  )}
                </span>
              ))
            )}
          </div>
          <h4 className="font-semibold text-sm text-slate-700 mb-2">Target Companies</h4>
          <div className="flex flex-wrap gap-2">
            {(data?.target_companies || []).map((c) => (
              <span key={c} className="badge-green">{c}</span>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
