import { Link, Navigate, Route, Routes } from "react-router-dom";
import EquipmentDetailPage from "./qr/pages/EquipmentDetailPage";
import EquipmentScanPage from "./qr/pages/EquipmentScanPage";
import MobileWorkOrdersPage from "./work-orders/pages/MobileWorkOrdersPage";
import MobileWorkOrderDetailPage from "./work-orders/pages/MobileWorkOrderDetailPage";
import WorkOrderEvidencePage from "./camera/pages/WorkOrderEvidencePage";

export default function MobileRoutes() {
  return (
    <div className="min-h-screen bg-industrial-900 text-slate-100">
      <header className="border-b border-slate-700 px-4 py-4 flex flex-col gap-4 bg-industrial-800 sticky top-0 z-10 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">PalmCore Mobile</p>
          <h1 className="text-xl font-semibold">OT y QR Industrial</h1>
        </div>
        <nav className="flex flex-wrap gap-3">
          <Link className="rounded-full border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:bg-slate-700" to="/mobile/work-orders">
            OT
          </Link>
          <Link className="rounded-full border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:bg-slate-700" to="/mobile/scanner">
            Escáner QR
          </Link>
        </nav>
      </header>

      <main className="px-4 py-4">
        <Routes>
          <Route path="" element={<Navigate to="work-orders" replace />} />
          <Route path="scanner" element={<EquipmentScanPage />} />
          <Route path="equipment/:id" element={<EquipmentDetailPage />} />
          <Route path="work-orders" element={<MobileWorkOrdersPage />} />
          <Route path="work-orders/:id" element={<MobileWorkOrderDetailPage />} />
          <Route path="work-orders/:id/evidence" element={<WorkOrderEvidencePage />} />
        </Routes>
      </main>
    </div>
  );
}
