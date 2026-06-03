import { Link } from "react-router-dom";
import { MobileWorkOrder } from "../store/mobileWorkOrdersStore";

interface WorkOrderCardProps {
  order: MobileWorkOrder;
}

const statusStyles: Record<string, string> = {
  Pending: "bg-slate-700 text-slate-200",
  Assigned: "bg-blue-600 text-white",
  "In Progress": "bg-orange-500 text-white",
  Paused: "bg-yellow-500 text-slate-900",
  Completed: "bg-emerald-500 text-slate-900",
};

const priorityStyles: Record<string, string> = {
  Low: "bg-slate-600 text-slate-100",
  Medium: "bg-slate-500 text-white",
  High: "bg-orange-600 text-white",
  Critical: "bg-red-600 text-white",
};

export default function WorkOrderCard({ order }: WorkOrderCardProps) {
  return (
    <Link to={`/mobile/work-orders/${order.id}`} className="block rounded-3xl border border-slate-700 bg-industrial-800 p-4 shadow-xl shadow-black/20 transition hover:-translate-y-0.5 hover:border-slate-500">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-slate-400">OT</p>
          <h2 className="text-xl font-semibold text-white">{order.code}</h2>
          <p className="mt-1 text-sm text-slate-300">{order.title}</p>
        </div>
        <div className="flex flex-col gap-2 text-right">
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityStyles[order.priority]}`}>
            {order.priority}
          </span>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[order.status]}`}>
            {order.status}
          </span>
        </div>
      </div>
      <div className="mt-4 grid gap-2 text-sm text-slate-300">
        <div className="flex items-center justify-between">
          <span>Equipo</span>
          <span className="font-medium text-slate-100">{order.equipment}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Técnico</span>
          <span className="font-medium text-slate-100">{order.assignedTechnician}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Vence</span>
          <span className="font-medium text-slate-100">{new Date(order.dueDate).toLocaleDateString()}</span>
        </div>
      </div>
    </Link>
  );
}
