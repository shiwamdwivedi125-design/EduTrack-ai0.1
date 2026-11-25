import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { GraduationCap, Lock, Mail, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('admin@edutrack.ai');
  const [password, setPassword] = useState('Admin@123');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.full_name}!`);
      if (user.role === 'admin') navigate('/admin/dashboard');
      else if (user.role === 'teacher') navigate('/teacher/dashboard');
      else navigate('/student/dashboard');
    } catch (err) {
      const status = err.response?.status;
      const message = status === 503
        ? 'The service is temporarily unavailable. Please try again shortly.'
        : status === 401
          ? 'Invalid email or password. Try one of the demo accounts below.'
          : err.response?.data?.detail || 'Could not connect to EduTrack AI. Please try again.';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
        <div className="flex flex-col items-center mb-8">
          <Link to="/" className="bg-blue-600 p-3 rounded-xl mb-3">
            <GraduationCap className="w-8 h-8 text-white" />
          </Link>
          <h1 className="text-2xl font-bold text-slate-900">Sign in to EduTrack AI</h1>
          <p className="text-sm text-slate-500 mt-1">Academic Performance & Early Warning System</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input pl-9"
                placeholder="you@edutrack.ai"
              />
            </div>
          </div>

          <div>
            <label className="label">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input pl-9"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary justify-center py-2.5 text-sm font-semibold"
          >
            {loading ? 'Signing in...' : 'Sign In'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Demo Credentials */}
        <div className="mt-6 pt-6 border-t border-slate-100">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
            Demo Accounts (Click to Autofill)
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
            <button
              type="button"
              onClick={() => fillDemo('admin@edutrack.ai', 'Admin@123')}
              className="p-2.5 rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50 text-left transition-colors"
            >
              <p className="font-semibold text-slate-800">Admin</p>
              <p className="text-slate-500 truncate">admin@edutrack.ai</p>
            </button>
            <button
              type="button"
              onClick={() => fillDemo('ramesh.kumar@edutrack.ai', 'Teacher@123')}
              className="p-2.5 rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50 text-left transition-colors"
            >
              <p className="font-semibold text-slate-800">Teacher</p>
              <p className="text-slate-500 truncate">ramesh.kumar@edutrack.ai</p>
            </button>
            <button
              type="button"
              onClick={() => fillDemo('jay.verma.s1@edu.example.com', 'Student@123')}
              className="p-2.5 rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50 text-left transition-colors"
            >
              <p className="font-semibold text-slate-800">Student</p>
              <p className="text-slate-500 truncate">jay.verma.s1@edu.example.com</p>
            </button>
          </div>
          <p className="text-[11px] text-slate-400 mt-3 text-center">
            Demo passwords: Admin@123, Teacher@123, Student@123
          </p>
        </div>
      </div>
    </div>
  );
}
