import { db, SyncQueueRecord } from "../db/palmcore-db";

export interface SyncTaskPayload {
  id: string;
  action: SyncQueueRecord["action"];
  entity: SyncQueueRecord["entity"];
  entityId: string;
  payload: string;
  timestamp?: string;
}

export async function addSyncTask(task: Omit<SyncTaskPayload, "id" | "timestamp">) {
  const record: SyncQueueRecord = {
    id: crypto.randomUUID(),
    action: task.action,
    entity: task.entity,
    entityId: task.entityId,
    payload: task.payload,
    timestamp: task.timestamp ?? new Date().toISOString(),
    status: "pending",
    attempts: 0,
  };
  await db.syncQueue.put(record);
  return record;
}

export async function getPendingSyncTasks() {
  return await db.syncQueue.where("status").equals("pending").toArray();
}

export async function markTaskProcessing(id: string) {
  const task = await db.syncQueue.get(id);
  const attempts = (task?.attempts ?? 0) + 1;
  await db.syncQueue.update(id, { status: "processing", attempts });
}

export async function markTaskCompleted(id: string) {
  await db.syncQueue.update(id, { status: "completed" });
}

export async function markTaskFailed(id: string) {
  await db.syncQueue.update(id, { status: "failed" });
}

export async function getSyncStatusCounts() {
  const pending = await db.syncQueue.where("status").equals("pending").count();
  const failed = await db.syncQueue.where("status").equals("failed").count();
  return { pending, failed };
}
