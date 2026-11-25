import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { LoadingSpinner } from '../components/Common';
import { marksAPI, studentsAPI, subjectsAPI, semestersAPI, importAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { FileSpreadsheet, Upload, Plus } from 'lucide-react';

export default function MarksManagement() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [semesters, setSemesters] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [studentMarks, setStudentMarks] = useState([]);
  const [form, setForm] = useState({ student_id: '', subject_id: '', semester_id: '', internal_marks: '', external_marks: '' });
  const [importPreview, setImportPreview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        if (user?.role === 'student') {
          const prof = await studentsAPI.myProfile();
          setSelectedStudentId(prof.data.id);
          const mRes = await marksAPI.studentMarks(prof.data.id);
          setStudentMarks(mRes.data.marks || []);
        } else {
          const [stRes, suRes, seRes] = await Promise.all([
            studentsAPI.list({ page: 1, page_size: 50 }),
            subjectsAPI.list(),
            semestersAPI.list(),
          ]);
          const list = stRes.data.items || [];
          setStudents(list);
          setSubjects(suRes.data || []);
          setSemesters(seRes.data || []);
          if (list.length > 0) {
            setSelectedStudentId(list[0].id);
            const mRes = await marksAPI.studentMarks(list[0].id);
            setStudentMarks(mRes.data.marks || []);
          }
        }
      } catch {
        toast.error('Failed to load marks data');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const fetchStudentMarks = async (sid) => {
    setSelectedStudentId(sid);
    if (!sid) return setStudentMarks([]);
    try {
      const res = await marksAPI.studentMarks(sid);
      setStudentMarks(res.data.marks || []);
    } catch {
      toast.error('Failed to fetch marks');
    }
  };

  const handleSaveMarks = async (e) => {
    e.preventDefault();
    try {
      const res = await marksAPI.add({
        student_id: Number(form.student_id),
        subject_id: Number(form.subject_id),
        semester_id: Number(form.semester_id),
        internal_marks: Number(form.internal_marks),
        external_marks: Number(form.external_marks),
      });
      toast.success(`Marks saved! Grade: ${res.data.marks.grade} (${res.data.marks.percentage}%)`);
      if (Number(form.student_id) === Number(selectedStudentId)) {
        fetchStudentMarks(selectedStudentId);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save marks');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const res = await importAPI.preview('marks', file);
      setImportPreview(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to parse file');
    }
    e.target.value = '';
  };

  const handleConfirmImport = async () => {
    try {
      const res = await importAPI.confirm('marks', importPreview.valid_rows);
      toast.success(`Imported ${res.data.imported} marks records (${res.data.skipped} skipped)`);
      setImportPreview(null);
      if (selectedStudentId) fetchStudentMarks(selectedStudentId);
    } catch {
      toast.error('Import failed');
    }
  };

  if (loading) {
    return <DashboardLayout title="Marks & Grades Management"><LoadingSpinner /></DashboardLayout>;
  }

  return (
    <DashboardLayout title="Marks & Grades Management">
      {user?.role !== 'student' && (
        <div className="card mb-6">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
              <Plus className="w-4 h-4 text-blue-600" /> Enter / Update Internal & External Marks
            </h3>
            <label className="btn-secondary cursor-pointer text-xs">
              <Upload className="w-4 h-4" /> Bulk CSV/Excel Upload
              <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
          <form onSubmit={handleSaveMarks} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 items-end">
            <div>
              <label className="label">Student</label>
              <select required className="input" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })}>
                <option value="">Select...</option>
                {students.map((s) => <option key={s.id} value={s.id}>{s.student_id} - {s.full_name}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Subject</label>
              <select required className="input" value={form.subject_id} onChange={(e) => setForm({ ...form, subject_id: e.target.value })}>
                <option value="">Select...</option>
                {subjects.map((s) => <option key={s.id} value={s.id}>{s.code} - {s.name}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Semester</label>
              <select required className="input" value={form.semester_id} onChange={(e) => setForm({ ...form, semester_id: e.target.value })}>
                <option value="">Select...</option>
                {semesters.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Internal (Max 30)</label>
              <input type="number" step="0.5" min={0} max={30} required className="input" value={form.internal_marks} onChange={(e) => setForm({ ...form, internal_marks: e.target.value })} />
            </div>
            <div>
              <label className="label">External (Max 70)</label>
              <input type="number" step="0.5" min={0} max={70} required className="input" value={form.external_marks} onChange={(e) => setForm({ ...form, external_marks: e.target.value })} />
            </div>
            <button type="submit" className="btn-primary justify-center">Save & Calculate</button>
          </form>
        </div>
      )}

      {/* Marks Table */}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h3 className="font-semibold text-slate-800 flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-blue-600" /> Subject-wise Marks & Grade Sheet
          </h3>
          {user?.role !== 'student' && (
            <select className="input w-72" value={selectedStudentId} onChange={(e) => fetchStudentMarks(e.target.value)}>
              {students.map((s) => <option key={s.id} value={s.id}>{s.student_id} — {s.full_name}</option>)}
            </select>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b">
              <tr>
                <th className="table-header">Subject</th>
                <th className="table-header">Semester</th>
                <th className="table-header">Internal</th>
                <th className="table-header">External</th>
                <th className="table-header">Total / Max</th>
                <th className="table-header">Percentage</th>
                <th className="table-header">Grade</th>
                <th className="table-header">Credits</th>
                <th className="table-header">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {studentMarks.map((m) => (
                <tr key={m.id}>
                  <td className="table-cell font-medium">{m.subject_code} — {m.subject_name}</td>
                  <td className="table-cell">{m.semester_name}</td>
                  <td className="table-cell">{m.internal_marks}</td>
                  <td className="table-cell">{m.external_marks}</td>
                  <td className="table-cell font-semibold">{m.total_marks} / {m.max_marks}</td>
                  <td className="table-cell">{m.percentage}%</td>
                  <td className="table-cell font-bold text-blue-700">{m.grade} ({m.grade_points})</td>
                  <td className="table-cell">{m.credits}</td>
                  <td className="table-cell">
                    <span className={m.is_pass ? 'badge-green' : 'badge-red'}>
                      {m.is_pass ? 'PASS' : 'FAIL'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Import Preview Modal */}
      {importPreview && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl">
            <h3 className="font-bold text-lg mb-3">Marks Import Preview</h3>
            <div className="grid grid-cols-3 gap-3 mb-4 text-sm">
              <div className="p-3 bg-emerald-50 rounded-lg">Valid: <strong>{importPreview.valid_count}</strong></div>
              <div className="p-3 bg-amber-50 rounded-lg">Duplicates: <strong>{importPreview.duplicate_count}</strong></div>
              <div className="p-3 bg-red-50 rounded-lg">Errors: <strong>{importPreview.error_count}</strong></div>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setImportPreview(null)} className="btn-secondary">Cancel</button>
              <button onClick={handleConfirmImport} className="btn-primary">Confirm Import</button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
