import { useEffect, useMemo, useState } from "react";
import { useCamera } from "../hooks/useCamera";

export type CaptureType = "BEFORE" | "AFTER" | "INSPECTION" | "FAILURE";

interface CameraCaptureProps {
  onCapture: (file: Blob, fileName: string, mimeType: string, type: CaptureType) => void;
}

export default function CameraCapture({ onCapture }: CameraCaptureProps) {
  const {
    videoRef,
    streamActive,
    cameraReady,
    recording,
    error,
    previewUrl,
    captureType,
    captureResult,
    startCamera,
    stopCamera,
    takePhoto,
    startRecording,
    stopRecording,
    resetPreview,
  } = useCamera();

  const [selectedType, setSelectedType] = useState<CaptureType>("BEFORE");

  useEffect(() => {
    void startCamera();
  }, []);

  const previewElement = useMemo(() => {
    if (!previewUrl || !captureType) return null;
    if (captureType === "photo") {
      return <img src={previewUrl} alt="Vista previa" className="h-full w-full rounded-[1.5rem] object-cover" />;
    }
    return (
      <video controls src={previewUrl} className="h-full w-full rounded-[1.5rem] bg-black" />
    );
  }, [previewUrl, captureType]);

  return (
    <div className="space-y-5 rounded-[2rem] border border-slate-700 bg-industrial-800/90 p-4 shadow-xl shadow-black/20">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Cámara de evidencia</p>
          <h2 className="text-2xl font-semibold text-white">Captura foto o video</h2>
          <p className="mt-1 text-sm text-slate-400">Toma evidencia antes/después, falla o inspección desde el dispositivo.</p>
        </div>
        <span className="rounded-full bg-slate-700 px-3 py-2 text-xs uppercase tracking-[0.2em] text-slate-200">
          {cameraReady ? "Listo" : "Iniciando cámara"}
        </span>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[1.75rem] border border-slate-700 bg-slate-950/90 p-3">
          <div className="relative overflow-hidden rounded-[1.5rem] bg-black">
            <video ref={videoRef} muted playsInline className="h-[320px] w-full object-cover" />
          </div>
          <div className="mt-3 flex flex-wrap gap-3">
            <button
              onClick={() => {
                void takePhoto();
              }}
              className="rounded-3xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
            >
              Tomar foto
            </button>
            {recording ? (
              <button
                onClick={() => {
                  void stopRecording();
                }}
                className="rounded-3xl bg-orange-500 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-orange-400"
              >
                Detener video
              </button>
            ) : (
              <button
                onClick={() => {
                  void startRecording();
                }}
                className="rounded-3xl bg-slate-700 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-600"
              >
                Grabar video
              </button>
            )}
            <button
              onClick={() => {
                void stopCamera();
              }}
              className="rounded-3xl border border-slate-600 px-4 py-3 text-sm font-semibold text-slate-200 hover:bg-slate-700"
            >
              Detener cámara
            </button>
          </div>
          {error && <p className="mt-3 text-sm text-orange-300">{error}</p>}
        </div>

        <div className="rounded-[1.75rem] border border-slate-700 bg-slate-950/90 p-4">
          <div className="mb-4 flex flex-wrap gap-2">
            {(["BEFORE", "AFTER", "INSPECTION", "FAILURE"] as CaptureType[]).map((type) => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${selectedType === type ? "bg-orange-500 text-slate-950" : "bg-slate-700 text-slate-200 hover:bg-slate-600"}`}
              >
                {type}
              </button>
            ))}
          </div>

          <div className="rounded-[1.5rem] border border-slate-700 bg-black p-2 h-[320px] overflow-hidden">
            {previewElement ?? <div className="flex h-full items-center justify-center text-slate-500">Vista previa de captura aparecerá aquí</div>}
          </div>

          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={() => {
                if (previewUrl && captureResult) {
                  onCapture(captureResult.file, captureResult.fileName, captureResult.mimeType, selectedType);
                  resetPreview();
                }
              }}
              disabled={!previewUrl}
              className="rounded-3xl bg-green-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Guardar evidencia
            </button>
            <button
              onClick={resetPreview}
              disabled={!previewUrl}
              className="rounded-3xl border border-slate-600 px-4 py-3 text-sm font-semibold text-slate-200 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Repetir captura
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
