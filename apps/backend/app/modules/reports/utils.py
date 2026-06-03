from decimal import Decimal
from typing import Optional


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def format_currency(value: Optional[float]) -> str:
    if value is None:
        value = 0.0
    return f"${value:,.2f}"


def normalize_number(value: Optional[float]) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)
