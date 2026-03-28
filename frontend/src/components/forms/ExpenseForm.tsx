import { useState, useEffect, useMemo } from 'react';
import { Calendar, Repeat, DollarSign, Hash, Percent, LayoutList } from 'lucide-react';
import Input from '../common/Input';
import Select from '../common/Select';
import Button from '../common/Button';
import type { SplitType, RecurringFrequency, SplitEntry, Group, GroupMember } from '../../types';
import { useAuthStore } from '../../store/useAuthStore';

interface ExpenseFormProps {
  groups: Group[];
  preSelectedGroupId?: string;
  onSubmit: (data: ExpenseFormData) => void;
  onCancel: () => void;
}

export interface ExpenseFormData {
  description: string;
  amount: number;
  currency: string;
  group_id: string;
  payer_id: string;
  date: string;
  split_type: SplitType;
  splits: SplitEntry[];
  is_recurring: boolean;
  recurring_frequency?: RecurringFrequency;
  recurring_day_of_week?: number;
  recurring_day_of_month?: number;
}

// ─── Mock members per group (replace with API later) ─────────────────────
const MOCK_MEMBERS: Record<string, GroupMember[]> = {
  '1': [
    { user_id: '1', full_name: 'Demo User', email: 'demo@splititfair.com', preferred_currency: 'USD', balance: 0 },
    { user_id: '2', full_name: 'Alice', email: 'alice@test.com', preferred_currency: 'USD', balance: 0 },
    { user_id: '3', full_name: 'Bob', email: 'bob@test.com', preferred_currency: 'USD', balance: 0 },
  ],
  '2': [
    { user_id: '1', full_name: 'Demo User', email: 'demo@splititfair.com', preferred_currency: 'USD', balance: 0 },
    { user_id: '4', full_name: 'Charlie', email: 'charlie@test.com', preferred_currency: 'EUR', balance: 0 },
    { user_id: '5', full_name: 'Diana', email: 'diana@test.com', preferred_currency: 'GBP', balance: 0 },
  ],
};

const CURRENCIES = ['USD', 'EUR', 'GBP', 'INR', 'JPY', 'CAD', 'AUD'];
const DAYS_OF_WEEK = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

const SPLIT_ICONS: Record<SplitType, React.ReactNode> = {
  EQUAL: <Hash size={16} />,
  PERCENTAGE: <Percent size={16} />,
  SHARE: <LayoutList size={16} />,
  ITEM: <DollarSign size={16} />,
};

