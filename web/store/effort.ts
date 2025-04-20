import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface Effort {
  id: string;
  source: string;
  type: "message" | "function" | "agent";
  content: string;
}

export interface EffortStore {
  efforts: Effort[];
  addEffort: (effort: Effort) => void;
  removeEffort: (index: number) => void;
  clearEfforts: () => void;
}

export const useEffortStore = create<EffortStore>()(
  persist(
    (set) => ({
      efforts: [],
      addEffort: (effort) =>
        set((state) => ({ efforts: [...state.efforts, effort] })),
      removeEffort: (index) =>
        set((state) => ({
          efforts: state.efforts.filter((_, i) => i !== index),
        })),
      clearEfforts: () => set({ efforts: [] }),
    }),
    {
      name: "effort-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);