import { ChecklistItem } from "../store/mobileWorkOrdersStore";

interface MobileChecklistProps {
  items: ChecklistItem[];
  onToggle: (itemId: string) => void;
}

export default function MobileChecklist({ items, onToggle }: MobileChecklistProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-base font-semibold text-white">Checklist</h3>
      {items.map((item) => (
        <button
          key={item.id}
          onClick={() => onToggle(item.id)}
          className={`flex w-full items-center justify-between rounded-3xl border px-4 py-4 text-left transition ${item.completed ? "border-emerald-500 bg-emerald-500/10" : "border-slate-700 bg-slate-950/50 hover:border-slate-500"}`}
        >
          <span className={`text-sm font-medium ${item.completed ? "text-emerald-100" : "text-slate-100"}`}>
            {item.label}
          </span>
          <span className={`inline-flex h-9 w-9 items-center justify-center rounded-full border text-sm font-semibold ${item.completed ? "border-emerald-400 bg-emerald-400 text-slate-950" : "border-slate-600 text-slate-300"}`}>
            {item.completed ? "✓" : ""}
          </span>
        </button>
      ))}
    </div>
  );
}
