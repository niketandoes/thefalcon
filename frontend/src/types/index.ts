// ─── Shared type definitions ────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  preferred_currency?: string;
}

export interface Group {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  members?: GroupMember[];
}

export interface GroupMember {
  user_id: string;
  full_name: string;
  email: string;
  preferred_currency: string;
  balance: number; // positive = they owe you, negative = you owe them
}

export type SplitType = 'EQUAL' | 'PERCENTAGE' | 'SHARE' | 'ITEM';

export type RecurringFrequency = 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY' | 'SEMI_MONTHLY';

export interface SplitEntry {
  user_id: string;
  user_name?: string;
  percentage?: number;
  share?: number;
  amount_owed?: number;
}

export interface ExpensePayload {
  description: string;
  amount: number;
  currency: string;
  group_id: string;
  split_type: SplitType;
  date: string;
  splits: SplitEntry[];
  is_recurring: boolean;
  recurring_frequency?: RecurringFrequency;
  recurring_day_of_week?: number; // 0-6, Sun-Sat
  recurring_day_of_month?: number; // 1-31
}

export interface DebtSummary {
  from_user_id: string;
  from_user_name?: string;
  to_user_id: string;
  to_user_name?: string;
  amount: number;
}

export interface AggregatedStats {
  total_to_pay: number;
  total_owed_to_you: number;
  debts_by_group: GroupDebt[];
}

export interface GroupDebt {
  group_id: string;
  group_name: string;
  you_owe: number;
  you_are_owed: number;
}
