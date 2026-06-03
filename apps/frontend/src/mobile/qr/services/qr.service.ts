export interface EquipmentQrPayload {
  type: "equipment";
  equipment_id: string;
  company_id: string;
}

export function parseEquipmentQrPayload(raw: string): EquipmentQrPayload {
  let payload: unknown;
  try {
    payload = JSON.parse(raw);
  } catch (error) {
    throw new Error("QR inválido: no es JSON válido.");
  }

  if (!isEquipmentQrPayload(payload)) {
    throw new Error("QR inválido: formato inesperado.");
  }

  return payload;
}

export function isEquipmentQrPayload(value: unknown): value is EquipmentQrPayload {
  return (
    typeof value === "object" &&
    value !== null &&
    (value as any).type === "equipment" &&
    typeof (value as any).equipment_id === "string" &&
    typeof (value as any).company_id === "string"
  );
}
