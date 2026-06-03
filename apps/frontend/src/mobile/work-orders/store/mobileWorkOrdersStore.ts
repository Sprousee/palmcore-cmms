import { create } from "zustand";

export type WorkOrderStatus = "Pending" | "Assigned" | "In Progress" | "Paused" | "Completed";
export type WorkOrderPriority = "Low" | "Medium" | "High" | "Critical";

export interface ChecklistItem {
  id: string;
  label: string;
  completed: boolean;
}

export interface MobileWorkOrder {
  id: string;
  code: string;
  title: string;
  equipment: string;
  priority: WorkOrderPriority;
  status: WorkOrderStatus;
  assignedTechnician: string;
  createdAt: string;
  dueDate: string;
  notes: string;
  checklist: ChecklistItem[];
  spentMinutes: number;
  pausedMinutes: number;
  parts: string[];
  evidenceCount: number;
}

interface MobileWorkOrdersState {
  workOrders: MobileWorkOrder[];
  offlineState: boolean;
  selectedOrderId: string | null;
  loadWorkOrders: (orders: MobileWorkOrder[]) => void;
  setOfflineState: (value: boolean) => void;
  setSelectedOrderId: (id: string | null) => void;
  updateWorkOrderStatus: (id: string, nextStatus: WorkOrderStatus) => void;
  toggleChecklistItem: (orderId: string, itemId: string) => void;
  updateOrderTimes: (id: string, minutes: number) => void;
}

const initialOrders: MobileWorkOrder[] = [
  {
    id: "1",
    code: "OT-0021",
    title: "Revisión de prensa principal",
    equipment: "Prensa Principal",
    priority: "High",
    status: "Assigned",
    assignedTechnician: "Carlos Mendoza",
    createdAt: "2026-06-03T08:20:00Z",
    dueDate: "2026-06-03T16:00:00Z",
    notes: "Revisar causa de vibración y operaciones seguras.",
    checklist: [
      { id: "c1", label: "Desconectar energía principal", completed: false },
      { id: "c2", label: "Verificar presión hidráulica", completed: false },
      { id: "c3", label: "Inspeccionar mangueras", completed: false },
      { id: "c4", label: "Registrar hallazgos", completed: false },
    ],
    spentMinutes: 0,
    pausedMinutes: 0,
    parts: ["Sello hidráulico", "Filtro de aceite"],
    evidenceCount: 0,
  },
  {
    id: "2",
    code: "OT-0035",
    title: "Cambio de filtro de aire",
    equipment: "Extractor 4",
    priority: "Medium",
    status: "Pending",
    assignedTechnician: "Ana López",
    createdAt: "2026-06-02T14:12:00Z",
    dueDate: "2026-06-03T12:00:00Z",
    notes: "Cambio preventivo programado, cumplir con SOP.",
    checklist: [
      { id: "c5", label: "Retirar tapa del filtro", completed: false },
      { id: "c6", label: "Cambiar filtro nuevo", completed: false },
      { id: "c7", label: "Verificar sellos", completed: false },
    ],
    spentMinutes: 0,
    pausedMinutes: 0,
    parts: ["Filtro de aire"],
    evidenceCount: 1,
  },
];

export const useMobileWorkOrdersStore = create<MobileWorkOrdersState>((set) => ({
  workOrders: initialOrders,
  offlineState: false,
  selectedOrderId: null,
  loadWorkOrders: (orders) => set({ workOrders: orders }),
  setOfflineState: (value) => set({ offlineState: value }),
  setSelectedOrderId: (id) => set({ selectedOrderId: id }),
  updateWorkOrderStatus: (id, nextStatus) =>
    set((state) => ({
      workOrders: state.workOrders.map((order) =>
        order.id === id ? { ...order, status: nextStatus } : order,
      ),
    })),
  toggleChecklistItem: (orderId, itemId) =>
    set((state) => ({
      workOrders: state.workOrders.map((order) =>
        order.id === orderId
          ? {
              ...order,
              checklist: order.checklist.map((item) =>
                item.id === itemId ? { ...item, completed: !item.completed } : item,
              ),
            }
          : order,
      ),
    })),
  updateOrderTimes: (id, minutes) =>
    set((state) => ({
      workOrders: state.workOrders.map((order) =>
        order.id === id ? { ...order, spentMinutes: order.spentMinutes + minutes } : order,
      ),
    })),
}));
