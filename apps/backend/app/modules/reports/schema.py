from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReportFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date_from: Optional[date]
    date_to: Optional[date]
    plant_id: Optional[UUID]
    equipment_id: Optional[UUID]
    technician_id: Optional[UUID]
    maintenance_type: Optional[str]


class KpiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mttr_minutes: float
    mtbf_minutes: float
    availability_percent: float
    maintenance_costs: float
    preventive_compliance_percent: float
    backlog_count: int
    reactive_work_orders: int
    preventive_work_orders: int


class MaintenanceCostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    parts_cost: float
    labor_cost: float
    total_cost: float


class BacklogStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Optional[str]
    count: int


class TechnicianProductivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    technician_id: Optional[UUID]
    technician_name: Optional[str]
    completed_work_orders: int
    average_duration_minutes: float
    total_cost: float


class InventoryConsumptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    spare_part_id: UUID
    spare_part_name: Optional[str]
    total_quantity: int
    total_cost: float


class TimeSeriesPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: str
    value: float


class FailureTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: Optional[UUID]
    equipment_name: Optional[str]
    failures: int


class CriticalEquipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: Optional[UUID]
    equipment_name: Optional[str]
    downtime_minutes: int
    work_order_count: int
