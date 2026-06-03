import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchMobileWorkOrderById, fetchMobileWorkOrders, saveMobileWorkOrders } from "../api/workOrdersApi";
import { connectWorkOrdersSocket, WorkOrderEvent } from "../api/wsClient";
import { MobileWorkOrder, useMobileWorkOrdersStore } from "../store/mobileWorkOrdersStore";

export function useMobileWorkOrders() {
  const setOrders = useMobileWorkOrdersStore((state) => state.loadWorkOrders);
  const queryClient = useQueryClient();

  const query = useQuery<MobileWorkOrder[]>(["mobileWorkOrders"], fetchMobileWorkOrders, {
    onSuccess: (orders) => {
      setOrders(orders);
    },
    staleTime: 1000 * 60 * 2,
    cacheTime: 1000 * 60 * 5,
  });

  useEffect(() => {
    const disconnect = connectWorkOrdersSocket((event: WorkOrderEvent) => {
      if (event.type === "status_changed") {
        queryClient.invalidateQueries(["mobileWorkOrders"]);
      }
    });
    return () => disconnect();
  }, [queryClient]);

  return query;
}

export function useMobileWorkOrder(id: string | undefined) {
  return useQuery<MobileWorkOrder | undefined>(["mobileWorkOrder", id], () =>
    id ? fetchMobileWorkOrderById(id) : Promise.resolve(undefined),
  );
}
