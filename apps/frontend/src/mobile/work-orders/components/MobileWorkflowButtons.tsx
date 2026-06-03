import { WorkOrderStatus } from "../store/mobileWorkOrdersStore";

interface MobileWorkflowButtonsProps {
  status: WorkOrderStatus;
  onChangeStatus: (nextStatus: WorkOrderStatus) => void;
}

const buttonConfig: { label: string; status: WorkOrderStatus; style: string }[] = [
  { label: "Iniciar", status: "In Progress", style: "bg-orange-500 text-white" },
  { label: "Pausar", status: "Paused", style: "bg-yellow-500 text-slate-900" },
  { label: "Completar", status: "Completed", style: "bg-emerald-500 text-slate-950" },
];

export default function MobileWorkflowButtons({ status, onChangeStatus }: MobileWorkflowButtonsProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-base font-semibold text-white">Workflow</h3>
      <div className="grid gap-3 md:grid-cols-3">
        {buttonConfig.map((button) => (
          <button
            key={button.status}
            onClick={() => onChangeStatus(button.status)}
            disabled={button.status === status}
            className={`rounded-3xl px-4 py-4 text-sm font-semibold shadow-lg shadow-black/25 transition disabled:cursor-not-allowed disabled:opacity-50 ${button.style}`}
          >
            {button.label}
          </button>
        ))}
      </div>
    </div>
  );
}
