import qrcode
from pathlib import Path
from uuid import UUID

from app.core.config import settings


def generate_equipment_qr_code(equipment_id: UUID) -> str:
    base_dir = Path(__file__).resolve().parents[4]
    output_dir = base_dir / "static" / "qr"
    output_dir.mkdir(parents=True, exist_ok=True)

    qr_url = f"{settings.QR_BASE_URL}/{equipment_id}"
    qr_file = output_dir / f"{equipment_id}.png"

    qr_image = qrcode.make(qr_url)
    qr_image.save(qr_file)

    return str(qr_file.relative_to(base_dir))
