import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { reportsAPI, studentsAPI, departmentsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { FileText, Download, FileSpreadsheet } from 'lucide-react';

export default function AcademicReports() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [selectedDept, setSelectedDept] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (user?.role === 'student') {
      studentsAPI.myProfile().then((r) => setSelectedStudent(r.data.id)).catch(() => {});
    } else {
      studentsAPI.list({ page: 1, page_size: 50 }).then((r) => {
        const list = r.data.items || [];
        setStudents(list);
        if (list.length > 0) setSelectedStudent(list[0].id);
      }).catch(() => {});
      departmentsAPI.list().then((r) => {
        setDepartments(r.data || []);
        if (r.data?.length > 0) setSelectedDept(r.data[0].id);
      }).catch(() => {});
    }
  }, []);

  const triggerDownload = async (reportType, format, extraParams = {}) => {
    setDownloading(true);
    try {
      const res = await reportsAPI.download(reportType, format, extraParams);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `edutrack_${reportType}_report.${format === 'pdf' ? 'pdf' : 'xlsx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success(`Downloaded ${reportType} ${format.toUpperCase()} report!`);
    } catch {
      toast.error('Failed to generate report');
    } finally {
      setDownloading(false);
    }
  };

  const reportCards = [
    {
      title: 'Individual Student Report',
      desc: 'Detailed subject-wise marks, percentages, grades, and CGPA summary.',
      type: 'student',
      params: { student_id: selectedStudent },
      extra: user?.role !== 'student' && (
        <select className="input mb-3" value={selectedStudent} onChange={(e) => setSelectedStudent(e.target.value)}>
          {students.map((s) => <option key={s.id} value={s.id}>{s.student_id} — {s.full_name}</option>)}
        </select>
      ),
    },
    ...(user?.role !== 'student' ? [
      {
        title: 'College Analytics Report',
        desc: 'Institution-wide CGPA, semester backlogs, and student summary.',
        type: 'college',
        params: {},
      },
      {
        title: 'Department Performance Report',
        desc: 'Filtered academic metrics for a specific department.',
        type: 'department',
        params: { department_id: selectedDept },
        extra: (
          <select className="input mb-3" value={selectedDept} onChange={(e) => setSelectedDept(e.target.value)}>
            {departments.map((d) => <option key={d.id} value={d.id}>{d.code} — {d.name}</option>)}
          </select>
        ),
      },
      {
        title: 'Attendance Summary Report',
        desc: 'Student attendance percentages, conducted classes, and low-attendance tracking.',
        type: 'attendance',
        params: {},
      },
      {
        title: 'Academic Risk & Early Warning Report',
        desc: 'Active high/moderate risk alerts, risk scores, and primary warning factors.',
        type: 'risk',
        params: {},
      },
    ] : []),
  ];

  return (
    <DashboardLayout title="Academic Reports (PDF & Excel)">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reportCards.map((rc) => (
          <div key={rc.title} className="card flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2.5 mb-2">
                <FileText className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-lg text-slate-900">{rc.title}</h3>
              </div>
              <p className="text-sm text-slate-500 mb-4">{rc.desc}</p>
              {rc.extra}
            </div>
            <div className="flex gap-3 pt-2">
              <button
                disabled={downloading}
                onClick={() => triggerDownload(rc.type, 'pdf', rc.params)}
                className="btn-primary text-sm flex-1 justify-center"
              >
                <Download className="w-4 h-4" /> Download PDF
              </button>
              <button
                disabled={downloading}
                onClick={() => triggerDownload(rc.type, 'excel', rc.params)}
                className="btn-secondary text-sm flex-1 justify-center"
              >
                <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Export Excel
              </button>
            </div>
          </div>
        ))}
      </div>
    </DashboardLayout>
  );
}
