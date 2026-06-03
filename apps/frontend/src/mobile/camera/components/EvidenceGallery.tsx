import { useEffect, useState } from "react";
import { EvidenceRecord } from "../../offline/db/palmcore-db";

interface EvidenceGalleryProps {
  evidences: EvidenceRecord[];
}

export default function EvidenceGallery({ evidences }: EvidenceGalleryProps) {
  const [evidencePreviews, setEvidencePreviews] = useState(
    [] as Array<EvidenceRecord & { previewUrl: string }>,
  );

  useEffect(() => {
    const previews = evidences.map((item) => ({
      ...item,
      previewUrl: URL.createObjectURL(item.localFile),
    }));
    setEvidencePreviews(previews);
    return () => {
      previews.forEach((item) => URL.revokeObjectURL(item.previewUrl));
    };
  }, [evidences]);

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {evidencePreviews.map((item) => (
          <div key={item.id} className="overflow-hidden rounded-[1.75rem] border border-slate-700 bg-industrial-800 p-4">
            <div className="relative mb-4 overflow-hidden rounded-[1.5rem] bg-black">
              {item.mimeType.startsWith("video") ? (
                <video controls src={item.previewUrl} className="h-52 w-full object-cover" />
              ) : (
                <img src={item.previewUrl} alt={item.fileName} className="h-52 w-full object-cover" />
              )}
            </div>
            <div className="space-y-2 text-sm text-slate-300">
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-white">{item.type}</span>
                <span className="rounded-full bg-slate-700 px-2 py-1 text-[11px] uppercase tracking-[0.25em] text-slate-200">{item.status}</span>
              </div>
              <p>{item.fileName}</p>
              <p>{new Date(item.createdAt).toLocaleString()}</p>
              <p>{(item.fileSize / 1024).toFixed(1)} KB</p>
              <p className="text-slate-400">{item.uploadedBy}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
