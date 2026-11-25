import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { studyPlanAPI, studentsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Brain, Calendar, Clock, CheckCircle2, Sparkles } from 'lucide-react';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function AIStudyPlanner() {
  const { user } = useAuth();
  const [weakSubjectsText, setWeakSubjectsText] = useState('Data Structures, Operating Systems, Engineering Mathematics');
  const [dailyHours, setDailyHours] = useState(4);
  const [studyDays, setStudyDays] = useState(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']);
  const [examDate, setExamDate] = useState('');
  const [targetCgpa, setTargetCgpa] = useState(8.5);
  const [studentId, setStudentId] = useState('');
  const [students, setStudents] = useState([]);
  const [activePlan, setActivePlan] = useState(null);
  const [savedPlans, setSavedPlans] = useState([]);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    studyPlanAPI.list().then((res) => {
      const plans = res.data?.plans || [];
      setSavedPlans(plans);
      if (plans.length > 0) setActivePlan(plans[0].plan);
    }).catch(() => {});

    if (user?.role !== 'student') {
      studentsAPI.list({ page: 1, page_size: 30 }).then((r) => {
        const list = r.data.items || [];
        setStudents(list);
        if (list.length > 0) setStudentId(list[0].id);
      }).catch(() => {});
    }
  }, []);

  const toggleDay = (day) => {
    setStudyDays((prev) => prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]);
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const weak_subjects = weakSubjectsText.split(',').map((s) => s.trim()).filter(Boolean);
      const res = await studyPlanAPI.generate({
        student_id: user?.role === 'student' ? undefined : Number(studentId),
        weak_subjects,
        daily_hours: Number(dailyHours),
        study_days: studyDays,
        exam_date: examDate || null,
        target_cgpa: Number(targetCgpa),
      });
      setActivePlan(res.data.plan);
      toast.success('Personalized study plan generated!');
      const listRes = await studyPlanAPI.list();
      setSavedPlans(listRes.data?.plans || []);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate study plan');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <DashboardLayout title="AI Personalized Study Planner">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-blue-600" /> Configure Study Plan
          </h3>
          <form onSubmit={handleGenerate} className="space-y-4">
            {user?.role !== 'student' && (
              <div>
                <label className="label">Student</label>
                <select className="input" value={studentId} onChange={(e) => setStudentId(e.target.value)}>
                  {students.map((s) => <option key={s.id} value={s.id}>{s.student_id} — {s.full_name}</option>)}
                </select>
              </div>
            )}
            <div>
              <label className="label">Weak / Focus Subjects (comma-separated)</label>
              <textarea
                rows={2}
                required
                className="input"
                value={weakSubjectsText}
                onChange={(e) => setWeakSubjectsText(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Daily Study Hours</label>
                <input type="number" step="0.5" min={1} max={14} className="input" value={dailyHours} onChange={(e) => setDailyHours(e.target.value)} />
              </div>
              <div>
                <label className="label">Target CGPA</label>
                <input type="number" step="0.1" min={5} max={10} className="input" value={targetCgpa} onChange={(e) => setTargetCgpa(e.target.value)} />
              </div>
            </div>
            <div>
              <label className="label">Exam Date (optional)</label>
              <input type="date" className="input" value={examDate} onChange={(e) => setExamDate(e.target.value)} />
            </div>
            <div>
              <label className="label">Weekly Study Days</label>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {DAYS.map((d) => (
                  <button
                    type="button"
                    key={d}
                    onClick={() => toggleDay(d)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${
                      studyDays.includes(d) ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-600 border-slate-200'
                    }`}
                  >
                    {d.slice(0, 3)}
                  </button>
                ))}
              </div>
            </div>
            <button type="submit" disabled={generating} className="btn-primary w-full justify-center">
              <Sparkles className="w-4 h-4" /> {generating ? 'Generating...' : 'Generate Study Plan'}
            </button>
          </form>
        </div>

        {/* Output */}
        <div className="lg:col-span-2 space-y-6">
          {!activePlan ? (
            <div className="card text-center py-16 text-slate-500">
              Fill out the study parameters on the left and click "Generate Study Plan" to build your personalized timetable.
            </div>
          ) : (
            <>
              <div className="card">
                <h3 className="font-bold text-lg text-slate-900 mb-3">{activePlan.plan_title}</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4 text-sm">
                  <div className="p-3 bg-blue-50 rounded-lg"><p className="text-xs text-slate-500">Daily Target</p><p className="font-bold text-blue-700">{activePlan.summary?.daily_study_hours} hrs</p></div>
                  <div className="p-3 bg-slate-50 rounded-lg"><p className="text-xs text-slate-500">Study Days</p><p className="font-bold">{activePlan.summary?.study_days_per_week} / wk</p></div>
                  <div className="p-3 bg-slate-50 rounded-lg"><p className="text-xs text-slate-500">Weeks</p><p className="font-bold">{activePlan.summary?.weeks_available}</p></div>
                  <div className="p-3 bg-emerald-50 rounded-lg"><p className="text-xs text-slate-500">Target CGPA</p><p className="font-bold text-emerald-700">{activePlan.summary?.target_cgpa || 'N/A'}</p></div>
                </div>

                <h4 className="font-semibold text-sm text-slate-800 mb-2 flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-blue-600" /> Weekly Timetable
                </h4>
                <div className="grid sm:grid-cols-2 gap-3">
                  {Object.entries(activePlan.weekly_schedule || {}).map(([day, info]) => (
                    <div key={day} className="p-3 rounded-xl border border-slate-200 bg-slate-50">
                      <div className="flex justify-between items-center mb-1.5">
                        <span className="font-semibold text-sm text-slate-800">{day}</span>
                        <span className="badge-blue flex items-center gap-1"><Clock className="w-3 h-3" /> {info.hours}h</span>
                      </div>
                      <ul className="text-xs text-slate-600 space-y-1">
                        {(info.tasks || []).map((t, i) => <li key={i}>• {t}</li>)}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Milestones */}
              {activePlan.milestones?.length > 0 && (
                <div className="card">
                  <h4 className="font-semibold text-slate-800 mb-3">Weekly Progress Milestones</h4>
                  <div className="space-y-2">
                    {activePlan.milestones.map((m) => (
                      <div key={m.week} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 text-sm">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                          <span className="font-medium">Week {m.week}: {m.goal}</span>
                        </div>
                        <span className="text-xs text-slate-500">{m.expected_improvement}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
