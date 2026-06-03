import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import QRScanner from "../scanner/QRScanner";
import { parseEquipmentQrPayload } from "../services/qr.service";
import { getEquipmentById } from "../../offline/repositories/equipment.repository";

export default function EquipmentScanPage() {
  const navigate = useNavigate();
  const [message, setMessage] = useState<string>("Escanea el QR del equipo para abrir su ficha técnica.");
  const [error, setError] = useState<string | null>(null);

  const onScan = useCallback(async (decodedText: string) => {
    setError(null);
    try {
      const payload = parseEquipmentQrPayload(decodedText);
      const equipment = await getEquipmentById(payload.equipment_id);

      if (!equipment) {
        setError("Equipo no encontrado en la caché local. Sincroniza la base de equipos.");
        setMessage("Puedes abrir la ficha cuando el equipo esté disponible offline.");
        return;
      }

      if (equipment.companyId !== payload.company_id) {
        setError("QR no corresponde al tenant actual.");
        return;
      }

      setMessage(`Equipo detectado: ${equipment.name}. Abriendo ficha...`);
      setTimeout(() => {
        navigate(`/mobile/equipment/${payload.equipment_id}`);
      }, 300);
    } catch (scanError) {
      setError((scanError as Error).message ?? "No se pudo leer el QR.");
    }
  }, [navigate]);

  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-700 bg-industrial-800 p-5 shadow-xl shadow-black/20">
        <div className="flex flex-col gap-2">
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Escaneo QR</p>
          <h1 className="text-3xl font-semibold text-white">Escanear equipo</h1>
          <p className="text-sm text-slate-400">Camina por planta, apunta al QR y deja que el sistema abra la ficha automáticamente.</p>
        </div>
      </div>

      <QRScanner onScan={onScan} />

      <div className="rounded-3xl border border-slate-700 bg-slate-950/40 p-4 text-sm text-slate-300">
        <p>{message}</p>
        {error && <p className="mt-3 text-sm text-orange-300">{error}</p>}
      </div>
    </section>
  );
}
