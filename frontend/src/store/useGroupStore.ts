import { create } from 'zustand';

interface Group {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

interface GroupState {
  groups: Group[];
  activeGroup: Group | null;
  setGroups: (groups: Group[]) => void;
  setActiveGroup: (group: Group | null) => void;
  addGroup: (group: Group) => void;
}

export const useGroupStore = create<GroupState>((set) => ({
  groups: [],
  activeGroup: null,
  setGroups: (groups) => set({ groups }),
  setActiveGroup: (group) => set({ activeGroup: group }),
  addGroup: (group) => set((state) => ({ groups: [...state.groups, group] })),
}));
