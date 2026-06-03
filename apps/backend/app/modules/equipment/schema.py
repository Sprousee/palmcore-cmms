from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EquipmentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plant_id: Optional[UUID]
    area_id: Optional[UUID]
    category_id: Optional[UUID]
    code: str = Field(..., min_length=2, max_length=128)
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    criticality: Optional[str]
    status: Optional[str]
    installation_date: Optional[date]
    photo_url: Optional[str]


class EquipmentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plant_id: Optional[UUID]
    area_id: Optional[UUID]
    category_id: Optional[UUID]
    code: Optional[str] = Field(None, min_length=2, max_length=128)
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    criticality: Optional[str]
    status: Optional[str]
    installation_date: Optional[date]
    photo_url: Optional[str]


class EquipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    plant_id: Optional[UUID]
    area_id: Optional[UUID]
    category_id: Optional[UUID]
    code: str
    name: str
    description: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    criticality: Optional[str]
    status: Optional[str]
    installation_date: Optional[date]
    qr_code: Optional[str]
    photo_url: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class PlantCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=2, max_length=255)
    city: Optional[str]
    department: Optional[str]
    address: Optional[str]


class PlantResponse(PlantCreate):
    id: UUID
    company_id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]


class AreaCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plant_id: UUID
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str]


class AreaResponse(AreaCreate):
    id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]


class EquipmentCategoryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]


class EquipmentCategoryResponse(EquipmentCategoryCreate):
    id: UUID
    company_id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]
