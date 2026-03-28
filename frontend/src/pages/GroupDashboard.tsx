import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Receipt, History, Users, PlusCircle,
  TrendingUp, TrendingDown, UserCircle, Coins, X,
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import StatCard from '../components/dashboard/StatCard';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import ExpenseForm from '../components/forms/ExpenseForm';
import type { ExpenseFormData } from '../components/forms/ExpenseForm';
import type { Group, GroupMember } from '../types';

// ─── Mock Data (replace with API) ───────────────────────────────────────────
const MOCK_GROUPS: Record<string, Group> = {
  '1': { id: '1', name: "Miami Trip '24", description: 'Spring break with the crew', created_at: new Date().toISOString() },
  '2': { id: '2', name: 'Apartment Utilities', description: 'Monthly rent & bills', created_at: new Date().toISOString() },
};

const MOCK_MEMBERS: Record<string, GroupMember[]> = {
  '1': [
    { user_id: '1', full_name: 'Demo User', email: 'demo@splititfair.com', preferred_currency: 'USD', balance: 45.00 },
    { user_id: '2', full_name: 'Alice Johnson', email: 'alice@test.com', preferred_currency: 'USD', balance: -20.00 },
    { user_id: '3', full_name: 'Bob Williams', email: 'bob@test.com', preferred_currency: 'USD', balance: -25.00 },
    { user_id: '6', full_name: 'Eve Parker', email: 'eve@test.com', preferred_currency: 'EUR', balance: 0 },
  ],
  '2': [
    { user_id: '1', full_name: 'Demo User', email: 'demo@splititfair.com', preferred_currency: 'USD', balance: -12.50 },
    { user_id: '4', full_name: 'Charlie Brown', email: 'charlie@test.com', preferred_currency: 'EUR', balance: 8.00 },
    { user_id: '5', full_name: 'Diana Prince', email: 'diana@test.com', preferred_currency: 'GBP', balance: 4.50 },
  ],
};

const GROUP_STATS: Record<string, { totalSpending: number; totalTransactions: number }> = {
  '1': { totalSpending: 1240.00, totalTransactions: 8 },
  '2': { totalSpending: 345.75, totalTransactions: 4 },
};

