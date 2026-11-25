import React, { useState } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import { useAuth } from '../context/AuthContext';
import { usersAPI, authAPI } from '../services/api';
import toast from 'react-hot-toast';
import { User, Lock } from 'lucide-react';

export default function UserProfile() {
  const { user } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [oldPass, setOldPass] = useState('');
  const [newPass, setNewPass] = useState('');

  const handleUpdateName = async (e) => {
    e.preventDefault();
    try {
      await usersAPI.update(user.id, { full_name: fullName });
      toast.success('Profile updated! Refresh to see changes.');
    } catch {
      toast.error('Failed to update profile');
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    try {
      await authAPI.changePassword(oldPass, newPass);
      toast.success('Password changed successfully');
      setOldPass('');
      setNewPass('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to change password');
    }
  };

  return (
    <DashboardLayout title="User Profile">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-blue-600" /> Account Details
          </h3>
          <form onSubmit={handleUpdateName} className="space-y-4">
            <div>
              <label className="label">Full Name</label>
              <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div>
              <label className="label">Email</label>
              <input disabled className="input bg-slate-100" value={user?.email || ''} />
            </div>
            <div>
              <label className="label">Role</label>
              <input disabled className="input bg-slate-100 capitalize" value={user?.role || ''} />
            </div>
            <button type="submit" className="btn-primary">Save Profile</button>
          </form>
        </div>

        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Lock className="w-5 h-5 text-blue-600" /> Change Password
          </h3>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="label">Current Password</label>
              <input type="password" required className="input" value={oldPass} onChange={(e) => setOldPass(e.target.value)} />
            </div>
            <div>
              <label className="label">New Password</label>
              <input type="password" required minLength={6} className="input" value={newPass} onChange={(e) => setNewPass(e.target.value)} />
            </div>
            <button type="submit" className="btn-primary">Update Password</button>
          </form>
        </div>
      </div>
    </DashboardLayout>
  );
}
