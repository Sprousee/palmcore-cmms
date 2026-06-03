from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MaintenancePlanBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: Optional[UUID]
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str]
    maintenance_type: Optional[str] = Field(None, max_length=64)
    frequency_type: str = Field(..., min_length=2, max_length=64)
    frequency_value: int = Field(..., ge=1)
    estimated_duration: Optional[int] = Field(None, ge=1)
    priority: Optional[str] = Field(None, max_length=64)
    auto_generate_work_order: bool = False
    is_active: bool = True


class MaintenancePlanCreate(MaintenancePlanBase):
    pass


class MaintenancePlanUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: Optional[UUID]
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str]
    maintenance_type: Optional[str] = Field(None, max_length=64)
    frequency_type: Optional[str] = Field(None, min_length=2, max_length=64)
    frequency_value: Optional[int] = Field(None, ge=1)
    estimated_duration: Optional[int] = Field(None, ge=1)
    priority: Optional[str] = Field(None, max_length=64)
    auto_generate_work_order: Optional[bool]
    is_active: Optional[bool]


class MaintenancePlanResponse(MaintenancePlanBase):
    id: UUID
    company_id: UUID
    created_by: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class HourmeterCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: UUID
    current_hours: int = Field(..., ge=0)
    last_recorded_hours: Optional[int] = Field(None, ge=0)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    recorded_by: Optional[UUID]


class HourmeterResponse(HourmeterCreate):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    maintenance_plan_id: UUID
    scheduled_date: date
    scheduled_hours: Optional[int]
    status: Optional[str]
    generated_work_order_id: Optional[UUID]
    created_at: Optional[datetime]


class BacklogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    equipment_id: Optional[UUID]
    maintenance_plan_id: Optional[UUID]
    scheduled_date: Optional[date]
    days_overdue: Optional[int]
    priority: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]
