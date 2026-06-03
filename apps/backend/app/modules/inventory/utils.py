from decimal import Decimal


def calculate_total_cost(quantity: int, unit_cost: Decimal) -> Decimal:
    return (Decimal(quantity) * unit_cost).quantize(Decimal("0.01"))


def clamp_stock_value(value: int) -> int:
    return max(0, value)
