import { registerSW } from "virtual:pwa-register";

export function registerServiceWorker(onNeedRefresh?: () => void, onOfflineReady?: () => void) {
  return registerSW({
    onNeedRefresh() {
      onNeedRefresh?.();
    },
    onOfflineReady() {
      onOfflineReady?.();
    },
  });
}
