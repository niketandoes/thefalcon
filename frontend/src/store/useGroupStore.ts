import { create } from 'zustand';
import type { Group, AggregatedStats } from '../types';

interface GroupState {
  groups: Group[];
  activeGroup: Group | null;
  globalStats: AggregatedStats;
  setGroups: (groups: Group[]) => void;
  setActiveGroup: (group: Group | null) => void;
  addGroup: (group: Group) => void;
  setGlobalStats: (stats: AggregatedStats) => void;
}

const emptyStats: AggregatedStats = {
  total_to_pay: 0,
  total_owed_to_you: 0,
  debts_by_group: [],
};

export const useGroupStore = create<GroupState>((set) => ({
  groups: [],
  activeGroup: null,
  globalStats: emptyStats,
  setGroups: (groups) => set({ groups }),
  setActiveGroup: (group) => set({ activeGroup: group }),
  addGroup: (group) =>
    set((state) => ({ groups: [...state.groups, group] })),
  setGlobalStats: (stats) => set({ globalStats: stats }),
}));
