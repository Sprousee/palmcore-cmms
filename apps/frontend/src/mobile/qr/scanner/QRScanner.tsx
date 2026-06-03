import { useEffect, useMemo, useState } from "react";
import { useQRScanner } from "../hooks/useQRScanner";

interface QRScannerProps {
  onScan: (decodedText: string) => void;
}

export default function QRScanner({ onScan }: QRScannerProps) {
  const { scanning, error, flashAvailable, torchOn, cameraLabel, start, stop, toggleFlash } = useQRScanner(onScan);
  const [infoMessage, setInfoMessage] = useState("Apunta la cámara al QR del equipo.");

  useEffect(() => {
    void start();
    return () => {
      void stop();
    };
  }, []);

  const statusLabel = useMemo(() => {
    if (error) return error;
    return scanning ? "Escaneando..." : "Presiona para iniciar el escáner.";
  }, [error, scanning]);

  return (
    <div className="space-y-5 rounded-[2rem] border border-slate-700 bg-industrial-800/90 p-4 shadow-xl shadow-black/20">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Escáner QR</p>
          <h2 className="text-xl font-semibold text-white">Modo industrial</h2>
          <p className="mt-2 text-sm text-slate-300">{cameraLabel}</p>
        </div>
        <span className="rounded-full bg-slate-700 px-3 py-2 text-xs uppercase tracking-[0.2em] text-slate-200">{statusLabel}</span>
      </div>

      <div className="relative overflow-hidden rounded-[1.75rem] border border-slate-700 bg-slate-950/80 p-2">
        <div id="qr-scanner" className="h-[320px] min-h-[320px] rounded-[1.5rem] bg-slate-900" />
        <div className="pointer-events-none absolute inset-x-0 top-0 mx-auto flex h-full max-w-[320px] items-center justify-center opacity-60">
          <div className="h-[250px] w-[250px] rounded-3xl border border-slate-500" />
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <button
          onClick={() => {
            if (scanning) {
              void stop();
              setInfoMessage("Escáner detenido. Vuelve a iniciar si lo necesitas.");
            } else {
              void start();
              setInfoMessage("Escaneando con la cámara trasera.");
            }
          }}
          className="rounded-3xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
        >
          {scanning ? "Detener" : "Iniciar escáner"}
        </button>
        <button
          onClick={() => {
            if (flashAvailable) {
              void toggleFlash();
            }
          }}
          disabled={!flashAvailable}
          className="rounded-3xl bg-slate-700 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-600 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {torchOn ? "Flash encendido" : "Flash"}
        </button>
      </div>

      <p className="text-sm leading-6 text-slate-400">{infoMessage}</p>
    </div>
  );
}