export default function ExpenseForm({ groups, preSelectedGroupId, onSubmit, onCancel }: ExpenseFormProps) {
  const user = useAuthStore((s) => s.user);
  const today = new Date();

  // ─── Core form state ──────────────────────────────────────────────────
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [groupId, setGroupId] = useState(preSelectedGroupId || groups[0]?.id || '');
  const [payerId, setPayerId] = useState(user?.id || '');
  const [date, setDate] = useState(today.toISOString().split('T')[0]);
  const [splitType, setSplitType] = useState<SplitType>('EQUAL');

  // ─── Recurring state ──────────────────────────────────────────────────
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurringFrequency, setRecurringFrequency] = useState<RecurringFrequency>('MONTHLY');
  const [recurringDayOfWeek, setRecurringDayOfWeek] = useState(today.getDay());
  const [recurringDayOfMonth, setRecurringDayOfMonth] = useState(today.getDate());

  // ─── Split entries (one per member in the selected group) ─────────────
  const members = useMemo(() => MOCK_MEMBERS[groupId] || [], [groupId]);
  const [splits, setSplits] = useState<SplitEntry[]>([]);

  // Re-init splits when group or split type changes
  useEffect(() => {
    const initial: SplitEntry[] = members.map((m) => ({
      user_id: m.user_id,
      user_name: m.full_name,
      percentage: splitType === 'PERCENTAGE' ? parseFloat((100 / members.length).toFixed(2)) : undefined,
      share: splitType === 'SHARE' ? 1 : undefined,
      amount_owed: splitType === 'ITEM' ? 0 : undefined,
    }));
    setSplits(initial);
  }, [groupId, splitType, members]);

  // ─── Validation ───────────────────────────────────────────────────────
  const percentageSum = splits.reduce((sum, s) => sum + (s.percentage || 0), 0);
  const exactSum = splits.reduce((sum, s) => sum + (s.amount_owed || 0), 0);

  const isValid =
    description.trim().length > 0 &&
    parseFloat(amount) > 0 &&
    groupId &&
    (splitType !== 'PERCENTAGE' || Math.abs(percentageSum - 100) < 0.01) &&
    (splitType !== 'ITEM' || Math.abs(exactSum - parseFloat(amount || '0')) < 0.01);

  // ─── Handlers ─────────────────────────────────────────────────────────
  const updateSplit = (idx: number, field: keyof SplitEntry, value: number) => {
    setSplits((prev) => prev.map((s, i) => (i === idx ? { ...s, [field]: value } : s)));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;
    onSubmit({
      description,
      amount: parseFloat(amount),
      currency,
      group_id: groupId,
      payer_id: payerId,
      date,
      split_type: splitType,
      splits,
      is_recurring: isRecurring,
      recurring_frequency: isRecurring ? recurringFrequency : undefined,
      recurring_day_of_week: isRecurring && recurringFrequency === 'WEEKLY' ? recurringDayOfWeek : undefined,
      recurring_day_of_month: isRecurring && recurringFrequency === 'MONTHLY' ? recurringDayOfMonth : undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Row 1: Title + Amount + Currency */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="sm:col-span-1">
          <Input
            id="expense-title"
            label="Title"
            placeholder="Dinner, Uber, Groceries..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div>
          <Input
            id="expense-amount"
            label="Total Amount"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
            icon={<DollarSign size={16} />}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </div>
        <div>
          <Select
            id="expense-currency"
            label="Currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            options={CURRENCIES.map((c) => ({ value: c, label: c }))}
          />
        </div>
      </div>

      {/* Row 2: Group + Payer + Date */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Select
          id="expense-group"
          label="Group"
          value={groupId}
          onChange={(e) => setGroupId(e.target.value)}
          options={groups.map((g) => ({ value: g.id, label: g.name }))}
        />
        <Select
          id="expense-payer"
          label="Paid By"
          value={payerId}
          onChange={(e) => setPayerId(e.target.value)}
          options={members.map((m) => ({ value: m.user_id, label: m.full_name }))}
        />
        <Input
          id="expense-date"
          label="Date"
          type="date"
          icon={<Calendar size={16} />}
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
      </div>

      {/* ─── Split Method Selector ─────────────────────────────────────── */}
      <div>
        <p className="text-sm font-medium text-slate-300 mb-2">Split Method</p>
        <div className="grid grid-cols-4 gap-2">
          {(['EQUAL', 'PERCENTAGE', 'SHARE', 'ITEM'] as SplitType[]).map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => setSplitType(type)}
              className={`flex flex-col items-center gap-1 px-3 py-3 rounded-xl border text-sm font-medium transition-all
                ${
                  splitType === type
                    ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300'
                    : 'bg-slate-800/40 border-white/5 text-slate-400 hover:border-white/10 hover:text-white'
                }`}
            >
              {SPLIT_ICONS[type]}
              <span className="capitalize">{type.toLowerCase()}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ─── Split Entries ─────────────────────────────────────────────── */}
      {splits.length > 0 && splitType !== 'EQUAL' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-slate-300">Split Details</p>
            {splitType === 'PERCENTAGE' && (
              <span className={`text-xs font-mono px-2 py-1 rounded-md ${Math.abs(percentageSum - 100) < 0.01 ? 'text-emerald-400 bg-emerald-400/10' : 'text-rose-400 bg-rose-400/10'}`}>
                {percentageSum.toFixed(1)}% / 100%
              </span>
            )}
            {splitType === 'ITEM' && (
              <span className={`text-xs font-mono px-2 py-1 rounded-md ${Math.abs(exactSum - parseFloat(amount || '0')) < 0.01 ? 'text-emerald-400 bg-emerald-400/10' : 'text-rose-400 bg-rose-400/10'}`}>
                {currency} {exactSum.toFixed(2)} / {parseFloat(amount || '0').toFixed(2)}
              </span>
            )}
          </div>
          {splits.map((split, idx) => (
            <div key={split.user_id} className="flex items-center gap-3 bg-slate-800/30 border border-white/5 p-3 rounded-xl">
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-xs font-bold text-indigo-300">
                {(split.user_name || '?')[0]}
              </div>
              <span className="text-sm text-slate-300 min-w-[80px]">{split.user_name}</span>
              <div className="flex-1">
                {splitType === 'PERCENTAGE' && (
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={split.percentage ?? ''}
                    onChange={(e) => updateSplit(idx, 'percentage', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
                    placeholder="%"
                  />
                )}
                {splitType === 'SHARE' && (
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={split.share ?? ''}
                    onChange={(e) => updateSplit(idx, 'share', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
                    placeholder="Shares"
                  />
                )}
                {splitType === 'ITEM' && (
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={split.amount_owed ?? ''}
                    onChange={(e) => updateSplit(idx, 'amount_owed', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
                    placeholder="Exact amount"
                  />
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {splitType === 'EQUAL' && splits.length > 0 && parseFloat(amount) > 0 && (
        <div className="bg-slate-800/30 border border-white/5 rounded-xl p-4">
          <p className="text-sm text-slate-400 mb-2">Equal split preview</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {splits.map((s) => (
              <div key={s.user_id} className="flex items-center gap-2 text-sm">
                <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-xs font-bold text-indigo-300">
                  {(s.user_name || '?')[0]}
                </div>
                <span className="text-slate-300">{s.user_name}</span>
                <span className="ml-auto font-mono text-emerald-400">
                  {currency} {(parseFloat(amount) / splits.length).toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Recurring Toggle ──────────────────────────────────────────── */}
      <div className="border-t border-white/5 pt-5">
        <div className="flex items-center gap-3 mb-4">
          <button
            type="button"
            onClick={() => setIsRecurring(!isRecurring)}
            className={`relative w-11 h-6 rounded-full transition-colors ${isRecurring ? 'bg-indigo-600' : 'bg-slate-700'}`}
          >
            <span
              className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform
                ${isRecurring ? 'translate-x-5' : 'translate-x-0'}`}
            />
          </button>
          <label className="flex items-center gap-2 text-sm font-medium text-slate-300 cursor-pointer" onClick={() => setIsRecurring(!isRecurring)}>
            <Repeat size={16} className={isRecurring ? 'text-indigo-400' : 'text-slate-500'} />
            Recurring Expense
          </label>
        </div>

        {isRecurring && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-800/20 border border-white/5 rounded-xl p-4">
            <Select
              id="recurring-frequency"
              label="Frequency"
              value={recurringFrequency}
              onChange={(e) => setRecurringFrequency(e.target.value as RecurringFrequency)}
              options={[
                { value: 'DAILY', label: 'Daily' },
                { value: 'WEEKLY', label: 'Weekly' },
                { value: 'MONTHLY', label: 'Monthly' },
                { value: 'YEARLY', label: 'Yearly' },
                { value: 'SEMI_MONTHLY', label: 'Semi-monthly (1st & 15th)' },
              ]}
            />

            {recurringFrequency === 'WEEKLY' && (
              <Select
                id="recurring-day"
                label="Day of Week"
                value={String(recurringDayOfWeek)}
                onChange={(e) => setRecurringDayOfWeek(parseInt(e.target.value))}
                options={DAYS_OF_WEEK.map((d, i) => ({ value: String(i), label: d }))}
              />
            )}

            {recurringFrequency === 'MONTHLY' && (
              <Input
                id="recurring-date"
                label="Day of Month"
                type="number"
                min="1"
                max="31"
                value={recurringDayOfMonth}
                onChange={(e) => setRecurringDayOfMonth(parseInt(e.target.value) || 1)}
              />
            )}
          </div>
        )}
      </div>

      {/* ─── Actions ───────────────────────────────────────────────────── */}
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="ghost" type="button" onClick={onCancel}>Cancel</Button>
        <Button variant="primary" type="submit" disabled={!isValid} icon={<DollarSign size={16} />}>
          Add Expense
        </Button>
      </div>
    </form>
  );
}
