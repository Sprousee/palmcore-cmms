import { db, SyncQueueRecord } from "../db/palmcore-db";
import { getPendingSyncTasks, markTaskCompleted, markTaskFailed, markTaskProcessing } from "./queue-manager";

async function syncTaskToBackend(task: SyncQueueRecord) {
  // Placeholder for backend sync. Replace this with real API calls.
  await new Promise((resolve) => setTimeout(resolve, 250));
  return {
    success: true,
    result: { syncedAt: new Date().toISOString() },
  };
}

export async function processSyncQueue() {
  const tasks = await getPendingSyncTasks();
  for (const task of tasks) {
    await markTaskProcessing(task.id);
    try {
      const response = await syncTaskToBackend(task);
      if (response.success) {
        await markTaskCompleted(task.id);
        if (task.entity === "workOrder") {
          await db.workOrders.update(task.entityId, { offlineStatus: "synced" });
        }
        if (task.entity === "checklist") {
          await db.checklists.update(task.entityId, { offlineStatus: "synced" });
        }
        if (task.entity === "evidence") {
          await db.evidences.update(task.entityId, { status: "SYNCED" });
        }
      } else {
        await markTaskFailed(task.id);
      }
    } catch (error) {
      await markTaskFailed(task.id);
    }
  }
}

export async function syncAllIfOnline() {
  if (typeof navigator !== "undefined" && navigator.onLine) {
    await processSyncQueue();
  }
}

export function startSyncManager() {
  if (typeof window === "undefined") return () => {};

  const onOnline = async () => {
    await syncAllIfOnline();
  };

  window.addEventListener("online", onOnline);

  return () => {
    window.removeEventListener("online", onOnline);
  };
}
