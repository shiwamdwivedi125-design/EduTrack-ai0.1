import React from 'react';
import { Link } from 'react-router-dom';
import {
  GraduationCap, ShieldCheck, BarChart3, Brain, BellRing,
  FileSpreadsheet, ArrowRight, CheckCircle2, Users, Award
} from 'lucide-react';

export default function LandingPage() {
  const features = [
    { icon: BarChart3, title: 'Academic Analytics', desc: 'Pandas & NumPy powered performance distributions, rankings, and correlations.' },
    { icon: BellRing, title: 'Early Warning System', desc: 'Explainable risk scoring (Low, Moderate, High) to support timely faculty intervention.' },
    { icon: Brain, title: 'AI Study Planner', desc: 'Personalized weekly study timetables, revision schedules, and practice milestones.' },
    { icon: ShieldCheck, title: 'ML Performance Prediction', desc: 'Scikit-learn Logistic Regression & Random Forest models with clear estimate disclaimers.' },
    { icon: FileSpreadsheet, title: 'CSV/Excel Bulk Import', desc: 'Preview, column validation, duplicate detection, and row-level error reporting.' },
    { icon: Award, title: 'Placement Readiness & Goals', desc: 'Track technical skills, projects, aptitude, weekly goals, and achievement badges.' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Navbar */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="bg-blue-600 p-2 rounded-lg">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl text-slate-900">EduTrack AI</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login" className="text-sm font-medium text-slate-600 hover:text-blue-600">
              Sign In
            </Link>
            <Link to="/login" className="btn-primary text-sm">
              Launch Portal <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-900 via-blue-800 to-slate-900 text-white py-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <span className="inline-block px-4 py-1.5 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs font-semibold uppercase tracking-wider mb-6">
            Student Academic Performance & Early Warning System
          </span>
          <h1 className="text-4xl sm:text-5xl font-extrabold leading-tight mb-6">
            Intelligent Academic Tracking & Support for Modern Colleges
          </h1>
          <p className="text-lg text-blue-100 max-w-2xl mx-auto mb-10">
            Empowering Administrators, Teachers, and Students with real-time CGPA calculation,
            attendance monitoring, explainable risk alerts, ML predictions, and personalized AI study plans.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/login" className="bg-white text-blue-900 hover:bg-blue-50 font-semibold px-7 py-3.5 rounded-xl flex items-center gap-2 transition-colors shadow-lg">
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
            <a href="#features" className="border border-blue-400/50 hover:bg-blue-800/50 text-white font-semibold px-7 py-3.5 rounded-xl transition-colors">
              Explore Features
            </a>
          </div>
        </div>
      </section>

      {/* Role Cards */}
      <section className="max-w-6xl mx-auto px-6 -mt-10 grid md:grid-cols-3 gap-6">
        {[
          { role: 'Admin Panel', items: ['Manage 200+ Students & Faculty', 'Configure Grading & Credit Rules', 'College-wide Analytics & PDF Reports'] },
          { role: 'Teacher Panel', items: ['Mark Attendance & Upload Marks', 'Subject-wise Performance Insights', 'Track Student Interventions'] },
          { role: 'Student Panel', items: ['View CGPA, Marks & Attendance', 'AI Personalized Study Planner', 'Goals, Badges & Placement Readiness'] },
        ].map((card) => (
          <div key={card.role} className="bg-white rounded-2xl shadow-md border border-slate-100 p-6">
            <div className="flex items-center gap-2 text-blue-600 font-bold text-lg mb-4">
              <Users className="w-5 h-5" />
              <h3>{card.role}</h3>
            </div>
            <ul className="space-y-2.5 text-sm text-slate-600">
              {card.items.map((item) => (
                <li key={item} className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      {/* Features Grid */}
      <section id="features" className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900">Complete Academic Intelligence Suite</h2>
          <p className="text-slate-500 mt-2">Built with FastAPI, React, Tailwind CSS, Recharts, Pandas, and Scikit-learn.</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => {
            const Icon = f.icon;
            return (
              <div key={f.title} className="card hover:shadow-md transition-shadow">
                <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="font-semibold text-lg text-slate-900 mb-2">{f.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{f.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      <footer className="bg-slate-900 text-slate-400 py-8 px-6 text-center text-sm">
        <p>© 2026 EduTrack AI — Student Academic Performance & Early Warning System. All demo data is synthetic.</p>
      </footer>
    </div>
  );
}
