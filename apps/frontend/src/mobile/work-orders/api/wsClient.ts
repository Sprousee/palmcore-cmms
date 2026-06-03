export type WorkOrderEvent =
  | { type: "new_work_order"; payload: { id: string; code: string; title: string } }
  | { type: "status_changed"; payload: { id: string; status: string } }
  | { type: "critical_alert"; payload: { message: string } };

export function connectWorkOrdersSocket(onEvent: (event: WorkOrderEvent) => void) {
  let intervalId: number | undefined;

  if (typeof WebSocket !== "undefined") {
    try {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const host = window.location.host;
      const ws = new WebSocket(`${protocol}://${host}/ws/work-orders`);

      ws.addEventListener("message", (event) => {
        try {
          const data = JSON.parse(event.data) as WorkOrderEvent;
          onEvent(data);
        } catch {
          // ignore invalid message
        }
      });

      ws.addEventListener("error", () => {
        ws.close();
      });

      return () => {
        ws.close();
      };
    } catch {
      intervalId = window.setInterval(() => {
        onEvent({ type: "status_changed", payload: { id: "1", status: "In Progress" } });
      }, 20000);
      return () => window.clearInterval(intervalId);
    }
  }

  intervalId = window.setInterval(() => {
    onEvent({ type: "status_changed", payload: { id: "1", status: "In Progress" } });
  }, 20000);

  return () => window.clearInterval(intervalId);
}
