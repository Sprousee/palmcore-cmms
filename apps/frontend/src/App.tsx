import { useEffect, useState } from "react";
import { Link, Route, Routes } from "react-router-dom";
import { registerServiceWorker } from "./registerServiceWorker";
import MobileRoutes from "./mobile/MobileRoutes";

function HomePage() {
  return (
    <main className="min-h-screen bg-industrial-900 px-4 py-8 text-slate-100">
      <section className="mx-auto max-w-3xl rounded-[2rem] border border-slate-700 bg-industrial-800/90 p-6 shadow-2xl shadow-black/40">
        <h1 className="text-4xl font-semibold text-white">PalmCore CMMS</h1>
        <p className="mt-3 max-w-2xl text-base text-slate-300">Aplicación PWA industrial para técnicos en campo. Navega a la experiencia móvil para gestionar órdenes de trabajo, checklist y workflow en tablet o celular.</p>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <Link className="inline-flex items-center justify-center rounded-3xl bg-orange-500 px-6 py-4 text-base font-semibold text-slate-950 shadow-lg shadow-orange-500/20 transition hover:bg-orange-400" to="/mobile">
            Ir a OT móviles
          </Link>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/40 px-5 py-4 text-sm text-slate-300">
            <p className="font-semibold text-slate-100">Modo Mobile</p>
            <p className="mt-1">Flujo táctil, diseño industrial y rutas móviles ya disponibles.</p>
          </div>
        </div>
      </section>
    </main>
  );
}

export default function App() {
  const [offlineReady, setOfflineReady] = useState(false);
  const [needRefresh, setNeedRefresh] = useState(false);
  const [updateServiceWorker, setUpdateServiceWorker] = useState<() => void>(() => () => {});

  useEffect(() => {
    const updateSW = registerServiceWorker(
      () => setNeedRefresh(true),
      () => setOfflineReady(true),
    );
    setUpdateServiceWorker(() => updateSW);
  }, []);

  return (
    <div className="min-h-screen bg-industrial-900 text-slate-100">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/mobile/*" element={<MobileRoutes />} />
        <Route path="*" element={<HomePage />} />
      </Routes>

      <div className="fixed bottom-4 left-4 right-4 z-20 rounded-3xl border border-slate-700 bg-slate-950/95 p-4 text-sm text-slate-300 shadow-2xl shadow-black/40 md:left-auto md:right-8 md:w-auto">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span>{offlineReady ? "Offline listo" : "Offline no disponible"}</span>
          {needRefresh && (
            <button onClick={() => updateServiceWorker()} className="rounded-full bg-blue-600 px-4 py-2 text-white">
              Actualizar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
