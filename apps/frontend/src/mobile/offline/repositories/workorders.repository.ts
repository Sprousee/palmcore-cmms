import { db, EquipmentRecord, WorkOrderRecord, ChecklistRecord } from "../db/palmcore-db";
import { addSyncTask } from "../sync/queue-manager";

export interface MobileWorkOrderEntity extends WorkOrderRecord {
  checklist: ChecklistRecord[];
}

export async function getAllWorkOrders(): Promise<MobileWorkOrderEntity[]> {
  await db.seedInitialData();
  const workOrders = await db.workOrders.toArray();
  return Promise.all(
    workOrders.map(async (order) => ({
      ...order,
      checklist: await db.checklists.where("workOrderId").equals(order.id).toArray(),
    })),
  );
}

export async function getWorkOrderById(id: string): Promise<MobileWorkOrderEntity | undefined> {
  const order = await db.workOrders.get(id);
  if (!order) return undefined;
  const checklist = await db.checklists.where("workOrderId").equals(id).toArray();
  return { ...order, checklist };
}

export async function saveWorkOrder(order: MobileWorkOrderEntity) {
  await db.workOrders.put({
    ...order,
    updatedAt: new Date().toISOString(),
    offlineStatus: "pending",
  });
  await addSyncTask({
    action: "update",
    entity: "workOrder",
    entityId: order.id,
    payload: JSON.stringify(order),
  });
}

export async function updateWorkOrderStatus(id: string, status: string) {
  const order = await db.workOrders.get(id);
  if (!order) return;
  await db.workOrders.update(id, {
    status,
    updatedAt: new Date().toISOString(),
    offlineStatus: "pending",
  });
  await addSyncTask({
    action: "update",
    entity: "workOrder",
    entityId: id,
    payload: JSON.stringify({ status, updatedAt: new Date().toISOString() }),
  });
}

export async function toggleChecklistItem(workOrderId: string, itemId: string) {
  const checklistItem = await db.checklists.get(itemId);
  if (!checklistItem) return;

  await db.checklists.update(itemId, {
    completed: !checklistItem.completed,
    updatedAt: new Date().toISOString(),
    offlineStatus: "pending",
  });

  await addSyncTask({
    action: "update",
    entity: "checklist",
    entityId: itemId,
    payload: JSON.stringify({ workOrderId, completed: !checklistItem.completed, updatedAt: new Date().toISOString() }),
  });
}

export async function saveChecklistItems(items: ChecklistRecord[]) {
  await db.checklists.bulkPut(items.map((item) => ({
    ...item,
    updatedAt: new Date().toISOString(),
    offlineStatus: "pending",
  })));
  for (const item of items) {
    await addSyncTask({
      action: "update",
      entity: "checklist",
      entityId: item.id,
      payload: JSON.stringify(item),
    });
  }
}

export async function createWorkOrderForEquipment(equipment: EquipmentRecord): Promise<MobileWorkOrderEntity> {
  const id = typeof crypto !== "undefined" && typeof crypto.randomUUID === "function" ? crypto.randomUUID() : `ot-${Date.now()}`;
  const newOrder: MobileWorkOrderEntity = {
    id,
    code: `OT-${Math.floor(1000 + Math.random() * 9000)}`,
    title: `Mantenimiento desde QR - ${equipment.name}`,
    equipmentId: equipment.id,
    equipment: equipment.name,
    priority: "Medium",
    status: "Pending",
    assignedTechnician: "Técnico de planta",
    createdAt: new Date().toISOString(),
    dueDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    notes: `Orden creada desde QR para ${equipment.name}.`,
    spentMinutes: 0,
    pausedMinutes: 0,
    evidenceCount: 0,
    parts: ["Repuesto estándar"],
    updatedAt: new Date().toISOString(),
    offlineStatus: "pending",
    checklist: [
      { id: `${id}-c1`, workOrderId: id, label: "Inspeccionar visualmente", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "pending" },
      { id: `${id}-c2`, workOrderId: id, label: "Revisar condición del equipo", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "pending" },
      { id: `${id}-c3`, workOrderId: id, label: "Registrar hallazgos", completed: false, updatedAt: new Date().toISOString(), offlineStatus: "pending" },
    ],
  };

  await db.workOrders.put(newOrder);
  await db.checklists.bulkPut(newOrder.checklist);

  await addSyncTask({
    action: "create",
    entity: "workOrder",
    entityId: newOrder.id,
    payload: JSON.stringify(newOrder),
  });

  return newOrder;
}
