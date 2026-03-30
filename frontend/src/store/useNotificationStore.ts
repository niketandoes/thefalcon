import { create } from 'zustand';
import { apiClient } from '../api/client';
import type { Notification } from '../types';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;

  fetchNotifications: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  respondToInvite: (groupId: string, action: 'accept' | 'reject') => Promise<void>;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,

  fetchNotifications: async () => {
    set({ isLoading: true });
    try {
      const { data } = await apiClient.get('/notifications/', {
        params: { limit: 50 },
      });
      set({
        notifications: data.items,
        unreadCount: data.unread_count,
        isLoading: false,
      });
    } catch {
      set({ isLoading: false });
    }
  },

  markAsRead: async (id) => {
    try {
      await apiClient.patch(`/notifications/${id}/read`);
      const updated = get().notifications.map((n) =>
        n.id === id ? { ...n, is_read: true } : n
      );
      const unread = updated.filter((n) => !n.is_read).length;
      set({ notifications: updated, unreadCount: unread });
    } catch { /* silent */ }
  },

  respondToInvite: async (groupId, action) => {
    try {
      await apiClient.post(`/notifications/invites/${groupId}/respond`, { action });
      // Refresh notifications
      await get().fetchNotifications();
    } catch (err: any) {
      throw new Error(err?.response?.data?.detail || 'Failed');
    }
  },
}));
