import Dexie from "dexie";

export interface WorkOrderRecord {
  id: string;
  code: string;
  title: string;
  equipmentId: string;
  equipment: string;
  priority: string;
  status: string;
  assignedTechnician: string;
  createdAt: string;
  dueDate: string;
  notes: string;
  spentMinutes: number;
  pausedMinutes: number;
  evidenceCount: number;
  parts: string[];
  updatedAt: string;
  offlineStatus: "pending" | "synced" | "failed";
}

export interface EquipmentRecord {
  id: string;
  code: string;
  name: string;
  plant: string;
  area: string;
  location: string;
  status: string;
  criticity: string;
  hourmeter: string;
  companyId: string;
  updatedAt: string;
}

export interface ChecklistRecord {
  id: string;
  workOrderId: string;
  label: string;
  completed: boolean;
  updatedAt: string;
  offlineStatus: "pending" | "synced" | "failed";
}

export interface AttachmentRecord {
  id: string;
  workOrderId: string;
  filename: string;
  url: string;
  type: string;
  createdAt: string;
  uploaded: boolean;
}

export interface EvidenceRecord {
  id: string;
  workOrderId: string;
  equipmentId: string;
  companyId: string;
  type: "BEFORE" | "AFTER" | "INSPECTION" | "FAILURE";
  fileName: string;
  mimeType: string;
  fileSize: number;
  localFile: Blob;
  status: "PENDING" | "UPLOADING" | "SYNCED" | "FAILED";
  createdAt: string;
  uploadedBy: string;
}

export interface SyncQueueRecord {
  id: string;
  action: "create" | "update" | "delete" | "upload";
  entity: "workOrder" | "checklist" | "equipment" | "attachment" | "evidence";
  entityId: string;
  payload: string;
  timestamp: string;
  status: "pending" | "processing" | "completed" | "failed";
  attempts: number;
}

const initialWorkOrders: WorkOrderRecord[] = [
  {
    id: "1",
    code: "OT-0021",
    title: "Revisión de prensa principal",
    equipmentId: "eq-0001",
    equipment: "Prensa Principal",
    priority: "High",
    status: "Assigned",
    assignedTechnician: "Carlos Mendoza",
    createdAt: "2026-06-03T08:20:00Z",
    dueDate: "2026-06-03T16:00:00Z",
    notes: "Revisar causa de vibración y operaciones seguras.",
    spentMinutes: 0,
    pausedMinutes: 0,
    evidenceCount: 0,
    parts: ["Sello hidráulico", "Filtro de aceite"],
    updatedAt: new Date().toISOString(),
    offlineStatus: "synced",
  },
  {
    id: "2",
    code: "OT-0035",
    title: "Cambio de filtro de aire",
    equipmentId: "eq-0002",
    equipment: "Extractor 4",
    priority: "Medium",
    status: "Pending",
    assignedTechnician: "Ana López",
    createdAt: "2026-06-02T14:12:00Z",
    dueDate: "2026-06-03T12:00:00Z",
    notes: "Cambio preventivo programado, cumplir con SOP.",
    spentMinutes: 0,
    pausedMinutes: 0,
    evidenceCount: 1,
    parts: ["Filtro de aire"],
    updatedAt: new Date().toISOString(),
    offlineStatus: "synced",
  },
];

const initialEquipment: EquipmentRecord[] = [
  {
    id: "eq-0001",
    code: "EQ-0001",
    name: "Prensa Principal",
    plant: "Planta Central",
    area: "Línea de prensado",
    location: "Sector A",
    status: "Operativo",
    criticity: "Alta",
    hourmeter: "12.500",
    companyId: "company-123",
    updatedAt: new Date().toISOString(),
  },
  {
    id: "eq-0002",
    code: "EQ-0002",
    name: "Extractor 4",
    plant: "Planta Central",
    area: "Área de extracción",
    location: "Sector B",
    status: "Operativo",
    criticity: "Media",
    hourmeter: "8.320",
    companyId: "company-123",
    updatedAt: new Date().toISOString(),
  },
];

const initialChecklist: ChecklistRecord[] = [
  { id: "c1", workOrderId: "1", label: "Desconectar energía principal", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "synced" },
  { id: "c2", workOrderId: "1", label: "Verificar presión hidráulica", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "synced" },
  { id: "c3", workOrderId: "1", label: "Inspeccionar mangueras", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "synced" },
  { id: "c4", workOrderId: "1", label: "Registrar hallazgos", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "synced" },
  { id: "c5", workOrderId: "2", label: "Retirar tapa del filtro", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "synced" },
  { id: "c6", workOrderId: "2", label: "Cambiar filtro nuevo", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "synced" },
  { id: "c7", workOrderId: "2", label: "Verificar sellos", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "synced" },
];

export class PalmCoreDB extends Dexie {
  workOrders!: Dexie.Table<WorkOrderRecord, string>;
  equipment!: Dexie.Table<EquipmentRecord, string>;
  checklists!: Dexie.Table<ChecklistRecord, string>;
  attachments!: Dexie.Table<AttachmentRecord, string>;
  evidences!: Dexie.Table<EvidenceRecord, string>;
  syncQueue!: Dexie.Table<SyncQueueRecord, string>;

  constructor() {
    super("PalmCoreDB");

    this.version(1).stores({
      workOrders: "id, code, equipment, status, priority, assignedTechnician, updatedAt, offlineStatus",
      equipment: "id, name, location, status, updatedAt",
      checklists: "id, workOrderId, completed, updatedAt, offlineStatus",
      attachments: "id, workOrderId, uploaded, createdAt",
      syncQueue: "id, action, entity, entityId, status, timestamp",
    });

    this.version(2).stores({
      workOrders: "id, code, equipmentId, equipment, status, priority, assignedTechnician, updatedAt, offlineStatus",
      equipment: "id, code, name, plant, area, location, status, criticity, companyId, updatedAt",
      checklists: "id, workOrderId, completed, updatedAt, offlineStatus",
      attachments: "id, workOrderId, uploaded, createdAt",
      evidences: "id, workOrderId, equipmentId, companyId, type, status, createdAt",
      syncQueue: "id, action, entity, entityId, status, timestamp",
    });
  }

  async seedInitialData() {
    const workOrderCount = await this.workOrders.count();
    const equipmentCount = await this.equipment.count();
    if (workOrderCount === 0) {
      await this.workOrders.bulkPut(initialWorkOrders);
      await this.checklists.bulkPut(initialChecklist);
    }
    if (equipmentCount === 0) {
      await this.equipment.bulkPut(initialEquipment);
    }
  }
}

export const db = new PalmCoreDB();
