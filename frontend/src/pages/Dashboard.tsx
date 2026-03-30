import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { useExpenseStore } from '../store/useExpenseStore';
import { useGroupStore } from '../store/useGroupStore';
import StatCards from '../components/dashboard/StatCards';
import GroupDebtList from '../components/dashboard/GroupDebtList';
import ExpenseList from '../components/expenses/ExpenseList';
import NewExpenseForm from '../components/expenses/NewExpenseForm';
import { Plus, Users, FolderPlus, ArrowRight, Receipt } from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuthStore();
  const { stats, expenses, fetchStats, fetchExpenses } = useExpenseStore();
  const { groups, fetchGroups, createGroup, isLoading: groupsLoading } = useGroupStore();
  const navigate = useNavigate();

  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupDesc, setNewGroupDesc] = useState('');

  useEffect(() => {
    fetchStats();
    fetchExpenses();
    fetchGroups();
  }, [fetchStats, fetchExpenses, fetchGroups]);

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGroupName.trim()) return;
    await createGroup(newGroupName.trim(), newGroupDesc.trim() || undefined);
    setNewGroupName('');
    setNewGroupDesc('');
    setShowCreateGroup(false);
  };

  const handleExpenseSuccess = () => {
    fetchStats();
    fetchExpenses();
  };

  return (
    <div className="dashboard-page">
      {/* Header section */}
      <div className="dash-header">
        <div>
          <h1 className="dash-title">Dashboard</h1>
          <p className="dash-subtitle">
            Welcome back, <strong>{user?.full_name || user?.email}</strong>
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowExpenseForm(true)}>
          <Plus size={18} /> New Expense
        </button>
      </div>

      {/* Stats */}
      {stats && <StatCards stats={stats} />}

      {/* Group debts */}
      {stats && stats.debts_by_group.length > 0 && (
        <div className="dash-section">
          <h2 className="section-heading">Balances by Group</h2>
          <GroupDebtList debts={stats.debts_by_group} />
        </div>
      )}

      {/* Global Expense List */}
      <div className="dash-section">
        <div className="section-header">
          <h2 className="section-heading">
            <Receipt size={20} /> Recent Expenses
          </h2>
        </div>
        <ExpenseList expenses={expenses.slice(0, 10)} showGroup />
      </div>

      {/* Groups */}
      <div className="dash-section">
        <div className="section-header">
          <h2 className="section-heading">
            <Users size={20} /> Your Groups
          </h2>
          <button className="btn btn-sm btn-ghost" onClick={() => setShowCreateGroup(!showCreateGroup)}>
            <FolderPlus size={16} /> New Group
          </button>
        </div>

        {showCreateGroup && (
          <form className="create-group-form" onSubmit={handleCreateGroup}>
            <input
              type="text"
              placeholder="Group name"
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
              required
              autoFocus
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={newGroupDesc}
              onChange={(e) => setNewGroupDesc(e.target.value)}
            />
            <button type="submit" className="btn btn-primary btn-sm" disabled={groupsLoading}>
              Create
            </button>
          </form>
        )}

        {groups.length === 0 ? (
          <div className="empty-state">
            <Users size={32} className="empty-icon" />
            <p>No groups yet. Create one to start splitting!</p>
          </div>
        ) : (
          <div className="group-grid">
            {groups.map((g) => (
              <div
                key={g.id}
                className="group-card"
                onClick={() => navigate(`/groups/${g.id}`)}
              >
                <div className="group-card-header">
                  <span className="group-card-avatar">{g.name.charAt(0).toUpperCase()}</span>
                  <div>
                    <h3 className="group-card-name">{g.name}</h3>
                    {g.description && <p className="group-card-desc">{g.description}</p>}
                  </div>
                </div>
                <div className="group-card-footer">
                  <span className="group-card-date">
                    Created {new Date(g.created_at).toLocaleDateString()}
                  </span>
                  <ArrowRight size={16} className="group-card-arrow" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Expense modal */}
      {showExpenseForm && (
        <NewExpenseForm
          onClose={() => setShowExpenseForm(false)}
          onSuccess={handleExpenseSuccess}
        />
      )}
    </div>
  );
}
