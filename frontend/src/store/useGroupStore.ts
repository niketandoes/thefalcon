import { create } from 'zustand';
import { apiClient } from '../api/client';
import type { Group, GroupDetail, DebtSummary } from '../types';

interface GroupState {
  groups: Group[];
  currentGroup: GroupDetail | null;
  balances: DebtSummary[];
  isLoading: boolean;
  error: string | null;

  fetchGroups: () => Promise<void>;
  fetchGroupDetail: (id: string) => Promise<void>;
  createGroup: (name: string, description?: string) => Promise<void>;
  inviteMember: (groupId: string, email: string) => Promise<void>;
  addMember: (groupId: string, email: string) => Promise<void>;
  leaveGroup: (groupId: string) => Promise<void>;
  fetchBalances: (groupId: string) => Promise<void>;
  clearError: () => void;
}

export const useGroupStore = create<GroupState>((set) => ({
  groups: [],
  currentGroup: null,
  balances: [],
  isLoading: false,
  error: null,

  fetchGroups: async () => {
    set({ isLoading: true });
    try {
      const { data } = await apiClient.get('/groups/');
      set({ groups: data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  fetchGroupDetail: async (id) => {
    set({ isLoading: true });
    try {
      const { data } = await apiClient.get(`/groups/${id}`);
      set({ currentGroup: data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  createGroup: async (name, description) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post('/groups/', { name, description });
      const { data } = await apiClient.get('/groups/');
      set({ groups: data, isLoading: false });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to create group';
      set({ error: msg, isLoading: false });
    }
  },

  inviteMember: async (groupId, email) => {
    try {
      await apiClient.post(`/groups/${groupId}/invite`, { email });
    } catch (err: any) {
      throw new Error(err?.response?.data?.detail || 'Failed to invite');
    }
  },

  addMember: async (groupId, email) => {
    try {
      await apiClient.post(`/groups/${groupId}/members`, { email });
    } catch (err: any) {
      throw new Error(err?.response?.data?.detail || 'Failed to add member');
    }
  },

  leaveGroup: async (groupId) => {
    try {
      await apiClient.delete(`/groups/${groupId}/leave`);
    } catch (err: any) {
      throw new Error(err?.response?.data?.detail || 'Failed to leave group');
    }
  },

  fetchBalances: async (groupId) => {
    try {
      const { data } = await apiClient.get(`/groups/${groupId}/balances`);
      set({ balances: data });
    } catch {
      set({ balances: [] });
    }
  },

  clearError: () => set({ error: null }),
}));
