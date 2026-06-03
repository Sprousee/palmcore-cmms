import { useMemo } from "react";
import { Link } from "react-router-dom";
import WorkOrderCard from "../components/WorkOrderCard";
import { useMobileWorkOrders } from "../hooks/useMobileWorkOrders";
import { useMobileWorkOrdersStore } from "../store/mobileWorkOrdersStore";
import { useOfflineSync } from "../../offline/hooks/useOfflineSync";

export default function MobileWorkOrdersPage() {
  const { data, isLoading, isFetching } = useMobileWorkOrders();
  const orders = useMobileWorkOrdersStore((state) => state.workOrders);
  const { online, statusLabel, pendingCount, lastSyncAt, triggerSync } = useOfflineSync();

  const sortedOrders = useMemo(
    () => orders.slice().sort((a, b) => (a.priority === b.priority ? 0 : a.priority === "Critical" ? -1 : 1)),
    [orders],
  );

  return (
    <section>
      <div className="mb-6 space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold text-white">OT Asignadas</h2>
            <p className="text-sm text-slate-400">Toca cualquier orden para ver el detalle y el workflow.</p>
          </div>
          <span className="rounded-full bg-slate-700 px-3 py-2 text-xs text-slate-200">{isFetching ? "Actualizando..." : "En línea"}</span>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-3xl border border-slate-700 bg-slate-950/70 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Estado de red</p>
            <p className="mt-2 text-lg font-semibold text-white">{statusLabel}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/70 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Cola de sincronización</p>
            <p className="mt-2 text-lg font-semibold text-white">{pendingCount} pendientes</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/70 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Última sincronización</p>
            <p className="mt-2 text-lg font-semibold text-white">{lastSyncAt ?? "Nunca"}</p>
          </div>
        </div>

        <button
          onClick={triggerSync}
          disabled={!online}
          className="rounded-3xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Forzar sincronización
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((item) => (
            <div key={item} className="h-40 rounded-3xl bg-slate-800/70 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {sortedOrders.length === 0 ? (
            <div className="rounded-3xl border border-slate-700 bg-industrial-800 p-6 text-center text-slate-300">No hay OT asignadas por el momento.</div>
          ) : (
            sortedOrders.map((order) => <WorkOrderCard key={order.id} order={order} />)
          )}
        </div>
      )}

      <div className="mt-6 rounded-3xl border border-slate-700 bg-industrial-800 p-4 text-sm text-slate-300">
        <p className="font-semibold text-white">Consejos de campo</p>
        <ul className="mt-3 space-y-2 list-disc pl-5 text-slate-400">
          <li>Usa guantes y cubre cuando trabajes con maquinaria.</li>
          <li>Verifica el estado del checklist antes de cerrar la OT.</li>
          <li>Registra tiempos reales y actualiza el estado en cada paso.</li>
        </ul>
      </div>

      <div className="mt-6 text-center text-sm text-slate-400">
        <Link to="/" className="font-semibold text-slate-100 hover:text-white">
          Volver al inicio PWA
        </Link>
      </div>
    </section>
  );
}
