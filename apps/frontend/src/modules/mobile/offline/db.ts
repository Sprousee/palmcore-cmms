import Dexie from "dexie";

export interface OfflineWorkOrder {
  id: string;
  companyId: string;
  equipmentId: string;
  status: string;
  title: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  offlineStatus: "pending" | "synced" | "failed";
}

export interface OfflineSyncTask {
  id: string;
  type: "work-order" | "checklist" | "evidence";
  payload: string;
  createdAt: string;
  status: "pending" | "in_progress" | "completed" | "failed";
}

export class PalmCoreOfflineDB extends Dexie {
  workOrders!: Dexie.Table<OfflineWorkOrder, string>;
  syncQueue!: Dexie.Table<OfflineSyncTask, string>;

  constructor() {
    super("PalmCoreOfflineDB");
    this.version(1).stores({
      workOrders: "id, companyId, equipmentId, status, offlineStatus, createdAt, updatedAt",
      syncQueue: "id, type, status, createdAt",
    });
  }
}

export const db = new PalmCoreOfflineDB();
