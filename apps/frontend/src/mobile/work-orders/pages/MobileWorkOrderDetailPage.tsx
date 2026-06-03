import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMobileWorkOrder } from "../hooks/useMobileWorkOrders";
import { useMobileWorkOrdersStore } from "../store/mobileWorkOrdersStore";
import { toggleChecklistItem as toggleChecklistOffline, updateWorkOrderStatus as updateWorkOrderStatusOffline } from "../../offline/repositories/workorders.repository";
import MobileChecklist from "../components/MobileChecklist";
import MobileWorkflowButtons from "../components/MobileWorkflowButtons";

export default function MobileWorkOrderDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data, isLoading } = useMobileWorkOrder(id);
  const order = useMobileWorkOrdersStore((state) => state.workOrders.find((order) => order.id === id));
  const updateStatus = useMobileWorkOrdersStore((state) => state.updateWorkOrderStatus);
  const toggleChecklistItem = useMobileWorkOrdersStore((state) => state.toggleChecklistItem);
  const updateOrderTimes = useMobileWorkOrdersStore((state) => state.updateOrderTimes);

  const currentOrder = order ?? data;

  const timeLabel = useMemo(() => {
    if (!currentOrder) return "---";
    const minutes = currentOrder.spentMinutes;
    return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
  }, [currentOrder]);

  if (isLoading || !currentOrder) {
    return <div className="min-h-[60vh] rounded-3xl bg-industrial-800 p-6 text-slate-300">Cargando OT...</div>;
  }

  return (
    <section className="space-y-6">
      <button onClick={() => navigate(-1)} className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-700">
        ← Volver
      </button>

      <div className="space-y-4 rounded-[2rem] border border-slate-700 bg-industrial-800 p-5 shadow-xl shadow-black/20">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.34em] text-slate-400">OT móvil</p>
            <h1 className="text-2xl font-semibold text-white">{currentOrder.code}</h1>
            <p className="mt-1 text-sm text-slate-300">{currentOrder.title}</p>
          </div>
          <span className="rounded-full bg-slate-700 px-3 py-2 text-xs uppercase tracking-[0.22em] text-slate-200">{currentOrder.status}</span>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Equipo</p>
            <p className="mt-2 text-base font-semibold text-white">{currentOrder.equipment}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Prioridad</p>
            <p className="mt-2 text-base font-semibold text-white">{currentOrder.priority}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Técnico</p>
            <p className="mt-2 text-base font-semibold text-white">{currentOrder.assignedTechnician}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Tiempo total</p>
            <p className="mt-2 text-base font-semibold text-white">{timeLabel}</p>
          </div>
        </div>

        <div className="space-y-3 rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
          <h2 className="text-base font-semibold text-white">Notas de la orden</h2>
          <p className="text-sm leading-6 text-slate-300">{currentOrder.notes}</p>
        </div>

        <MobileChecklist
          items={currentOrder.checklist}
          onToggle={(itemId) => {
            toggleChecklistItem(currentOrder.id, itemId);
            void toggleChecklistOffline(currentOrder.id, itemId);
          }}
        />

        <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
          <h2 className="text-base font-semibold text-white">Repuestos y evidencia</h2>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <div className="rounded-3xl bg-industrial-900 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Repuestos</p>
              <ul className="mt-3 space-y-2 text-sm text-slate-200">
                {currentOrder.parts.map((part) => (
                  <li key={part} className="rounded-2xl bg-slate-800 px-3 py-2">{part}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-3xl bg-industrial-900 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Evidencias</p>
              <p className="mt-3 text-2xl font-semibold text-white">{currentOrder.evidenceCount}</p>
              <p className="text-sm text-slate-400">Fotos / documentos</p>
            </div>
          </div>
        </div>

        <MobileWorkflowButtons
          status={currentOrder.status}
          onChangeStatus={(next) => {
            updateStatus(currentOrder.id, next);
            void updateWorkOrderStatusOffline(currentOrder.id, next);
          }}
        />

        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => updateOrderTimes(currentOrder.id, 15)}
            className="rounded-3xl bg-slate-700 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-600"
          >
            +15 min trabajo
          </button>
          <button
            onClick={() => updateOrderTimes(currentOrder.id, 5)}
            className="rounded-3xl bg-slate-700 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-600"
          >
            +5 min pausa
          </button>
          <button
            onClick={() => navigate(`/mobile/work-orders/${currentOrder.id}/evidence`)}
            className="rounded-3xl bg-orange-500 px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-orange-400"
          >
            Registrar evidencia
          </button>
        </div>
      </div>
    </section>
  );
}
