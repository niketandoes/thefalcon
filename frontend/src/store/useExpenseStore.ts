import { create } from 'zustand';
import { apiClient } from '../api/client';
import type { Expense, DashboardStats, ExpensePayload } from '../types';

interface ExpenseState {
  expenses: Expense[];
  stats: DashboardStats | null;
  isLoading: boolean;
  error: string | null;

  fetchExpenses: (groupId?: string) => Promise<void>;
  fetchStats: (groupId?: string) => Promise<void>;
  createExpense: (payload: ExpensePayload) => Promise<void>;
  clearError: () => void;
}

export const useExpenseStore = create<ExpenseState>((set) => ({
  expenses: [],
  stats: null,
  isLoading: false,
  error: null,

  fetchExpenses: async (groupId) => {
    set({ isLoading: true });
    try {
      const params = groupId ? { group_id: groupId } : {};
      const { data } = await apiClient.get('/expenses/', { params });
      set({ expenses: data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  fetchStats: async (groupId) => {
    set({ isLoading: true });
    try {
      const url = groupId
        ? `/expenses/dashboard/stats/group/${groupId}`
        : '/expenses/dashboard/stats';
      const { data } = await apiClient.get(url);
      set({ stats: data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  createExpense: async (payload) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post('/expenses/', payload);
      set({ isLoading: false });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to create expense';
      set({ error: msg, isLoading: false });
      throw new Error(msg);
    }
  },

  clearError: () => set({ error: null }),
}));
