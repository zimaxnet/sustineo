import { create } from 'zustand'
import {
  type Node,
  type Edge,
} from '@xyflow/react';
import { persist, createJSONStorage } from "zustand/middleware";

interface WorkState {
  nodes: Node[]
  edges: Edge[]
  addWork: (node: Node) => void
  addConnection: (edge: Edge) => void
}

const useWorkStore = create<WorkState>()(
  persist((set) => ({
    nodes: [
      { id: "1", position: { x: 0, y: 0 }, data: { label: "1" } },
      { id: "2", position: { x: 0, y: 100 }, data: { label: "2" } },
    ],
    edges: [{ id: "e1-2", source: "1", target: "2" }],
    addWork: (node) => set((state) => ({ nodes: [...state.nodes, node] })),
    addConnection: (edge) => set((state) => ({ edges: [...state.edges, edge] })),
  }),
    {
      name: "work-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);