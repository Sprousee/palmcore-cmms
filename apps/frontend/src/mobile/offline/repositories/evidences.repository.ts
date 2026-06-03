import { db, EvidenceRecord } from "../db/palmcore-db";
import { addSyncTask } from "../sync/queue-manager";

export async function saveEvidenceForWorkOrder(params: {
  workOrderId: string;
  equipmentId: string;
  companyId: string;
  type: "BEFORE" | "AFTER" | "INSPECTION" | "FAILURE";
  file: Blob;
  fileName: string;
  mimeType: string;
  fileSize: number;
}) {
  const id = typeof crypto !== "undefined" && typeof crypto.randomUUID === "function" ? crypto.randomUUID() : `evidence-${Date.now()}`;
  const evidenceRecord: EvidenceRecord = {
    id,
    workOrderId: params.workOrderId,
    equipmentId: params.equipmentId,
    companyId: params.companyId,
    type: params.type,
    fileName: params.fileName,
    mimeType: params.mimeType,
    fileSize: params.fileSize,
    localFile: params.file,
    status: "PENDING",
    createdAt: new Date().toISOString(),
    uploadedBy: "Técnico móvil",
  };

  await db.evidences.put(evidenceRecord);
  await addSyncTask({
    action: "create",
    entity: "evidence",
    entityId: evidenceRecord.id,
    payload: JSON.stringify({
      id: evidenceRecord.id,
      workOrderId: evidenceRecord.workOrderId,
      equipmentId: evidenceRecord.equipmentId,
      companyId: evidenceRecord.companyId,
      type: evidenceRecord.type,
      fileName: evidenceRecord.fileName,
      mimeType: evidenceRecord.mimeType,
      fileSize: evidenceRecord.fileSize,
      createdAt: evidenceRecord.createdAt,
      uploadedBy: evidenceRecord.uploadedBy,
    }),
  });

  return evidenceRecord;
}

export async function getEvidenceByWorkOrder(workOrderId: string): Promise<EvidenceRecord[]> {
  return await db.evidences.where("workOrderId").equals(workOrderId).toArray();
}

export async function getPendingEvidence(): Promise<EvidenceRecord[]> {
  return await db.evidences.where("status").equals("PENDING").toArray();
}

export async function markEvidenceSynced(id: string) {
  await db.evidences.update(id, { status: "SYNCED" });
}

export async function markEvidenceFailed(id: string) {
  await db.evidences.update(id, { status: "FAILED" });
}
