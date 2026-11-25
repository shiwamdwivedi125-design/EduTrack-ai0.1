import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { KPICard, LoadingSpinner } from '../components/Common';
import { analyticsAPI, mlAPI } from '../services/api';
import toast from 'react-hot-toast';
import { BarChart3, Cpu, TrendingUp, Award, AlertCircle } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function AcademicAnalytics() {
  const [stats, setStats] = useState(null);
  const [charts, setCharts] = useState({});
  const [mlEval, setMlEval] = useState(null);
  const [fi, setFi] = useState(null);
  const [predInput, setPredInput] = useState({ attendance: 78, previous_cgpa: 7.2, avg_internal_percentage: 70 });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [stRes, chRes, evRes, fiRes] = await Promise.all([
          analyticsAPI.stats(),
          analyticsAPI.charts().catch(() => ({ data: { charts: {} } })),
          mlAPI.evaluation(),
          mlAPI.featureImportance(),
        ]);
        setStats(stRes.data);
        setCharts(chRes.data?.charts || {});
        setMlEval(evRes.data);
        setFi(fiRes.data);
      } catch {
        toast.error('Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handlePredict = async (e) => {
    e.preventDefault();
    try {
      const res = await mlAPI.predict({
        attendance: Number(predInput.attendance),
        previous_cgpa: Number(predInput.previous_cgpa),
        avg_internal_percentage: Number(predInput.avg_internal_percentage),
      });
      setPrediction(res.data);
    } catch {
      toast.error('Prediction failed');
    }
  };

  if (loading) {
    return <DashboardLayout title="Academic Analytics & ML"><LoadingSpinner /></DashboardLayout>;
  }

  const s = stats?.stats || {};
  const fiData = (fi?.features || []).map((f, idx) => ({
    feature: f,
    importance: Number(((fi?.importance?.[idx] || 0) * 100).toFixed(1)),
  }));

  return (
    <DashboardLayout title="Academic Analytics & Machine Learning">
      {/* Pandas / NumPy Descriptive Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <KPICard title="Mean Percentage" value={`${s.mean_percentage ?? 0}%`} subtitle={`Median: ${s.median_percentage ?? 0}%`} icon={BarChart3} color="blue" />
        <KPICard title="Std Deviation" value={s.std_deviation ?? 0} subtitle={`Mode: ${s.mode_percentage ?? 0}%`} icon={TrendingUp} color="indigo" />
        <KPICard title="Pass Rate" value={`${s.pass_rate ?? 0}%`} subtitle={`${s.records_analyzed ?? 0} records`} icon={Award} color="green" />
        <KPICard title="Att–CGPA Correlation" value={stats?.attendance_cgpa_correlation ?? 0} subtitle={stats?.correlation_interpretation} icon={Cpu} color="purple" />
      </div>

      {/* ML Predictor & Model Evaluation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-2 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-600" /> ML Performance Predictor
          </h3>
          <p className="text-xs text-slate-500 mb-4">Estimate student outcome using Attendance, Previous CGPA & Internal Marks.</p>
          <form onSubmit={handlePredict} className="space-y-3">
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="label">Attendance (%)</label>
                <input type="number" min={0} max={100} className="input" value={predInput.attendance} onChange={(e) => setPredInput({ ...predInput, attendance: e.target.value })} />
              </div>
              <div>
                <label className="label">Previous CGPA</label>
                <input type="number" step="0.1" min={0} max={10} className="input" value={predInput.previous_cgpa} onChange={(e) => setPredInput({ ...predInput, previous_cgpa: e.target.value })} />
              </div>
              <div>
                <label className="label">Internal (%)</label>
                <input type="number" min={0} max={100} className="input" value={predInput.avg_internal_percentage} onChange={(e) => setPredInput({ ...predInput, avg_internal_percentage: e.target.value })} />
              </div>
            </div>
            <button type="submit" className="btn-primary">Run Prediction Estimate</button>
          </form>

          {prediction && (
            <div className="mt-4 p-4 rounded-xl bg-blue-50 border border-blue-200">
              <div className="flex items-center justify-between">
                <span className="font-bold text-lg text-blue-900">Estimate: {prediction.prediction}</span>
                <span className="badge-blue">Confidence: {(prediction.probability * 100).toFixed(0)}%</span>
              </div>
              <p className="text-xs text-slate-600 mt-1">Model: {prediction.model_type}</p>
              <p className="text-[11px] text-amber-800 mt-2 flex items-start gap-1">
                <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" /> {prediction.disclaimer}
              </p>
            </div>
          )}
        </div>

        {/* ML Evaluation & Feature Importance */}
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">ML Model Evaluation & Feature Importance</h3>
          {mlEval?.metrics ? (
            <div className="grid grid-cols-4 gap-2 mb-4 text-center">
              <div className="p-2 bg-slate-50 rounded-lg"><p className="text-xs text-slate-500">Accuracy</p><p className="font-bold">{(mlEval.metrics.accuracy * 100).toFixed(1)}%</p></div>
              <div className="p-2 bg-slate-50 rounded-lg"><p className="text-xs text-slate-500">Precision</p><p className="font-bold">{(mlEval.metrics.precision * 100).toFixed(1)}%</p></div>
              <div className="p-2 bg-slate-50 rounded-lg"><p className="text-xs text-slate-500">Recall</p><p className="font-bold">{(mlEval.metrics.recall * 100).toFixed(1)}%</p></div>
              <div className="p-2 bg-slate-50 rounded-lg"><p className="text-xs text-slate-500">F1 Score</p><p className="font-bold">{(mlEval.metrics.f1_score * 100).toFixed(1)}%</p></div>
            </div>
          ) : (
            <p className="text-xs text-amber-700 bg-amber-50 p-2.5 rounded-lg mb-4">
              {mlEval?.message || 'Demonstration mode — using rule-based fallback until ML model is trained.'}
            </p>
          )}
          <div className="h-44">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fiData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis type="category" dataKey="feature" width={130} />
                <Tooltip />
                <Bar dataKey="importance" fill="#2563eb" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Matplotlib / Seaborn Charts */}
      {(charts.marks_distribution || charts.dept_cgpa_boxplot) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {charts.marks_distribution && (
            <div className="card">
              <h3 className="font-semibold text-slate-800 mb-3">Seaborn Marks Distribution (KDE)</h3>
              <img src={charts.marks_distribution} alt="Marks Distribution" className="w-full rounded-lg" />
            </div>
          )}
          {charts.dept_cgpa_boxplot && (
            <div className="card">
              <h3 className="font-semibold text-slate-800 mb-3">Seaborn Department CGPA Boxplot</h3>
              <img src={charts.dept_cgpa_boxplot} alt="Dept Boxplot" className="w-full rounded-lg" />
            </div>
          )}
        </div>
      )}

      {/* Top Student Rankings */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4">Top Ranked Students (By CGPA)</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b">
              <tr>
                <th className="table-header">Rank</th>
                <th className="table-header">Student ID</th>
                <th className="table-header">Name</th>
                <th className="table-header">Department</th>
                <th className="table-header">CGPA</th>
                <th className="table-header">Attendance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(stats?.top_rankings || []).map((r) => (
                <tr key={r.student_id}>
                  <td className="table-cell font-bold text-blue-600">#{r.rank}</td>
                  <td className="table-cell">{r.student_code}</td>
                  <td className="table-cell font-medium">{r.name}</td>
                  <td className="table-cell"><span className="badge-blue">{r.department}</span></td>
                  <td className="table-cell font-bold">{r.cgpa}</td>
                  <td className="table-cell">{r.attendance_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardLayout>
  );
}
