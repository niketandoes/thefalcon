// ─── Shared type definitions ────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  preferred_currency: string;
  is_active: boolean;
}

export interface Group {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  members?: GroupMember[];
}

export type MemberStatus = 'PENDING' | 'ACCEPTED' | 'REJECTED';

export interface GroupMember {
  user_id: string;
  full_name: string | null;
  email: string;
  preferred_currency: string;
  status: MemberStatus;
}

export type SplitType = 'EQUAL' | 'PERCENTAGE' | 'SHARE' | 'ITEM';

export type RecurringFrequency = 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY' | 'SEMI_MONTHLY';

export interface SplitEntry {
  user_id: string;
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
  expense_date: string;
  payer_id?: string;
  splits: SplitEntry[];
  is_recurring: boolean;
  recurring_frequency?: RecurringFrequency;
  recurring_day_of_week?: number;
  recurring_day_of_month?: number;
}

export interface SplitResponse {
  id: string;
  expense_id: string;
  user_id: string;
  amount_owed: number;
  percentage?: number;
  share?: number;
}

export interface Expense {
  id: string;
  description: string;
  amount: number;
  currency: string;
  split_type: SplitType;
  group_id: string;
  expense_date: string;
  payer_id: string;
  is_recurring: boolean;
  recurring_frequency?: RecurringFrequency;
  recurring_day_of_week?: number;
  recurring_day_of_month?: number;
  created_at: string;
  splits: SplitResponse[];
}

export interface DebtSummary {
  from_user_id: string;
  to_user_id: string;
  amount: number;
}

export interface GroupDebt {
  group_id: string;
  group_name: string;
  you_owe: number;
  you_are_owed: number;
}

export interface DashboardStats {
  total_to_pay: number;
  total_owed_to_you: number;
  net_balance: number;
  debts_by_group: GroupDebt[];
}

export type NotificationType = 'GROUP_INVITE' | 'EXPENSE_ADDED' | 'PAYMENT_RECEIVED' | 'PAYMENT_REMINDER';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  group_id?: string;
  expense_id?: string;
  created_at: string;
}

export interface NotificationList {
  total: number;
  unread_count: number;
  items: Notification[];
}

export interface GroupDetail extends Group {
  members: GroupMember[];
}
