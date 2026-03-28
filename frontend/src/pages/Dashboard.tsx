import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users, Plus, TrendingDown, TrendingUp, Receipt,
  ArrowUpRight, ArrowDownRight, PlusCircle,
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import StatCard from '../components/dashboard/StatCard';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Modal from '../components/common/Modal';
import ExpenseForm from '../components/forms/ExpenseForm';
import type { ExpenseFormData } from '../components/forms/ExpenseForm';
import type { Group, GroupDebt } from '../types';

// ─── Mock Data (replace with API) ───────────────────────────────────────────
const MOCK_GROUPS: Group[] = [
  { id: '1', name: 'Miami Trip \'24', description: 'Spring break with the crew', created_at: new Date().toISOString() },
  { id: '2', name: 'Apartment Utilities', description: 'Monthly rent & bills', created_at: new Date().toISOString() },
];

const MOCK_DEBTS: GroupDebt[] = [
  { group_id: '1', group_name: 'Miami Trip \'24', you_owe: 0, you_are_owed: 45.00 },
  { group_id: '2', group_name: 'Apartment Utilities', you_owe: 12.50, you_are_owed: 0 },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [groups, setGroups] = useState<Group[]>(MOCK_GROUPS);
  const [showNewGroup, setShowNewGroup] = useState(false);
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupDesc, setNewGroupDesc] = useState('');

  const totalOwed = MOCK_DEBTS.reduce((s, d) => s + d.you_are_owed, 0);
  const totalToPay = MOCK_DEBTS.reduce((s, d) => s + d.you_owe, 0);

  const handleCreateGroup = () => {
    if (!newGroupName.trim()) return;
    const newGroup: Group = {
      id: String(groups.length + 1),
      name: newGroupName,
      description: newGroupDesc || null,
      created_at: new Date().toISOString(),
    };
    setGroups([...groups, newGroup]);
    setNewGroupName('');
    setNewGroupDesc('');
    setShowNewGroup(false);
  };

  const handleNewExpense = (data: ExpenseFormData) => {
    console.log('New expense created:', data);
    setShowExpenseForm(false);
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* ── Header ───────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-10">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard</h1>
            <p className="text-slate-400 mt-1">Your global expense summary across all groups.</p>
          </div>
          <Button
            variant="primary"
            icon={<PlusCircle size={18} />}
            onClick={() => setShowExpenseForm(true)}
            className="shadow-lg shadow-indigo-500/20"
          >
            New Expense
          </Button>
        </div>

        {/* ── Aggregated Stats ─────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12">
          <StatCard
            icon={<TrendingUp size={24} />}
            label="Total Owed to You"
            value={`$${totalOwed.toFixed(2)}`}
            accentColor="emerald"
          />
          <StatCard
            icon={<TrendingDown size={24} />}
            label="Total You Owe"
            value={`$${totalToPay.toFixed(2)}`}
            accentColor="rose"
          />
          <StatCard
            icon={<Receipt size={24} />}
            label="Net Balance"
            value={`$${(totalOwed - totalToPay).toFixed(2)}`}
            accentColor={totalOwed - totalToPay >= 0 ? 'emerald' : 'rose'}
            subtitle={totalOwed - totalToPay >= 0 ? 'You\'re in the green' : 'You owe more overall'}
          />
        </div>

        {/* ── Per-Group Debts ──────────────────────────────────────────── */}
        <div className="mb-12">
          <h2 className="text-lg font-semibold text-white mb-4">Breakdown by Group</h2>
          <div className="space-y-3">
            {MOCK_DEBTS.map((debt) => (
              <div
                key={debt.group_id}
                onClick={() => navigate(`/groups/${debt.group_id}`)}
                className="flex items-center justify-between bg-slate-900 border border-white/5 rounded-2xl p-5 cursor-pointer hover:border-white/10 transition-all hover:-translate-y-0.5 group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10">
                    <Users className="text-indigo-400" size={20} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white group-hover:text-indigo-300 transition-colors">{debt.group_name}</h3>
                    <p className="text-sm text-slate-500">Click to view details</p>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  {debt.you_are_owed > 0 && (
                    <span className="flex items-center gap-1 text-sm font-medium text-emerald-400">
                      <ArrowUpRight size={14} /> +${debt.you_are_owed.toFixed(2)}
                    </span>
                  )}
                  {debt.you_owe > 0 && (
                    <span className="flex items-center gap-1 text-sm font-medium text-rose-400">
                      <ArrowDownRight size={14} /> -${debt.you_owe.toFixed(2)}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Group List & New Group ───────────────────────────────────── */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Your Groups</h2>
            <Button variant="secondary" icon={<Plus size={16} />} onClick={() => setShowNewGroup(true)}>
              Create New Group
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {groups.map((group) => {
              const debt = MOCK_DEBTS.find((d) => d.group_id === group.id);
              const isPositive = (debt?.you_are_owed || 0) > (debt?.you_owe || 0);
              return (
                <div
                  key={group.id}
                  onClick={() => navigate(`/groups/${group.id}`)}
                  className="group cursor-pointer bg-slate-900 rounded-2xl border border-white/5 p-6
                    hover:border-indigo-500/30 transition-all hover:-translate-y-1.5 duration-300
                    hover:shadow-2xl hover:shadow-indigo-500/5"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="p-3 bg-indigo-500/10 rounded-xl">
                      <Users className="text-indigo-400" size={22} />
                    </div>
                    {debt && (
                      <span
                        className={`text-xs font-medium px-2.5 py-1 rounded-lg ${
                          isPositive
                            ? 'text-emerald-400 bg-emerald-400/10'
                            : 'text-rose-400 bg-rose-400/10'
                        }`}
                      >
                        {isPositive ? `+$${debt.you_are_owed.toFixed(2)}` : `-$${debt.you_owe.toFixed(2)}`}
                      </span>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-white mb-1 group-hover:text-indigo-300 transition-colors">
                    {group.name}
                  </h3>
                  <p className="text-sm text-slate-500 line-clamp-1">{group.description || 'No description'}</p>
                </div>
              );
            })}
          </div>
        </div>
      </main>

      {/* ── New Group Modal ───────────────────────────────────────────── */}
      <Modal isOpen={showNewGroup} onClose={() => setShowNewGroup(false)} title="Create New Group">
        <div className="space-y-4">
          <Input
            id="new-group-name"
            label="Group Name"
            placeholder="e.g. Road Trip 2024"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
          />
          <Input
            id="new-group-desc"
            label="Description (optional)"
            placeholder="What's this group for?"
            value={newGroupDesc}
            onChange={(e) => setNewGroupDesc(e.target.value)}
          />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="ghost" onClick={() => setShowNewGroup(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleCreateGroup} disabled={!newGroupName.trim()}>
              Create Group
            </Button>
          </div>
        </div>
      </Modal>

      {/* ── New Expense Modal ─────────────────────────────────────────── */}
      <Modal isOpen={showExpenseForm} onClose={() => setShowExpenseForm(false)} title="Add New Expense" size="lg">
        <ExpenseForm
          groups={groups}
          onSubmit={handleNewExpense}
          onCancel={() => setShowExpenseForm(false)}
        />
      </Modal>
    </div>
  );
}
