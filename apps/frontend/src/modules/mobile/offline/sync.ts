import { db, OfflineSyncTask } from "./db";

export async function enqueueSyncTask(task: OfflineSyncTask) {
  await db.syncQueue.put(task);
}

export async function getPendingSyncTasks() {
  return await db.syncQueue.where("status").equals("pending").toArray();
}

export async function markSyncTaskCompleted(id: string) {
  await db.syncQueue.update(id, { status: "completed" });
}

export async function markSyncTaskFailed(id: string) {
  await db.syncQueue.update(id, { status: "failed" });
}

export async function processOfflineQueue(onSync?: (task: OfflineSyncTask) => void) {
  const tasks = await getPendingSyncTasks();
  for (const task of tasks) {
    try {
      onSync?.(task);
      await markSyncTaskCompleted(task.id);
    } catch (error) {
      await markSyncTaskFailed(task.id);
    }
  }
}
