import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface Message {
  id: string;
  type: "message";
  content: string;
  role: "user" | "assistant";
}

export interface Function {
  id: string;
  type: "function";
  name: string;
  arguments: Record<string, any>;
}

export interface Agent {
  id: string;
  type: "agent";
  agentName: string;
  callId: string;
  name: "run" | "step" | "message";
  status: string;
  statusType?: string;
  content?: object;
}


export type Effort = Message | Function | Agent;


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