import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useGroupStore } from '../store/useGroupStore';
import { useExpenseStore } from '../store/useExpenseStore';
import { useAuthStore } from '../store/useAuthStore';
import StatCards from '../components/dashboard/StatCards';
import ExpenseList from '../components/expenses/ExpenseList';
import NewExpenseForm from '../components/expenses/NewExpenseForm';
import {
  Plus, UserPlus, Users, LogOut, ArrowLeft, Mail, X,
  ChevronDown, ChevronUp,
} from 'lucide-react';

export default function GroupDashboard() {
  const { groupId } = useParams<{ groupId: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const {
    currentGroup, fetchGroupDetail,
    inviteMember, leaveGroup, fetchBalances, balances,
  } = useGroupStore();
  const { stats, expenses, fetchStats, fetchExpenses } = useExpenseStore();

  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteMsg, setInviteMsg] = useState('');
  const [inviteError, setInviteError] = useState('');
  const [showInvite, setShowInvite] = useState(false);
  const [expandMembers, setExpandMembers] = useState(false);
  const [selectedMember, setSelectedMember] = useState<string | null>(null);
  const [leaveLoading, setLeaveLoading] = useState(false);

  useEffect(() => {
    if (groupId) {
      fetchGroupDetail(groupId);
      fetchStats(groupId);
      fetchExpenses(groupId);
      fetchBalances(groupId);
    }
  }, [groupId, fetchGroupDetail, fetchStats, fetchExpenses, fetchBalances]);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!groupId || !inviteEmail.trim()) return;
    setInviteError('');
    setInviteMsg('');
    try {
      await inviteMember(groupId, inviteEmail.trim());
      setInviteMsg(`Invite sent to ${inviteEmail}`);
      setInviteEmail('');
      fetchGroupDetail(groupId);
    } catch (err: any) {
      setInviteError(err.message);
    }
  };

  const handleLeave = async () => {
    if (!groupId) return;
    if (!confirm('Are you sure you want to leave this group?')) return;
    setLeaveLoading(true);
    try {
      await leaveGroup(groupId);
      navigate('/dashboard');
    } catch (err: any) {
      alert(err.message);
    }
    setLeaveLoading(false);
  };

  const handleExpenseSuccess = () => {
    if (groupId) {
      fetchStats(groupId);
      fetchExpenses(groupId);
      fetchBalances(groupId);
    }
  };

  // Compute member-specific balance from balances data
  const getMemberBalance = (memberId: string): number => {
    if (!user) return 0;
    let net = 0;
    for (const b of balances) {
      if (b.from_user_id === user.id && b.to_user_id === memberId) {
        net -= b.amount; // you owe them
      }
      if (b.from_user_id === memberId && b.to_user_id === user.id) {
        net += b.amount; // they owe you
      }
    }
    return net;
  };

  const fmt = (n: number) =>
    new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Math.abs(n));

  if (!currentGroup) {
    return (
      <div className="dashboard-page">
        <div className="loading-state">Loading group...</div>
      </div>
    );
  }

  const acceptedMembers = currentGroup.members.filter((m) => m.status === 'ACCEPTED');
  const pendingMembers = currentGroup.members.filter((m) => m.status === 'PENDING');
  const selMember = selectedMember
    ? currentGroup.members.find((m) => m.user_id === selectedMember)
    : null;

  return (
    <div className="dashboard-page">
      {/* Header */}
      <div className="dash-header">
        <div className="dash-header-left">
          <button className="btn-icon" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="dash-title">{currentGroup.name}</h1>
            {currentGroup.description && (
              <p className="dash-subtitle">{currentGroup.description}</p>
            )}
          </div>
        </div>
        <div className="dash-header-actions">
          <button className="btn btn-primary" onClick={() => setShowExpenseForm(true)}>
            <Plus size={18} /> New Expense
          </button>
          <button
            className="btn btn-ghost btn-danger-ghost"
            onClick={handleLeave}
            disabled={leaveLoading}
          >
            <LogOut size={16} /> Leave
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && <StatCards stats={stats} />}

      {/* Add Member */}
      <div className="dash-section">
        <div className="section-header">
          <h2 className="section-heading">
            <UserPlus size={20} /> Add Member
          </h2>
          <button className="btn btn-sm btn-ghost" onClick={() => setShowInvite(!showInvite)}>
            {showInvite ? 'Cancel' : 'Invite'}
          </button>
        </div>
        {showInvite && (
          <form className="invite-form" onSubmit={handleInvite}>
            <div className="invite-input-group">
              <Mail size={16} className="invite-icon" />
              <input
                type="email"
                placeholder="Enter email address"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                required
              />
              <button type="submit" className="btn btn-primary btn-sm">
                Send Invite
              </button>
            </div>
            {inviteMsg && <p className="invite-success">{inviteMsg}</p>}
            {inviteError && <p className="invite-error">{inviteError}</p>}
          </form>
        )}
      </div>

      {/* Group Expense List */}
      <div className="dash-section">
        <h2 className="section-heading">Group Expenses</h2>
        <ExpenseList expenses={expenses} />
      </div>

      {/* Members */}
      <div className="dash-section">
        <div
          className="section-header clickable"
          onClick={() => setExpandMembers(!expandMembers)}
        >
          <h2 className="section-heading">
            <Users size={20} /> Members ({acceptedMembers.length})
            {pendingMembers.length > 0 && (
              <span className="pending-badge">{pendingMembers.length} pending</span>
            )}
          </h2>
          {expandMembers ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>

        {expandMembers && (
          <div className="members-list">
            {currentGroup.members.map((m) => {
              const balance = getMemberBalance(m.user_id);
              const isMe = m.user_id === user?.id;

              return (
                <div
                  key={m.user_id}
                  className={`member-row ${selectedMember === m.user_id ? 'selected' : ''} ${m.status === 'PENDING' ? 'pending' : ''}`}
                  onClick={() => !isMe && setSelectedMember(
                    selectedMember === m.user_id ? null : m.user_id
                  )}
                >
                  <div className="member-row-left">
                    <div className="member-avatar">
                      {(m.full_name || m.email).charAt(0).toUpperCase()}
                    </div>
                    <div className="member-info">
                      <span className="member-name">
                        {m.full_name || m.email}
                        {isMe && <span className="you-badge">You</span>}
                      </span>
                      <span className="member-email">{m.email}</span>
                    </div>
                  </div>
                  <div className="member-row-right">
                    {m.status === 'PENDING' && (
                      <span className="status-badge pending">Pending</span>
                    )}
                    {m.status === 'ACCEPTED' && !isMe && (
                      <span className={`member-balance ${balance >= 0 ? 'positive' : 'negative'}`}>
                        {balance >= 0 ? `+$${fmt(balance)}` : `-$${fmt(balance)}`}
                      </span>
                    )}
                    <span className="member-currency">{m.preferred_currency}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Member detail overlay */}
        {selMember && (
          <div className="member-detail">
            <div className="member-detail-header">
              <div className="member-detail-avatar">
                {(selMember.full_name || selMember.email).charAt(0).toUpperCase()}
              </div>
              <div>
                <h3>{selMember.full_name || selMember.email}</h3>
                <p>{selMember.email}</p>
              </div>
              <button className="btn-icon" onClick={() => setSelectedMember(null)}>
                <X size={18} />
              </button>
            </div>
            <div className="member-detail-body">
              <div className="detail-row">
                <span>Currency</span>
                <span className="detail-value">{selMember.preferred_currency}</span>
              </div>
              <div className="detail-row">
                <span>Status</span>
                <span className={`detail-value status-${selMember.status.toLowerCase()}`}>
                  {selMember.status}
                </span>
              </div>
              {selMember.status === 'ACCEPTED' && (() => {
                const bal = getMemberBalance(selMember.user_id);
                return (
                  <div className="detail-row">
                    <span>Balance with you</span>
                    <span className={`detail-value ${bal >= 0 ? 'positive' : 'negative'}`}>
                      {bal > 0 ? `They owe you $${fmt(bal)}` :
                       bal < 0 ? `You owe them $${fmt(bal)}` :
                       'Settled up ✓'}
                    </span>
                  </div>
                );
              })()}
            </div>
          </div>
        )}
      </div>

      {/* Expense modal */}
      {showExpenseForm && (
        <NewExpenseForm
          onClose={() => setShowExpenseForm(false)}
          preselectedGroupId={groupId}
          onSuccess={handleExpenseSuccess}
        />
      )}
    </div>
  );
}
