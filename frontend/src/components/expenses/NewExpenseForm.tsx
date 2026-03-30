import { useState, useEffect } from 'react';
import { X, Trash2 } from 'lucide-react';
import { useExpenseStore } from '../../store/useExpenseStore';
import { useGroupStore } from '../../store/useGroupStore';
import { useAuthStore } from '../../store/useAuthStore';
import type { SplitType, RecurringFrequency, GroupMember } from '../../types';

interface Props {
  onClose: () => void;
  preselectedGroupId?: string;
  onSuccess?: () => void;
}

const CURRENCIES = ['USD', 'EUR', 'GBP', 'INR', 'JPY', 'CAD', 'AUD', 'CHF'];
const DAYS_OF_WEEK = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

export default function NewExpenseForm({ onClose, preselectedGroupId, onSuccess }: Props) {
  const { createExpense, isLoading, error, clearError } = useExpenseStore();
  const { groups, fetchGroupDetail, currentGroup } = useGroupStore();
  const { user } = useAuthStore();

  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState(user?.preferred_currency || 'USD');
  const [groupId, setGroupId] = useState(preselectedGroupId || '');
  const [splitType, setSplitType] = useState<SplitType>('EQUAL');
  const [expenseDate, setExpenseDate] = useState(new Date().toISOString().split('T')[0]);
  const [payerId, setPayerId] = useState(user?.id || '');

  // Recurring
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurringFrequency, setRecurringFrequency] = useState<RecurringFrequency>('MONTHLY');
  const [recurringDayOfWeek, setRecurringDayOfWeek] = useState(0);
  const [recurringDayOfMonth, setRecurringDayOfMonth] = useState(1);

  // Splits
  const [splitUsers, setSplitUsers] = useState<{
    user_id: string;
    name: string;
    percentage?: string;
    share?: string;
    amount_owed?: string;
  }[]>([]);

  // Members for selected group
  const [members, setMembers] = useState<GroupMember[]>([]);

  useEffect(() => {
    if (groupId) {
      fetchGroupDetail(groupId);
    }
  }, [groupId, fetchGroupDetail]);

  useEffect(() => {
    if (currentGroup && currentGroup.id === groupId) {
      const accepted = currentGroup.members.filter((m) => m.status === 'ACCEPTED');
      setMembers(accepted);
      // Auto-populate split users with all accepted members
      setSplitUsers(
        accepted.map((m) => ({
          user_id: m.user_id,
          name: m.full_name || m.email,
        }))
      );
      // Ensure payer is in group
      if (!accepted.find((m) => m.user_id === payerId)) {
        setPayerId(user?.id || '');
      }
    }
  }, [currentGroup, groupId, payerId, user?.id]);

  const removeSplitUser = (userId: string) => {
    setSplitUsers((prev) => prev.filter((s) => s.user_id !== userId));
  };

  const updateSplitField = (userId: string, field: string, value: string) => {
    setSplitUsers((prev) =>
      prev.map((s) => (s.user_id === userId ? { ...s, [field]: value } : s))
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    const splits = splitUsers.map((s) => {
      const entry: any = { user_id: s.user_id };
      if (splitType === 'PERCENTAGE' && s.percentage) entry.percentage = parseFloat(s.percentage);
      if (splitType === 'SHARE' && s.share) entry.share = parseInt(s.share);
      if (splitType === 'ITEM' && s.amount_owed) entry.amount_owed = parseFloat(s.amount_owed);
      return entry;
    });

    const payload: any = {
      description,
      amount: parseFloat(amount),
      currency,
      group_id: groupId,
      split_type: splitType,
      expense_date: expenseDate,
      payer_id: payerId,
      splits,
      is_recurring: isRecurring,
    };

    if (isRecurring) {
      payload.recurring_frequency = recurringFrequency;
      if (recurringFrequency === 'WEEKLY') payload.recurring_day_of_week = recurringDayOfWeek;
      if (recurringFrequency === 'MONTHLY' || recurringFrequency === 'SEMI_MONTHLY') {
        payload.recurring_day_of_month = recurringDayOfMonth;
      }
    }

    try {
      await createExpense(payload);
      onSuccess?.();
      onClose();
    } catch { /* error set in store */ }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>New Expense</h2>
          <button className="modal-close" onClick={onClose}><X size={20} /></button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {error && <div className="form-error">{error}</div>}

          {/* Title */}
          <div className="form-group">
            <label htmlFor="expense-title">Title</label>
            <input
              id="expense-title"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Dinner, Groceries, Rent..."
              required
              maxLength={200}
            />
          </div>

          {/* Amount + Currency */}
          <div className="form-row">
            <div className="form-group form-grow">
              <label htmlFor="expense-amount">Amount</label>
              <input
                id="expense-amount"
                type="number"
                step="0.01"
                min="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                required
              />
            </div>
            <div className="form-group" style={{ width: '120px' }}>
              <label htmlFor="expense-currency">Currency</label>
              <select id="expense-currency" value={currency} onChange={(e) => setCurrency(e.target.value)}>
                {CURRENCIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Group */}
          <div className="form-group">
            <label htmlFor="expense-group">Group</label>
            <select
              id="expense-group"
              value={groupId}
              onChange={(e) => setGroupId(e.target.value)}
              required
              disabled={!!preselectedGroupId}
            >
              <option value="">Select a group</option>
              {groups.map((g) => (
                <option key={g.id} value={g.id}>{g.name}</option>
              ))}
            </select>
          </div>

          {/* Payer + Date */}
          <div className="form-row">
            <div className="form-group form-grow">
              <label htmlFor="expense-payer">Payer</label>
              <select id="expense-payer" value={payerId} onChange={(e) => setPayerId(e.target.value)}>
                {members.map((m) => (
                  <option key={m.user_id} value={m.user_id}>
                    {m.full_name || m.email} {m.user_id === user?.id ? '(You)' : ''}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group" style={{ width: '160px' }}>
              <label htmlFor="expense-date">Date</label>
              <input
                id="expense-date"
                type="date"
                value={expenseDate}
                onChange={(e) => setExpenseDate(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Split Method */}
          <div className="form-group">
            <label>Split Method</label>
            <div className="split-method-tabs">
              {(['EQUAL', 'PERCENTAGE', 'SHARE', 'ITEM'] as SplitType[]).map((method) => (
                <button
                  key={method}
                  type="button"
                  className={`split-tab ${splitType === method ? 'active' : ''}`}
                  onClick={() => setSplitType(method)}
                >
                  {method === 'ITEM' ? 'Exact' : method.charAt(0) + method.slice(1).toLowerCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Split entries */}
          {groupId && splitUsers.length > 0 && (
            <div className="form-group">
              <label>Split Between</label>
              <div className="split-entries">
                {splitUsers.map((su) => (
                  <div key={su.user_id} className="split-entry">
                    <span className="split-entry-name">{su.name}</span>

                    {splitType === 'PERCENTAGE' && (
                      <div className="split-entry-input">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          max="100"
                          placeholder="%"
                          value={su.percentage || ''}
                          onChange={(e) => updateSplitField(su.user_id, 'percentage', e.target.value)}
                        />
                        <span className="input-suffix">%</span>
                      </div>
                    )}

                    {splitType === 'SHARE' && (
                      <div className="split-entry-input">
                        <input
                          type="number"
                          step="1"
                          min="1"
                          placeholder="Shares"
                          value={su.share || ''}
                          onChange={(e) => updateSplitField(su.user_id, 'share', e.target.value)}
                        />
                        <span className="input-suffix">×</span>
                      </div>
                    )}

                    {splitType === 'ITEM' && (
                      <div className="split-entry-input">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="Amount"
                          value={su.amount_owed || ''}
                          onChange={(e) => updateSplitField(su.user_id, 'amount_owed', e.target.value)}
                        />
                        <span className="input-suffix">{currency}</span>
                      </div>
                    )}

                    {splitUsers.length > 1 && (
                      <button
                        type="button"
                        className="split-entry-remove"
                        onClick={() => removeSplitUser(su.user_id)}
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recurring toggle */}
          <div className="form-group">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={isRecurring}
                onChange={(e) => setIsRecurring(e.target.checked)}
              />
              <span className="toggle-slider"></span>
              Recurring Expense
            </label>
          </div>

          {isRecurring && (
            <div className="recurring-options">
              <div className="form-group">
                <label htmlFor="recurring-freq">Frequency</label>
                <select
                  id="recurring-freq"
                  value={recurringFrequency}
                  onChange={(e) => setRecurringFrequency(e.target.value as RecurringFrequency)}
                >
                  <option value="DAILY">Daily</option>
                  <option value="WEEKLY">Weekly</option>
                  <option value="MONTHLY">Monthly</option>
                  <option value="SEMI_MONTHLY">Semi-Monthly</option>
                  <option value="YEARLY">Yearly</option>
                </select>
              </div>

              {recurringFrequency === 'WEEKLY' && (
                <div className="form-group">
                  <label htmlFor="recurring-dow">Day of Week</label>
                  <select
                    id="recurring-dow"
                    value={recurringDayOfWeek}
                    onChange={(e) => setRecurringDayOfWeek(parseInt(e.target.value))}
                  >
                    {DAYS_OF_WEEK.map((day, idx) => (
                      <option key={idx} value={idx}>{day}</option>
                    ))}
                  </select>
                </div>
              )}

              {(recurringFrequency === 'MONTHLY' || recurringFrequency === 'SEMI_MONTHLY') && (
                <div className="form-group">
                  <label htmlFor="recurring-dom">Day of Month</label>
                  <input
                    id="recurring-dom"
                    type="number"
                    min={1}
                    max={31}
                    value={recurringDayOfMonth}
                    onChange={(e) => setRecurringDayOfMonth(parseInt(e.target.value))}
                  />
                </div>
              )}
            </div>
          )}

          <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Add Expense'}
          </button>
        </form>
      </div>
    </div>
  );
}
