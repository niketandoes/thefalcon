import { ScanLine, ArrowRight, ShieldCheck, Zap, Users, Sparkles } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import Button from '../components/common/Button';

export default function LandingPage() {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 flex flex-col">
      {/* ── Dynamic Background ──────────────────────────────────────────── */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-indigo-600/15 rounded-full blur-[140px] pointer-events-none animate-pulse" />
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-sky-500/8 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-0 left-0 w-[350px] h-[350px] bg-violet-500/8 rounded-full blur-[100px] pointer-events-none" />

      {/* ── Navbar ──────────────────────────────────────────────────────── */}
      <nav className="relative z-10 max-w-7xl w-full mx-auto p-6 flex justify-between items-center">
        <div className="flex items-center gap-2 text-xl font-bold tracking-tight text-white">
          <ScanLine className="text-indigo-400" />
          <span>Split It <span className="text-indigo-400">Fair</span></span>
        </div>
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Button variant="primary" onClick={() => navigate('/dashboard')}>
              Go to Dashboard
            </Button>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-medium text-slate-300 hover:text-white transition-colors px-4 py-2"
              >
                Log in
              </Link>
              <Button variant="primary" onClick={() => navigate('/register')} icon={<ArrowRight size={16} />}>
                Register
              </Button>
            </>
          )}
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <main className="relative z-10 flex-1 flex flex-col justify-center items-center text-center px-4 pb-20">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm font-medium mb-8 backdrop-blur-sm">
          <Sparkles size={14} /> Smart Debt Engine Powered by Math
        </div>

        <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight mb-6 leading-[1.08]">
          <span className="text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-slate-500">
            Settle debts without
          </span>
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-sky-400">
            draining friendships.
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-400 mb-12 max-w-2xl font-light leading-relaxed">
          A precision-crafted expense engine that splits any bill fairly — by equal share,
          percentage, portion, or exact item — and minimizes who-pays-who across your entire&nbsp;group.
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            variant="primary"
            className="text-base px-8 py-4 shadow-[0_0_50px_-5px_rgba(79,70,229,0.35)]"
            onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
            icon={<Zap size={18} />}
          >
            Get Started — It's Free
          </Button>
          <Button
            variant="secondary"
            className="text-base px-8 py-4 backdrop-blur-md"
            onClick={() => navigate(isAuthenticated ? '/dashboard' : '/login')}
          >
            {isAuthenticated ? 'Open Dashboard' : 'I have an account'}
          </Button>
        </div>

        {/* ── Feature Cards ─────────────────────────────────────────────── */}
        <div className="mt-28 grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-5xl text-left">
          {[
            {
              icon: <Zap className="text-indigo-400" size={22} />,
              title: 'Penny-Perfect Splitting',
              desc: 'Hamilton largest-remainder algorithm ensures the sum is exact — down to the last cent.',
            },
            {
              icon: <Users className="text-sky-400" size={22} />,
              title: 'Minimized Transactions',
              desc: 'A greedy graph resolver reduces all inter-group debts to the fewest possible payments.',
            },
            {
              icon: <ShieldCheck className="text-emerald-400" size={22} />,
              title: 'Group Exit Guard',
              desc: 'Nobody can leave a group until their balance is fully settled — enforced by the system.',
            },
          ].map((f, i) => (
            <div
              key={i}
              className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:bg-white/[0.04] transition-all hover:-translate-y-1 duration-300"
            >
              <div className="mb-4">{f.icon}</div>
              <h3 className="text-white font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer className="relative z-10 text-center py-8 text-sm text-slate-600 border-t border-white/[0.03]">
        © {new Date().getFullYear()} Split It Fair • Built with precision
      </footer>
    </div>
  );
}
