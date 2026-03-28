import { ScanLine, ArrowRight, ShieldCheck, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';

export default function LandingPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  // Mock login for demonstration
  const handleGetStarted = () => {
    login({ id: '1', email: 'demo@splititfair.com', full_name: 'Demo User' }, 'mock-jwt-token');
    navigate('/dashboard');
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 flex flex-col justify-center items-center">
      
      {/* Dynamic Background Gradients */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-sky-500/10 rounded-full blur-[100px] pointer-events-none" />
      
      {/* Header / Nav Mock */}
      <nav className="absolute top-0 w-full p-6 flex justify-between items-center z-10 max-w-7xl">
        <div className="flex items-center gap-2 text-xl font-bold tracking-tight text-white">
          <ScanLine className="text-indigo-400" />
          <span>Split It <span className="text-indigo-400">Fair</span></span>
        </div>
        <button 
          onClick={handleGetStarted}
          className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
        >
          Sign In
        </button>
      </nav>

      <main className="relative z-10 text-center px-4 max-w-4xl mx-auto flex flex-col items-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm font-medium mb-8">
          <Zap size={14} /> v2.0 Debt Engine is Live
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400 mb-6 drop-shadow-sm">
          Settle debts without <br className="hidden md:block"/> draining friendships.
        </h1>
        
        <p className="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl font-light">
          A powerful expense engine designed to calculate fair splits instantly, minimize awkward transactions, and manage group debts beautifully.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4">
          <button 
            onClick={handleGetStarted}
            className="group relative inline-flex items-center justify-center gap-2 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-2xl transition-all active:scale-95 overflow-hidden shadow-[0_0_40px_-5px_rgba(79,70,229,0.4)]"
          >
            <span className="relative z-10">Get Started Free</span>
            <ArrowRight size={18} className="relative z-10 group-hover:translate-x-1 transition-transform" />
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
          
          <button className="px-8 py-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 text-slate-300 font-medium rounded-2xl transition-all hover:text-white active:scale-95 backdrop-blur-md">
            View Live Demo
          </button>
        </div>

        {/* Feature Highlights */}
        <div className="mt-24 grid grid-cols-1 sm:grid-cols-3 gap-6 w-full text-left">
          {[
            { title: "Smart Minimization", desc: "Our engine reduces total group transactions so you only pay once." },
            { title: "Any Split Logic", desc: "Equally, by percentage, exact amounts, or shares. Handle any receipt." },
            { title: "Ironclad Security", desc: "End-to-end encrypted sessions and secure Postgres-backed data." }
          ].map((feature, i) => (
             <div key={i} className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:bg-white/[0.04] transition-colors">
                <ShieldCheck className="text-indigo-400 mb-4 h-6 w-6" />
                <h3 className="text-white font-medium mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-400">{feature.desc}</p>
             </div>
          ))}
        </div>
      </main>
    </div>
  );
}
