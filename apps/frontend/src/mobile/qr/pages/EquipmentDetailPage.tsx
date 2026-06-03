import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getEquipmentById, getEquipmentHistoryById } from "../../offline/repositories/equipment.repository";
import { createWorkOrderForEquipment } from "../../offline/repositories/workorders.repository";

interface EquipmentHistoryItem {
  id: string;
  code: string;
  title: string;
  status: string;
  createdAt: string;
  updatedAt: string;
}

export default function EquipmentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [equipment, setEquipment] = useState<any>(null);
  const [history, setHistory] = useState<EquipmentHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([getEquipmentById(id), getEquipmentHistoryById(id)])
      .then(([equipmentRecord, historyItems]) => {
        if (!equipmentRecord) {
          setError("Equipo no encontrado en la base de datos local.");
          return;
        }
        setEquipment(equipmentRecord);
        setHistory(
          historyItems
            .slice()
            .sort((a, b) => (a.createdAt > b.createdAt ? -1 : 1))
            .map((item) => ({
              id: item.id,
              code: item.code,
              title: item.title,
              status: item.status,
              createdAt: item.createdAt,
              updatedAt: item.updatedAt,
            })),
        );
      })
      .catch(() => setError("No se pudo cargar la ficha del equipo."))
      .finally(() => setLoading(false));
  }, [id]);

  const lastOt = useMemo(() => history[0], [history]);

  const handleCreateOt = async () => {
    if (!equipment) return;

    try {
      const newOrder = await createWorkOrderForEquipment(equipment);
      navigate(`/mobile/work-orders/${newOrder.id}`);
    } catch {
      setError("No se pudo crear la OT. Intenta nuevamente.");
    }
  };

  if (loading) {
    return <div className="min-h-[60vh] rounded-3xl bg-industrial-800 p-6 text-slate-300">Cargando ficha del equipo...</div>;
  }

  if (!equipment) {
    return (
      <div className="rounded-[2rem] border border-slate-700 bg-industrial-800 p-6 text-slate-300">
        <p>{error ?? "Equipo no disponible."}</p>
        <button onClick={() => navigate("/mobile/scanner")} className="mt-4 rounded-3xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-500">
          Volver al escáner
        </button>
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <button onClick={() => navigate(-1)} className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-700">
        ← Volver
      </button>

      <div className="space-y-4 rounded-[2rem] border border-slate-700 bg-industrial-800 p-5 shadow-xl shadow-black/20">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Ficha técnica</p>
            <h1 className="text-3xl font-semibold text-white">{equipment.name}</h1>
            <p className="mt-2 text-sm text-slate-400">{equipment.plant} · {equipment.area}</p>
          </div>
          <div className="rounded-3xl bg-slate-950/40 p-4 text-sm text-slate-300">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Última OT</p>
            <p className="mt-2 text-base font-semibold text-white">{lastOt?.code ?? "Sin OT reciente"}</p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Código</p>
            <p className="mt-2 text-base font-semibold text-white">{equipment.code}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Estado</p>
            <p className="mt-2 text-base font-semibold text-white">{equipment.status}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Criticidad</p>
            <p className="mt-2 text-base font-semibold text-white">{equipment.criticity}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Horómetro</p>
            <p className="mt-2 text-base font-semibold text-white">{equipment.hourmeter}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Ubicación</p>
            <p className="mt-2 text-base font-semibold text-white">{equipment.location}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Empresa</p>
            <p className="mt-2 text-base font-semibold text-white">{equipment.companyId}</p>
          </div>
        </div>

        <button onClick={handleCreateOt} className="rounded-3xl bg-orange-500 px-5 py-4 text-sm font-semibold text-slate-950 transition hover:bg-orange-400">
          + Crear Orden de Trabajo
        </button>
      </div>

      <div className="rounded-[2rem] border border-slate-700 bg-slate-950/40 p-5">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-xl font-semibold text-white">Historial</h2>
          <span className="text-sm text-slate-400">{history.length} registros</span>
        </div>

        {history.length === 0 ? (
          <p className="mt-4 text-slate-300">No hay historial local para este equipo todavía.</p>
        ) : (
          <div className="mt-4 space-y-3">
            {history.map((item) => (
              <div key={item.id} className="rounded-3xl border border-slate-700 bg-industrial-800 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm text-slate-400">{new Date(item.createdAt).toLocaleDateString()}</p>
                    <p className="mt-1 text-base font-semibold text-white">{item.code}</p>
                  </div>
                  <span className="rounded-full bg-slate-700 px-3 py-1 text-xs uppercase tracking-[0.2em] text-slate-200">{item.status}</span>
                </div>
                <p className="mt-3 text-sm text-slate-300">{item.title}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
