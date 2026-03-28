import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, User, Coins, ScanLine } from 'lucide-react';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import Button from '../components/common/Button';
import { useAuthStore } from '../store/useAuthStore';
import { apiClient } from '../api/client';

const CURRENCIES = [
  { value: 'USD', label: '🇺🇸 USD — US Dollar' },
  { value: 'EUR', label: '🇪🇺 EUR — Euro' },
  { value: 'GBP', label: '🇬🇧 GBP — British Pound' },
  { value: 'INR', label: '🇮🇳 INR — Indian Rupee' },
  { value: 'JPY', label: '🇯🇵 JPY — Japanese Yen' },
  { value: 'CAD', label: '🇨🇦 CAD — Canadian Dollar' },
  { value: 'AUD', label: '🇦🇺 AUD — Australian Dollar' },
];

export default function RegisterPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // 1. Create the user
      await apiClient.post('/register', {
        email,
        full_name: fullName,
        password,
        preferred_currency: currency
      });

      // 2. Log them in to get the token
      const formParams = new URLSearchParams();
      formParams.append('username', email);
      formParams.append('password', password);
      
      const loginRes = await apiClient.post('/login/access-token', formParams, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      const token = loginRes.data.access_token;
      
      // 3. Fetch their profile to populate the store
      const userRes = await apiClient.get('/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      login(userRes.data, token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] bg-violet-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/4 w-[300px] h-[300px] bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md">
        <Link to="/" className="flex items-center justify-center gap-2 text-xl font-bold text-white mb-8">
          <ScanLine className="text-indigo-400" />
          Split It <span className="text-indigo-400">Fair</span>
        </Link>

        <div className="bg-slate-900/80 backdrop-blur-md border border-white/10 rounded-3xl p-8 shadow-2xl">
          <h1 className="text-2xl font-bold text-white mb-1">Create Account</h1>
          <p className="text-sm text-slate-400 mb-8">Start splitting expenses fairly in seconds.</p>

          {error && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm rounded-xl px-4 py-3 mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-5">
            <Input
              id="register-name"
              label="Full Name"
              placeholder="John Doe"
              icon={<User size={16} />}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
            <Input
              id="register-email"
              label="Email"
              type="email"
              placeholder="you@example.com"
              icon={<Mail size={16} />}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              id="register-password"
              label="Password"
              type="password"
              placeholder="Min 8 characters"
              icon={<Lock size={16} />}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
            <Select
              id="register-currency"
              label="Preferred Currency"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              options={CURRENCIES}
            />
            <Button type="submit" fullWidth loading={loading} icon={<Coins size={16} />}>
              Create Account
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