export default function GroupDashboard() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const group = MOCK_GROUPS[id || ''];
  const members = useMemo(() => MOCK_MEMBERS[id || ''] || [], [id]);
  const stats = GROUP_STATS[id || ''] || { totalSpending: 0, totalTransactions: 0 };

  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [selectedMember, setSelectedMember] = useState<GroupMember | null>(null);

  const myBalance = members.find((m) => m.user_id === '1')?.balance || 0;
  const totalOwedToYou = members.filter((m) => m.balance < 0).reduce((s, m) => s + Math.abs(m.balance), 0);
  const totalYouOwe = members.filter((m) => m.balance > 0 && m.user_id !== '1').reduce((s, m) => s + m.balance, 0);

  const handleNewExpense = (data: ExpenseFormData) => {
    console.log('Group expense created:', data);
    setShowExpenseForm(false);
  };

  if (!group) {
    return (
      <div className="min-h-screen bg-slate-950">
        <Navbar />
        <div className="flex flex-col items-center justify-center h-[60vh] text-slate-400">
          <p className="text-lg">Group not found.</p>
          <Button variant="ghost" className="mt-4" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* ── Back Button ──────────────────────────────────────────────── */}
        <button
          onClick={() => navigate('/dashboard')}
          className="group mb-6 flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
          Back to Dashboard
        </button>

        {/* ── Group Header ─────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-slate-900 border border-white/5 p-8 rounded-3xl relative overflow-hidden mb-8">
          <div className="absolute right-0 top-0 w-72 h-72 bg-indigo-500/5 blur-[80px] rounded-full pointer-events-none" />
          <div className="relative z-10">
            <h1 className="text-3xl font-extrabold text-white tracking-tight mb-1">{group.name}</h1>
            <p className="text-slate-400">{group.description}</p>
            <div className="flex items-center gap-3 mt-3">
              <span className="text-xs text-slate-500 bg-slate-800 px-2.5 py-1 rounded-lg flex items-center gap-1.5">
                <Users size={12} /> {members.length} members
              </span>
              <span
                className={`text-xs font-medium px-2.5 py-1 rounded-lg flex items-center gap-1.5 ${
                  myBalance >= 0 ? 'text-emerald-400 bg-emerald-400/10' : 'text-rose-400 bg-rose-400/10'
                }`}
              >
                {myBalance >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                {myBalance >= 0 ? `You are owed $${myBalance.toFixed(2)}` : `You owe $${Math.abs(myBalance).toFixed(2)}`}
              </span>
            </div>
          </div>
          <Button
            variant="primary"
            className="mt-4 sm:mt-0 z-10"
            icon={<PlusCircle size={18} />}
            onClick={() => setShowExpenseForm(true)}
          >
            Add Expense
          </Button>
        </div>

        {/* ── Stats Grid ───────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
          <StatCard icon={<Receipt size={22} />} label="Total Spending" value={`$${stats.totalSpending.toFixed(2)}`} accentColor="indigo" />
          <StatCard icon={<History size={22} />} label="Transactions" value={String(stats.totalTransactions)} accentColor="amber" />
          <StatCard icon={<TrendingUp size={22} />} label="Owed to You" value={`$${totalOwedToYou.toFixed(2)}`} accentColor="emerald" />
          <StatCard icon={<TrendingDown size={22} />} label="You Owe" value={`$${totalYouOwe.toFixed(2)}`} accentColor="rose" />
        </div>

        {/* ── Members List ─────────────────────────────────────────────── */}
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Group Members</h2>
          <div className="space-y-3">
            {members.map((member) => {
              const isYou = member.user_id === '1';
              // positive balance = they owe you, negative = you owe them (from YOUR perspective)
              const balanceLabel = isYou
                ? null
                : member.balance < 0
                ? `Owes you $${Math.abs(member.balance).toFixed(2)}`
                : member.balance > 0
                ? `You owe $${member.balance.toFixed(2)}`
                : 'Settled';
              const balanceColor = member.balance < 0 ? 'text-emerald-400' : member.balance > 0 ? 'text-rose-400' : 'text-slate-500';

              return (
                <div
                  key={member.user_id}
                  onClick={() => !isYou && setSelectedMember(member)}
                  className={`flex items-center justify-between bg-slate-900 border border-white/5 rounded-2xl p-5 transition-all
                    ${!isYou ? 'cursor-pointer hover:border-white/10 hover:-translate-y-0.5' : 'opacity-80'}`}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white font-bold text-sm">
                      {member.full_name[0]}
                    </div>
                    <div>
                      <h3 className="font-medium text-white">
                        {member.full_name} {isYou && <span className="text-xs text-indigo-400 ml-1">(You)</span>}
                      </h3>
                      <p className="text-sm text-slate-500">{member.email}</p>
                    </div>
                  </div>
                  {balanceLabel && (
                    <span className={`text-sm font-medium ${balanceColor}`}>{balanceLabel}</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </main>

      {/* ── Member Profile Modal ──────────────────────────────────────── */}
      {selectedMember && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSelectedMember(null)} />
          <div className="relative w-full max-w-sm bg-slate-900 border border-white/10 rounded-3xl shadow-2xl overflow-hidden">
            {/* gradient header */}
            <div className="relative h-28 bg-gradient-to-br from-indigo-600 to-violet-600 flex items-end pb-4 px-6">
              <button
                onClick={() => setSelectedMember(null)}
                className="absolute top-4 right-4 p-1.5 rounded-lg bg-black/20 hover:bg-black/40 text-white/80 hover:text-white transition-colors"
              >
                <X size={16} />
              </button>
              <div className="w-14 h-14 rounded-full bg-white/20 backdrop-blur-md border-2 border-white/30 flex items-center justify-center text-white text-xl font-bold shadow-xl translate-y-6">
                {selectedMember.full_name[0]}
              </div>
            </div>

            <div className="px-6 pt-10 pb-6 space-y-5">
              <div>
                <h2 className="text-xl font-bold text-white">{selectedMember.full_name}</h2>
                <p className="text-sm text-slate-400">{selectedMember.email}</p>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between bg-slate-800/50 border border-white/5 rounded-xl p-4">
                  <div className="flex items-center gap-3">
                    <Coins size={18} className="text-amber-400" />
                    <span className="text-sm text-slate-300">Currency</span>
                  </div>
                  <span className="font-mono font-medium text-white">{selectedMember.preferred_currency}</span>
                </div>

                <div className="flex items-center justify-between bg-slate-800/50 border border-white/5 rounded-xl p-4">
                  <div className="flex items-center gap-3">
                    <UserCircle size={18} className={selectedMember.balance < 0 ? 'text-emerald-400' : selectedMember.balance > 0 ? 'text-rose-400' : 'text-slate-400'} />
                    <span className="text-sm text-slate-300">Balance with you</span>
                  </div>
                  <span
                    className={`font-mono font-bold text-lg ${
                      selectedMember.balance < 0
                        ? 'text-emerald-400'
                        : selectedMember.balance > 0
                        ? 'text-rose-400'
                        : 'text-slate-500'
                    }`}
                  >
                    {selectedMember.balance < 0
                      ? `+$${Math.abs(selectedMember.balance).toFixed(2)}`
                      : selectedMember.balance > 0
                      ? `-$${selectedMember.balance.toFixed(2)}`
                      : '$0.00'}
                  </span>
                </div>

                <p className="text-xs text-slate-500 text-center pt-2">
                  {selectedMember.balance < 0
                    ? `${selectedMember.full_name} owes you money in this group.`
                    : selectedMember.balance > 0
                    ? `You owe ${selectedMember.full_name} money in this group.`
                    : `All settled with ${selectedMember.full_name}!`}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── New Expense Modal (auto-selects this group) ───────────────── */}
      <Modal isOpen={showExpenseForm} onClose={() => setShowExpenseForm(false)} title="Add Expense" size="lg">
        <ExpenseForm
          groups={[group]}
          preSelectedGroupId={group.id}
          onSubmit={handleNewExpense}
          onCancel={() => setShowExpenseForm(false)}
        />
      </Modal>
    </div>
  );
}
