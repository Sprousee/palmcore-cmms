from typing import Optional


def calculate_availability(mtbf_minutes: float, mttr_minutes: float) -> float:
    if mtbf_minutes + mttr_minutes <= 0:
        return 0.0
    return round((mtbf_minutes / (mtbf_minutes + mttr_minutes)) * 100, 2)


def calculate_preventive_compliance(completed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((completed / total) * 100, 2)


def calculate_mttr(total_minutes: float, count: int) -> float:
    if count <= 0:
        return 0.0
    return round(total_minutes / count, 2)


def calculate_mtbf(total_minutes: float, failures: int) -> float:
    if failures <= 0:
        return 0.0
    return round(total_minutes / failures, 2)
