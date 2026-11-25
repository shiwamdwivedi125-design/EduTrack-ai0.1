import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoadingSpinner } from './components/Common';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import AdminDashboard from './pages/AdminDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import StudentDashboard from './pages/StudentDashboard';
import StudentManagement from './pages/StudentManagement';
import AttendanceManagement from './pages/AttendanceManagement';
import MarksManagement from './pages/MarksManagement';
import AcademicAnalytics from './pages/AcademicAnalytics';
import AIStudyPlanner from './pages/AIStudyPlanner';
import PlacementReadiness from './pages/PlacementReadiness';
import GoalsAndAchievements from './pages/GoalsAndAchievements';
import AcademicReports from './pages/AcademicReports';
import UserProfile from './pages/UserProfile';
import SettingsPage from './pages/SettingsPage';

function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center"><LoadingSpinner /></div>;
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    if (user.role === 'admin') return <Navigate to="/admin/dashboard" replace />;
    if (user.role === 'teacher') return <Navigate to="/teacher/dashboard" replace />;
    return <Navigate to="/student/dashboard" replace />;
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />

          <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={['admin']}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/teacher/dashboard" element={<ProtectedRoute allowedRoles={['teacher', 'admin']}><TeacherDashboard /></ProtectedRoute>} />
          <Route path="/student/dashboard" element={<ProtectedRoute allowedRoles={['student', 'admin']}><StudentDashboard /></ProtectedRoute>} />

          <Route path="/students" element={<ProtectedRoute allowedRoles={['admin', 'teacher']}><StudentManagement /></ProtectedRoute>} />
          <Route path="/attendance" element={<ProtectedRoute><AttendanceManagement /></ProtectedRoute>} />
          <Route path="/marks" element={<ProtectedRoute><MarksManagement /></ProtectedRoute>} />
          <Route path="/analytics" element={<ProtectedRoute><AcademicAnalytics /></ProtectedRoute>} />
          <Route path="/study-planner" element={<ProtectedRoute><AIStudyPlanner /></ProtectedRoute>} />
          <Route path="/placement" element={<ProtectedRoute><PlacementReadiness /></ProtectedRoute>} />
          <Route path="/goals" element={<ProtectedRoute><GoalsAndAchievements /></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute><AcademicReports /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><UserProfile /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
