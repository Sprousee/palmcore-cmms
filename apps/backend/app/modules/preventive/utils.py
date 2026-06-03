from datetime import date, timedelta
from typing import Optional


def calculate_next_scheduled_date(
    last_date: date,
    frequency_type: str,
    frequency_value: int,
) -> date:
    if frequency_type.lower() == "daily":
        return last_date + timedelta(days=frequency_value)
    if frequency_type.lower() == "weekly":
        return last_date + timedelta(weeks=frequency_value)
    if frequency_type.lower() == "monthly":
        return date(
            last_date.year,
            min(12, last_date.month + frequency_value),
            last_date.day,
        )
    return last_date + timedelta(days=frequency_value)


def calculate_days_overdue(scheduled_date: date, reference_date: Optional[date] = None) -> int:
    reference_date = reference_date or date.today()
    return max(0, (reference_date - scheduled_date).days)
