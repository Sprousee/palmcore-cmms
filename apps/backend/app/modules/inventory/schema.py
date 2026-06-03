from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SparePartBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    part_number: str = Field(..., min_length=2, max_length=128)
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str]
    brand: Optional[str]
    category: Optional[str]
    unit_measure: Optional[str]
    minimum_stock: Optional[int] = Field(None, ge=0)
    maximum_stock: Optional[int] = Field(None, ge=0)
    current_stock: int = Field(0, ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    location: Optional[str]
    barcode: Optional[str]
    qr_code: Optional[str]
    status: Optional[str]


class SparePartCreate(SparePartBase):
    pass


class SparePartUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    part_number: Optional[str] = Field(None, min_length=2, max_length=128)
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str]
    brand: Optional[str]
    category: Optional[str]
    unit_measure: Optional[str]
    minimum_stock: Optional[int] = Field(None, ge=0)
    maximum_stock: Optional[int] = Field(None, ge=0)
    current_stock: Optional[int] = Field(None, ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    location: Optional[str]
    barcode: Optional[str]
    qr_code: Optional[str]
    status: Optional[str]


class SparePartResponse(SparePartBase):
    id: UUID
    company_id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    spare_part_id: UUID
    work_order_id: Optional[UUID]
    movement_type: str
    quantity_before: int
    quantity: int
    quantity_after: int
    reference: Optional[str]
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    performed_by: Optional[UUID]
    created_at: Optional[datetime]


class SupplierCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=2, max_length=255)
    nit: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    contact_person: Optional[str]
    status: Optional[str]


class SupplierResponse(SupplierCreate):
    id: UUID
    company_id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class PurchaseOrderItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    spare_part_id: UUID
    quantity: int = Field(..., ge=1)
    unit_cost: Decimal = Field(..., ge=0)
    total_cost: Decimal = Field(..., ge=0)


class PurchaseOrderItemResponse(PurchaseOrderItemCreate):
    id: UUID


class PurchaseOrderCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: UUID
    purchase_number: str = Field(..., min_length=2, max_length=128)
    status: Optional[str]
    subtotal: Optional[Decimal] = Field(None, ge=0)
    taxes: Optional[Decimal] = Field(None, ge=0)
    total: Optional[Decimal] = Field(None, ge=0)
    purchase_date: Optional[date]
    expected_delivery: Optional[date]
    created_by: Optional[UUID]
    items: List[PurchaseOrderItemCreate] = Field(default_factory=list)


class PurchaseOrderResponse(PurchaseOrderCreate):
    id: UUID
    company_id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    items: List[PurchaseOrderItemResponse]


class InventoryAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    spare_part_id: Optional[UUID]
    alert_type: str
    message: Optional[str]
    is_read: bool
    created_at: Optional[datetime]
