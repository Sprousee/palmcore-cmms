import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CameraCapture, { CaptureType } from "../components/CameraCapture";
import EvidenceGallery from "../components/EvidenceGallery";
import { EvidenceRecord } from "../../offline/db/palmcore-db";
import { compressImageFile } from "../services/image-compression";
import { saveEvidenceForWorkOrder, getEvidenceByWorkOrder } from "../../offline/repositories/evidences.repository";
import { useMobileWorkOrder } from "../../work-orders/hooks/useMobileWorkOrders";
import { useOfflineSync } from "../../offline/hooks/useOfflineSync";

export default function WorkOrderEvidencePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: workOrder, isLoading } = useMobileWorkOrder(id);
  const { online, statusLabel, pendingCount, failedCount, triggerSync } = useOfflineSync();
  const [evidences, setEvidences] = useState<EvidenceRecord[]>([]);
  const [message, setMessage] = useState<string>("Captura evidencia asociada a esta OT.");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    void loadEvidences();
  }, [id]);

  const loadEvidences = async () => {
    const items = await getEvidenceByWorkOrder(id ?? "");
    setEvidences(items);
  };

  const handleCapture = async (file: Blob, fileName: string, mimeType: string, type: CaptureType) => {
    if (!workOrder) {
      setError("No se encontró la OT. Recarga la página.");
      return;
    }
    setError(null);
    setMessage("Procesando evidencia...");

    try {
      const processedFile = mimeType.startsWith("image") ? await compressImageFile(new File([file], fileName, { type: mimeType })) : file;
      await saveEvidenceForWorkOrder({
        workOrderId: workOrder.id,
        equipmentId: workOrder.equipmentId,
        companyId: "company-123",
        type,
        file: processedFile,
        fileName,
        mimeType,
        fileSize: processedFile.size,
      });
      setMessage("Evidencia guardada localmente.");
      await loadEvidences();
      if (online) {
        await triggerSync();
      }
    } catch (err) {
      setError("No se pudo guardar la evidencia.");
    }
  };

  const evidenceCount = evidences.length;

  if (isLoading) {
    return <div className="min-h-[60vh] rounded-3xl bg-industrial-800 p-6 text-slate-300">Cargando evidencia...</div>;
  }

  if (!workOrder) {
    return (
      <div className="rounded-[2rem] border border-slate-700 bg-industrial-800 p-6 text-slate-300">
        <p>No se encontró la orden de trabajo.</p>
        <button onClick={() => navigate(-1)} className="mt-4 rounded-3xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-500">
          Volver
        </button>
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <button onClick={() => navigate(-1)} className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-700">
        ← Volver
      </button>

      <div className="rounded-[2rem] border border-slate-700 bg-industrial-800 p-5 shadow-xl shadow-black/20">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Evidencia de OT</p>
            <h1 className="text-3xl font-semibold text-white">{workOrder.code}</h1>
            <p className="mt-2 text-sm text-slate-400">Equipo: {workOrder.equipment}</p>
          </div>
          <div className="grid gap-2 sm:text-right">
            <span className="rounded-3xl bg-slate-950/70 px-4 py-3 text-sm font-semibold text-slate-200">{statusLabel}</span>
            <span className="rounded-3xl bg-slate-950/70 px-4 py-3 text-sm font-semibold text-slate-200">{pendingCount} en cola</span>
            <span className="rounded-3xl bg-slate-950/70 px-4 py-3 text-sm font-semibold text-slate-200">{failedCount} fallidas</span>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <CameraCapture onCapture={handleCapture} />
        <div className="rounded-[2rem] border border-slate-700 bg-slate-950/40 p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Galería de evidencias</p>
              <h2 className="text-xl font-semibold text-white">{evidenceCount} registros</h2>
            </div>
            <button onClick={loadEvidences} className="rounded-3xl bg-slate-700 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-600">
              Actualizar lista
            </button>
          </div>
          {error && <p className="mt-3 text-sm text-orange-300">{error}</p>}
          <p className="mt-2 text-sm text-slate-400">{message}</p>
          <EvidenceGallery evidences={evidences} />
        </div>
      </div>
    </section>
  );
}
