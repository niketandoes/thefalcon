import { LogOut, LayoutDashboard, ScanLine } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="border-b border-white/5 bg-slate-950/70 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between h-16 items-center">
        <Link to="/dashboard" className="flex items-center gap-2 font-bold text-white tracking-tight hover:opacity-90 transition-opacity">
          <ScanLine className="text-indigo-400" size={22} />
          <span>Split It <span className="text-indigo-400">Fair</span></span>
        </Link>
        <div className="flex items-center gap-4">
          <Link
            to="/dashboard"
            className="hidden sm:flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <LayoutDashboard size={16} /> Dashboard
          </Link>
          <span className="text-sm font-medium text-slate-500 hidden md:block">
            {user?.full_name || user?.email}
          </span>
          <button
            onClick={handleLogout}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </nav>
  );
}
