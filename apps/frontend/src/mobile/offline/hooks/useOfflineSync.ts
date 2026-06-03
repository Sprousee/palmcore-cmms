import { useEffect, useMemo, useState } from "react";
import { startSyncManager, syncAllIfOnline } from "../sync/sync-manager";
import { getSyncStatusCounts } from "../sync/queue-manager";
import { useNetworkStatus } from "./useNetworkStatus";

export function useOfflineSync() {
  const online = useNetworkStatus();
  const [pendingCount, setPendingCount] = useState(0);
  const [failedCount, setFailedCount] = useState(0);
  const [lastSyncAt, setLastSyncAt] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  const refreshStatus = async () => {
    const counts = await getSyncStatusCounts();
    setPendingCount(counts.pending);
    setFailedCount(counts.failed);
  };

  const triggerSync = async () => {
    if (!online) return;
    setSyncing(true);
    await syncAllIfOnline();
    setLastSyncAt(new Date().toLocaleTimeString());
    await refreshStatus();
    setSyncing(false);
  };

  useEffect(() => {
    refreshStatus();
    const cleanup = startSyncManager();
    return () => cleanup();
  }, []);

  useEffect(() => {
    if (online) {
      triggerSync();
    }
  }, [online]);

  const statusLabel = useMemo(() => {
    if (syncing) return "Sincronizando...";
    return online ? "Conectado" : "Sin conexión";
  }, [online, syncing]);

  return {
    online,
    statusLabel,
    pendingCount,
    failedCount,
    lastSyncAt,
    syncing,
    triggerSync,
  };
}
