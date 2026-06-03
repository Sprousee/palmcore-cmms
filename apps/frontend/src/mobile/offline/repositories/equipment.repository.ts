import { db, EquipmentRecord, WorkOrderRecord } from "../db/palmcore-db";

export async function getAllEquipment(): Promise<EquipmentRecord[]> {
  return await db.equipment.toArray();
}

export async function getEquipmentById(id: string): Promise<EquipmentRecord | undefined> {
  return await db.equipment.get(id);
}

export async function getEquipmentHistoryById(id: string): Promise<WorkOrderRecord[]> {
  const workOrders = await db.workOrders.where("equipmentId").equals(id).toArray();
  return workOrders.sort((a, b) => (a.createdAt > b.createdAt ? -1 : 1));
}

export async function saveEquipment(items: EquipmentRecord[]) {
  await db.equipment.bulkPut(items.map((item) => ({
    ...item,
    updatedAt: new Date().toISOString(),
  })));
}
