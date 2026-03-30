import { create } from 'zustand';
import { apiClient } from '../api/client';
import type { User } from '../types';

interface AuthState {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, currency: string) => Promise<void>;
  fetchMe: () => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: null,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const form = new URLSearchParams();
      form.append('username', email);
      form.append('password', password);
      const { data } = await apiClient.post('/login/access-token', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      localStorage.setItem('token', data.access_token);
      set({ token: data.access_token, isLoading: false });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Login failed';
      set({ error: msg, isLoading: false });
      throw new Error(msg);
    }
  },

  register: async (name, email, password, currency) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post('/register', {
        full_name: name,
        email,
        password,
        preferred_currency: currency,
      });
      set({ isLoading: false });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Registration failed';
      set({ error: msg, isLoading: false });
      throw new Error(msg);
    }
  },

  fetchMe: async () => {
    try {
      const { data } = await apiClient.get('/users/me');
      set({ user: data });
    } catch {
      set({ token: null, user: null });
      localStorage.removeItem('token');
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null });
  },

  clearError: () => set({ error: null }),
}));
