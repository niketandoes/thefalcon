import { useAuthStore } from '../store/useAuthStore';
import { LogOut, Users, Plus, LayoutDashboard } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-slate-950 pb-10">
      {/* Top Navbar */}
      <nav className="border-b border-white/5 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between h-16 items-center">
          <div className="flex items-center gap-2 font-bold text-white tracking-tight">
            <LayoutDashboard className="text-indigo-400" />
            <span>Dashboard</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-slate-400 hidden sm:block">
              {user?.full_name || user?.email}
            </span>
            <button 
              onClick={handleLogout}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 transition-colors"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-10">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Your Groups</h1>
            <p className="text-slate-400 mt-1">Manage shared expenses across different trips and friends.</p>
          </div>
          <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 transition-colors text-white px-4 py-2 font-medium rounded-xl shadow-lg shadow-indigo-500/20 active:scale-95">
            <Plus size={18} /> New Group
          </button>
        </div>

        {/* Empty State / Grid Mockup */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Mock Group Card */}
          <div 
            onClick={() => navigate('/groups/1')}
            className="group cursor-pointer bg-slate-900 rounded-2xl border border-white/5 p-6 hover:border-indigo-500/30 transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-indigo-500/10"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-indigo-500/10 rounded-xl">
                <Users className="text-indigo-400" size={24} />
              </div>
              <span className="text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md">You are owed $45.00</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-1 group-hover:text-indigo-300 transition-colors">Miami Trip '24</h3>
            <p className="text-sm text-slate-400">4 members • Last active 2h ago</p>
          </div>

           {/* Mock Group Card 2 */}
           <div 
            onClick={() => navigate('/groups/2')}
            className="group cursor-pointer bg-slate-900 rounded-2xl border border-white/5 p-6 hover:border-rose-500/30 transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-rose-500/10"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-rose-500/10 rounded-xl">
                <Users className="text-rose-400" size={24} />
              </div>
              <span className="text-xs font-medium text-rose-400 bg-rose-400/10 px-2 py-1 rounded-md">You owe $12.50</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-1 group-hover:text-rose-300 transition-colors">Apartment Utilities</h3>
            <p className="text-sm text-slate-400">3 members • Last active 1d ago</p>
          </div>

        </div>
      </main>
    </div>
  );
}
