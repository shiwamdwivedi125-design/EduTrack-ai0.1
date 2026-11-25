import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { LoadingSpinner } from '../components/Common';
import { studentsAPI, departmentsAPI, importAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Search, Plus, Upload, Eye, Trash2, ChevronLeft, ChevronRight, FileSpreadsheet } from 'lucide-react';

export default function StudentManagement() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [semFilter, setSemFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const [showAdd, setShowAdd] = useState(false);
  const [newStudent, setNewStudent] = useState({
    full_name: '', email: '', password: 'Student@123', student_id: '', roll_number: '',
    department_id: 1, current_semester: 1, admission_year: 2024, phone: ''
  });

  const [selectedSummary, setSelectedSummary] = useState(null);
  const [importPreview, setImportPreview] = useState(null);

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const res = await studentsAPI.list({
        page, page_size: 15,
        search: search || undefined,
        department_id: deptFilter || undefined,
        semester: semFilter || undefined,
      });
      setStudents(res.data.items || []);
      setTotal(res.data.total || 0);
      setTotalPages(res.data.total_pages || 1);
    } catch {
      toast.error('Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    departmentsAPI.list().then((r) => setDepartments(r.data || [])).catch(() => {});
  }, []);

  useEffect(() => {
    fetchStudents();
  }, [page, search, deptFilter, semFilter]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await studentsAPI.create({
        ...newStudent,
        department_id: Number(newStudent.department_id),
        current_semester: Number(newStudent.current_semester),
        admission_year: Number(newStudent.admission_year),
      });
      toast.success('Student created successfully');
      setShowAdd(false);
      fetchStudents();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create student');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Deactivate this student?')) return;
    try {
      await studentsAPI.delete(id);
      toast.success('Student deactivated');
      fetchStudents();
    } catch {
      toast.error('Failed to deactivate student');
    }
  };

  const handleViewDetails = async (id) => {
    try {
      const res = await studentsAPI.academicSummary(id);
      setSelectedSummary(res.data);
    } catch {
      toast.error('Failed to load student details');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const res = await importAPI.preview('students', file);
      setImportPreview(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to parse file');
    }
    e.target.value = '';
  };

  const handleConfirmImport = async () => {
    if (!importPreview) return;
    try {
      const res = await importAPI.confirm('students', importPreview.valid_rows);
      toast.success(`Imported ${res.data.imported} students (${res.data.skipped} skipped)`);
      setImportPreview(null);
      fetchStudents();
    } catch {
      toast.error('Import failed');
    }
  };

  return (
    <DashboardLayout title="Student Management">
      {/* Toolbar */}
      <div className="card mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          <div className="relative min-w-[220px] flex-1 max-w-xs">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search name, ID, roll..."
              value={search}
              onChange={(e) => { setPage(1); setSearch(e.target.value); }}
              className="input pl-9"
            />
          </div>
          <select value={deptFilter} onChange={(e) => { setPage(1); setDeptFilter(e.target.value); }} className="input w-44">
            <option value="">All Departments</option>
            {departments.map((d) => <option key={d.id} value={d.id}>{d.code} — {d.name}</option>)}
          </select>
          <select value={semFilter} onChange={(e) => { setPage(1); setSemFilter(e.target.value); }} className="input w-36">
            <option value="">All Semesters</option>
            {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => <option key={s} value={s}>Semester {s}</option>)}
          </select>
        </div>

        {user?.role === 'admin' && (
          <div className="flex items-center gap-2">
            <label className="btn-secondary cursor-pointer text-sm">
              <Upload className="w-4 h-4" /> CSV/Excel Import
              <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileUpload} className="hidden" />
            </label>
            <button onClick={() => setShowAdd(true)} className="btn-primary text-sm">
              <Plus className="w-4 h-4" /> Add Student
            </button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="card overflow-hidden p-0">
        {loading ? <LoadingSpinner /> : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="table-header">Student ID</th>
                    <th className="table-header">Name & Email</th>
                    <th className="table-header">Roll No</th>
                    <th className="table-header">Department</th>
                    <th className="table-header">Semester</th>
                    <th className="table-header">Status</th>
                    <th className="table-header">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {students.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-50">
                      <td className="table-cell font-semibold text-blue-600">{s.student_id}</td>
                      <td className="table-cell">
                        <p className="font-medium text-slate-900">{s.full_name}</p>
                        <p className="text-xs text-slate-500">{s.email}</p>
                      </td>
                      <td className="table-cell">{s.roll_number}</td>
                      <td className="table-cell"><span className="badge-blue">{s.department_code}</span></td>
                      <td className="table-cell">Sem {s.current_semester}</td>
                      <td className="table-cell">
                        <span className={s.is_active ? 'badge-green' : 'badge-red'}>
                          {s.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center gap-2">
                          <button onClick={() => handleViewDetails(s.id)} className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg" title="Academic Summary">
                            <Eye className="w-4 h-4" />
                          </button>
                          {user?.role === 'admin' && (
                            <button onClick={() => handleDelete(s.id)} className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg" title="Deactivate">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {/* Pagination */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100 text-sm text-slate-600">
              <span>Showing {students.length} of {total} students (Page {page} of {totalPages})</span>
              <div className="flex items-center gap-2">
                <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="btn-secondary py-1 px-2.5 disabled:opacity-40">
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)} className="btn-secondary py-1 px-2.5 disabled:opacity-40">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Add Student Modal */}
      {showAdd && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl">
            <h3 className="font-bold text-lg mb-4">Add New Student</h3>
            <form onSubmit={handleCreate} className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="label">Full Name</label>
                <input required className="input" value={newStudent.full_name} onChange={(e) => setNewStudent({ ...newStudent, full_name: e.target.value })} />
              </div>
              <div>
                <label className="label">Email</label>
                <input required type="email" className="input" value={newStudent.email} onChange={(e) => setNewStudent({ ...newStudent, email: e.target.value })} />
              </div>
              <div>
                <label className="label">Student ID</label>
                <input required className="input" placeholder="CSE2024001" value={newStudent.student_id} onChange={(e) => setNewStudent({ ...newStudent, student_id: e.target.value })} />
              </div>
              <div>
                <label className="label">Roll Number</label>
                <input required className="input" placeholder="CSE/2024/001" value={newStudent.roll_number} onChange={(e) => setNewStudent({ ...newStudent, roll_number: e.target.value })} />
              </div>
              <div>
                <label className="label">Department</label>
                <select className="input" value={newStudent.department_id} onChange={(e) => setNewStudent({ ...newStudent, department_id: e.target.value })}>
                  {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Semester</label>
                <input type="number" min={1} max={8} className="input" value={newStudent.current_semester} onChange={(e) => setNewStudent({ ...newStudent, current_semester: e.target.value })} />
              </div>
              <div>
                <label className="label">Admission Year</label>
                <input type="number" className="input" value={newStudent.admission_year} onChange={(e) => setNewStudent({ ...newStudent, admission_year: e.target.value })} />
              </div>
              <div className="col-span-2 flex justify-end gap-2 pt-3">
                <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary">Create Student</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Academic Summary Modal */}
      {selectedSummary && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 shadow-xl max-h-[85vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-bold text-lg">{selectedSummary.student.full_name}</h3>
                <p className="text-xs text-slate-500">{selectedSummary.student.student_id} • {selectedSummary.student.department}</p>
              </div>
              <button onClick={() => setSelectedSummary(null)} className="btn-secondary text-xs">Close</button>
            </div>
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-slate-500">Current CGPA</p>
                <p className="text-xl font-bold text-blue-700">{selectedSummary.current_cgpa}</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-500">Risk Level</p>
                <p className="text-xl font-bold uppercase">{selectedSummary.risk?.risk_level}</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-500">Risk Score</p>
                <p className="text-xl font-bold">{selectedSummary.risk?.risk_score}/100</p>
              </div>
            </div>
            <h4 className="font-semibold text-sm mb-2">Marks Overview</h4>
            <table className="w-full text-xs mb-4">
              <thead className="bg-slate-50">
                <tr>
                  <th className="p-2 text-left">Subject</th>
                  <th className="p-2">Internal</th>
                  <th className="p-2">External</th>
                  <th className="p-2">Total</th>
                  <th className="p-2">Grade</th>
                </tr>
              </thead>
              <tbody>
                {(selectedSummary.marks || []).slice(0, 10).map((m, i) => (
                  <tr key={i} className="border-t">
                    <td className="p-2">{m.subject_code} - {m.subject_name}</td>
                    <td className="p-2 text-center">{m.internal}</td>
                    <td className="p-2 text-center">{m.external}</td>
                    <td className="p-2 text-center">{m.total}</td>
                    <td className="p-2 text-center font-bold">{m.grade}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CSV/Excel Import Preview Modal */}
      {importPreview && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 shadow-xl max-h-[85vh] overflow-y-auto">
            <h3 className="font-bold text-lg flex items-center gap-2 mb-3">
              <FileSpreadsheet className="w-5 h-5 text-blue-600" /> Import Preview & Validation
            </h3>
            <div className="grid grid-cols-3 gap-3 mb-4 text-sm">
              <div className="p-3 bg-emerald-50 rounded-lg">Valid Rows: <strong>{importPreview.valid_count}</strong></div>
              <div className="p-3 bg-amber-50 rounded-lg">Duplicates: <strong>{importPreview.duplicate_count}</strong></div>
              <div className="p-3 bg-red-50 rounded-lg">Errors: <strong>{importPreview.error_count}</strong></div>
            </div>
            {importPreview.errors?.length > 0 && (
              <div className="mb-4 p-3 bg-red-50 rounded-lg text-xs text-red-700">
                <p className="font-semibold mb-1">Row Errors:</p>
                {importPreview.errors.map((e, i) => <p key={i}>Row {e.row}: {e.errors.join(', ')}</p>)}
              </div>
            )}
            <div className="flex justify-end gap-2">
              <button onClick={() => setImportPreview(null)} className="btn-secondary">Cancel</button>
              <button onClick={handleConfirmImport} disabled={importPreview.valid_count === 0} className="btn-primary">
                Confirm Import ({importPreview.valid_count} rows)
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
