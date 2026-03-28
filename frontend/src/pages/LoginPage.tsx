import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, ScanLine } from 'lucide-react';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import { useAuthStore } from '../store/useAuthStore';

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // ── Mock login (replace with real API call) ─────────────────────────
    try {
      await new Promise((r) => setTimeout(r, 600));
      if (email === 'demo@splititfair.com' && password === 'password') {
        login(
          { id: '1', email, full_name: 'Demo User', preferred_currency: 'USD' },
          'mock-jwt-token-v2'
        );
        navigate('/dashboard');
      } else {
        setError('Invalid email or password. Try demo@splititfair.com / password');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* BG glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <Link to="/" className="flex items-center justify-center gap-2 text-xl font-bold text-white mb-8">
          <ScanLine className="text-indigo-400" />
          Split It <span className="text-indigo-400">Fair</span>
        </Link>

        <div className="bg-slate-900/80 backdrop-blur-md border border-white/10 rounded-3xl p-8 shadow-2xl">
          <h1 className="text-2xl font-bold text-white mb-1">Welcome back</h1>
          <p className="text-sm text-slate-400 mb-8">Sign in to continue managing your expenses.</p>

          {error && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm rounded-xl px-4 py-3 mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <Input
              id="login-email"
              label="Email"
              type="email"
              placeholder="you@example.com"
              icon={<Mail size={16} />}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              id="login-password"
              label="Password"
              type="password"
              placeholder="••••••••"
              icon={<Lock size={16} />}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button type="submit" fullWidth loading={loading}>
              Sign In
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
