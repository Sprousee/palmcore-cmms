from app.models.inventory_alert import InventoryAlert
from app.models.spare_part import SparePart


def build_stock_alert(part: SparePart) -> InventoryAlert:
    message = (
        f"Stock crítico para {part.name}: {part.current_stock} {part.unit_measure} restantes. "
        f"Mínimo definido: {part.minimum_stock}."
    )
    return InventoryAlert(
        company_id=part.company_id,
        spare_part_id=part.id,
        alert_type="stock_critical",
        message=message,
        is_read=False,
    )


def should_create_stock_alert(part: SparePart) -> bool:
    if part.minimum_stock is None:
        return False
    return part.current_stock <= part.minimum_stock
