import { MobileWorkOrder } from "../store/mobileWorkOrdersStore";
import { getAllWorkOrders, getWorkOrderById, saveWorkOrder } from "../../offline/repositories/workorders.repository";
import { syncAllIfOnline } from "../../offline/sync/sync-manager";

export async function fetchMobileWorkOrders(): Promise<MobileWorkOrder[]> {
  if (typeof navigator !== "undefined" && navigator.onLine) {
    await syncAllIfOnline();
  }
  const orders = await getAllWorkOrders();
  return orders;
}

export async function fetchMobileWorkOrderById(id: string): Promise<MobileWorkOrder | undefined> {
  return await getWorkOrderById(id);
}

export async function saveMobileWorkOrders(orders: MobileWorkOrder[]) {
  await Promise.all(orders.map((order) => saveWorkOrder(order)));
}
