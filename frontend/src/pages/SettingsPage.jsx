import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { gradingAPI, auditAPI, departmentsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Settings, Plus, Trash2, Shield } from 'lucide-react';

export default function SettingsPage() {
  const { user } = useAuth();
  const [rules, setRules] = useState([]);
  const [logs, setLogs] = useState([]);
  const [depts, setDepts] = useState([]);
  const [ruleForm, setRuleForm] = useState({ grade: '', min_percentage: '', max_percentage: '', grade_points: '', is_pass: true });

  const loadData = async () => {
    try {
      const [rRes, dRes] = await Promise.all([gradingAPI.list(), departmentsAPI.list()]);
      setRules(rRes.data || []);
      setDepts(dRes.data || []);
      if (user?.role === 'admin') {
        const aRes = await auditAPI.list();
        setLogs(aRes.data || []);
      }
    } catch {}
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddRule = async (e) => {
    e.preventDefault();
    try {
      await gradingAPI.create(ruleForm);
      toast.success('Grading rule added');
      setRuleForm({ grade: '', min_percentage: '', max_percentage: '', grade_points: '', is_pass: true });
      loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add rule');
    }
  };

  const handleDeleteRule = async (id) => {
    try {
      await gradingAPI.delete(id);
      toast.success('Rule deleted');
      loadData();
    } catch {}
  };

  return (
    <DashboardLayout title="Institutional Settings & Grading Rules">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Configurable Grading Rules */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-600" /> Configurable Institutional Grading Rules
          </h3>
          {user?.role === 'admin' && (
            <form onSubmit={handleAddRule} className="grid grid-cols-5 gap-2 mb-4 items-end">
              <div><label className="label text-xs">Grade</label><input required className="input" placeholder="A" value={ruleForm.grade} onChange={(e) => setRuleForm({ ...ruleForm, grade: e.target.value })} /></div>
              <div><label className="label text-xs">Min %</label><input required type="number" className="input" value={ruleForm.min_percentage} onChange={(e) => setRuleForm({ ...ruleForm, min_percentage: e.target.value })} /></div>
              <div><label className="label text-xs">Max %</label><input required type="number" className="input" value={ruleForm.max_percentage} onChange={(e) => setRuleForm({ ...ruleForm, max_percentage: e.target.value })} /></div>
              <div><label className="label text-xs">Points</label><input required type="number" step="0.5" className="input" value={ruleForm.grade_points} onChange={(e) => setRuleForm({ ...ruleForm, grade_points: e.target.value })} /></div>
              <button type="submit" className="btn-primary justify-center text-xs py-2"><Plus className="w-4 h-4" /></button>
            </form>
          )}
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b">
              <tr>
                <th className="table-header">Grade</th>
                <th className="table-header">Range (%)</th>
                <th className="table-header">Points</th>
                <th className="table-header">Pass</th>
                {user?.role === 'admin' && <th className="table-header">Action</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rules.map((r) => (
                <tr key={r.id}>
                  <td className="table-cell font-bold text-blue-700">{r.grade}</td>
                  <td className="table-cell">{r.min_percentage}% – {r.max_percentage}%</td>
                  <td className="table-cell">{r.grade_points}</td>
                  <td className="table-cell"><span className={r.is_pass ? 'badge-green' : 'badge-red'}>{r.is_pass ? 'Yes' : 'No'}</span></td>
                  {user?.role === 'admin' && (
                    <td className="table-cell">
                      <button onClick={() => handleDeleteRule(r.id)} className="text-red-500 hover:text-red-700"><Trash2 className="w-4 h-4" /></button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Departments Overview */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">Departments</h3>
          <div className="space-y-3">
            {depts.map((d) => (
              <div key={d.id} className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-sm text-slate-900">{d.name} ({d.code})</p>
                  <p className="text-xs text-slate-500">HOD: {d.hod_name || 'N/A'}</p>
                </div>
                <span className="badge-blue">{d.students_count} Students</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Audit Logs (Admin) */}
      {user?.role === 'admin' && (
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-600" /> Security Audit Logs
          </h3>
          <div className="overflow-x-auto max-h-64 overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="bg-slate-50 border-b">
                <tr>
                  <th className="table-header">Action</th>
                  <th className="table-header">Resource</th>
                  <th className="table-header">User ID</th>
                  <th className="table-header">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((l) => (
                  <tr key={l.id}>
                    <td className="table-cell font-medium">{l.action}</td>
                    <td className="table-cell">{l.resource || 'system'}</td>
                    <td className="table-cell">{l.user_id}</td>
                    <td className="table-cell text-slate-400">{l.created_at}</td>
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
