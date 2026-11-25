import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { notificationsAPI } from '../services/api';
import {
  LayoutDashboard, Users, CalendarCheck, FileSpreadsheet, BarChart3,
  Brain, Briefcase, Trophy, FileText, User, Settings, LogOut,
  Bell, Menu, X, GraduationCap, AlertTriangle
} from 'lucide-react';

export default function DashboardLayout({ children, title }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    notificationsAPI.list()
      .then((res) => setNotifications(res.data || []))
      .catch(() => {});
  }, []);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const handleMarkRead = async (id) => {
    try {
      await notificationsAPI.markRead(id);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch {}
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const role = user?.role || 'student';

  const navItems = [
    ...(role === 'admin' ? [{ to: '/admin/dashboard', label: 'Admin Dashboard', icon: LayoutDashboard }] : []),
    ...(role === 'teacher' ? [{ to: '/teacher/dashboard', label: 'Teacher Dashboard', icon: LayoutDashboard }] : []),
    ...(role === 'student' ? [{ to: '/student/dashboard', label: 'Student Dashboard', icon: LayoutDashboard }] : []),
    ...(role !== 'student' ? [{ to: '/students', label: 'Student Management', icon: Users }] : []),
    { to: '/attendance', label: 'Attendance', icon: CalendarCheck },
    { to: '/marks', label: 'Marks & Grades', icon: FileSpreadsheet },
    { to: '/analytics', label: 'Academic Analytics & ML', icon: BarChart3 },
    { to: '/study-planner', label: 'AI Study Planner', icon: Brain },
    { to: '/placement', label: 'Placement Readiness', icon: Briefcase },
    { to: '/goals', label: 'Goals & Badges', icon: Trophy },
    { to: '/reports', label: 'Academic Reports', icon: FileText },
    { to: '/profile', label: 'User Profile', icon: User },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-slate-900 text-white w-64">
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-800">
        <div className="bg-blue-600 p-2 rounded-lg">
          <GraduationCap className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-lg leading-tight">EduTrack AI</h1>
          <p className="text-xs text-slate-400 capitalize">{role} Portal</p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 mb-3 px-2">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center font-bold text-sm">
            {user?.full_name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium truncate">{user?.full_name}</p>
            <p className="text-xs text-slate-400 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:block shrink-0">
        <div className="fixed inset-y-0 left-0 z-30">
          <SidebarContent />
        </div>
        <div className="w-64" />
      </aside>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div className="fixed inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="relative z-10">
            <SidebarContent />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-slate-200 sticky top-0 z-20 px-4 lg:px-8 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <h2 className="text-lg font-semibold text-slate-900">{title || 'Dashboard'}</h2>
          </div>

          <div className="flex items-center gap-4">
            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setNotifOpen(!notifOpen)}
                className="relative p-2 rounded-lg text-slate-600 hover:bg-slate-100"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                )}
              </button>

              {notifOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-slate-200 p-3 z-50">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
                    <span className="font-semibold text-sm text-slate-800">Notifications</span>
                    <span className="text-xs text-slate-500">{unreadCount} unread</span>
                  </div>
                  {notifications.length === 0 ? (
                    <p className="text-xs text-slate-500 py-4 text-center">No notifications yet.</p>
                  ) : (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {notifications.slice(0, 8).map((n) => (
                        <div
                          key={n.id}
                          onClick={() => handleMarkRead(n.id)}
                          className={`p-2 rounded-lg text-xs cursor-pointer ${
                            n.is_read ? 'bg-slate-50 text-slate-600' : 'bg-blue-50 text-slate-900 font-medium'
                          }`}
                        >
                          <p className="font-semibold">{n.title}</p>
                          <p className="text-slate-500 mt-0.5">{n.message}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            <NavLink to="/profile" className="flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-blue-600">
              <span className="hidden sm:inline">{user?.full_name}</span>
              <span className="badge-blue capitalize">{role}</span>
            </NavLink>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
