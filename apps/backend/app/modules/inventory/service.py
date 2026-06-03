from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.alerts import build_stock_alert, should_create_stock_alert
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schema import (
    BacklogResponse,
    InventoryAlertResponse,
    PurchaseOrderCreate,
    PurchaseOrderItemCreate,
    PurchaseOrderResponse,
    PurchaseOrderItemResponse,
    SparePartCreate,
    SparePartResponse,
    SparePartUpdate,
    StockMovementResponse,
    SupplierCreate,
    SupplierResponse,
)
from app.modules.inventory.utils import calculate_total_cost
from app.models.inventory_alert import InventoryAlert
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.spare_part import SparePart
from app.models.stock_movement import StockMovement
from app.models.supplier import Supplier
from app.models.user import User


class InventoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = InventoryRepository(db)
        self.db = db

    async def list_spare_parts(
        self,
        user: User,
        category: Optional[str] = None,
        critical_stock: Optional[bool] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[List[SparePart], int]:
        return await self.repo.get_spare_parts(
            user.company_id,
            category=category,
            location=location,
            critical_stock=critical_stock,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def get_spare_part(self, user: User, spare_part_id: UUID) -> SparePart:
        spare_part = await self.repo.get_spare_part_by_id(spare_part_id, user.company_id)
        if not spare_part:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spare part not found.")
        return spare_part

    async def create_spare_part(self, user: User, payload: SparePartCreate) -> SparePartResponse:
        spare_part = SparePart(
            company_id=user.company_id,
            part_number=payload.part_number,
            name=payload.name,
            description=payload.description,
            brand=payload.brand,
            category=payload.category,
            unit_measure=payload.unit_measure,
            minimum_stock=payload.minimum_stock,
            maximum_stock=payload.maximum_stock,
            current_stock=payload.current_stock,
            unit_cost=payload.unit_cost,
            location=payload.location,
            barcode=payload.barcode,
            qr_code=payload.qr_code,
            status=payload.status,
        )
        await self.repo.create_spare_part(spare_part)
        await self.db.commit()
        return SparePartResponse.from_orm(spare_part)

    async def update_spare_part(
        self, user: User, spare_part_id: UUID, payload: SparePartUpdate
    ) -> SparePartResponse:
        spare_part = await self.get_spare_part(user, spare_part_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(spare_part, field, value)
        await self.repo.update_spare_part(spare_part)
        await self.db.commit()
        return SparePartResponse.from_orm(spare_part)

    async def delete_spare_part(self, user: User, spare_part_id: UUID) -> None:
        spare_part = await self.get_spare_part(user, spare_part_id)
        await self.repo.delete_spare_part(spare_part)
        await self.db.commit()

    async def list_stock_movements(
        self,
        user: User,
        spare_part_id: Optional[UUID] = None,
        movement_type: Optional[str] = None,
        reference: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[List[StockMovement], int]:
        return await self.repo.get_stock_movements(
            user.company_id,
            spare_part_id=spare_part_id,
            movement_type=movement_type,
            reference=reference,
            limit=limit,
            offset=offset,
        )

    async def list_suppliers(
        self,
        user: User,
        search: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[List[Supplier], int]:
        return await self.repo.get_suppliers(
            user.company_id,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def create_supplier(self, user: User, payload: SupplierCreate) -> SupplierResponse:
        supplier = Supplier(
            company_id=user.company_id,
            name=payload.name,
            nit=payload.nit,
            phone=payload.phone,
            email=payload.email,
            address=payload.address,
            contact_person=payload.contact_person,
            status=payload.status,
        )
        await self.repo.create_supplier(supplier)
        await self.db.commit()
        return SupplierResponse.from_orm(supplier)

    async def list_purchase_orders(
        self,
        user: User,
        supplier_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[List[PurchaseOrder], int]:
        return await self.repo.get_purchase_orders(
            user.company_id,
            supplier_id=supplier_id,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def create_purchase_order(
        self, user: User, payload: PurchaseOrderCreate
    ) -> PurchaseOrderResponse:
        supplier = await self.repo.get_supplier_by_id(payload.supplier_id, user.company_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found.")

        purchase_order = PurchaseOrder(
            company_id=user.company_id,
            supplier_id=payload.supplier_id,
            purchase_number=payload.purchase_number,
            status=payload.status,
            subtotal=payload.subtotal,
            taxes=payload.taxes,
            total=payload.total,
            purchase_date=payload.purchase_date,
            expected_delivery=payload.expected_delivery,
            created_by=payload.created_by or user.id,
        )
        await self.repo.create_purchase_order(purchase_order)

        items: List[PurchaseOrderItemResponse] = []
        for item_payload in payload.items:
            item = PurchaseOrderItem(
                purchase_order_id=purchase_order.id,
                spare_part_id=item_payload.spare_part_id,
                quantity=item_payload.quantity,
                unit_cost=item_payload.unit_cost,
                total_cost=item_payload.total_cost,
            )
            await self.repo.create_purchase_order_item(item)
            items.append(PurchaseOrderItemResponse.model_validate(item))

        await self.db.commit()
        response = PurchaseOrderResponse.from_orm(purchase_order)
        response.items = items
        return response

    async def list_inventory_alerts(
        self,
        user: User,
        spare_part_id: Optional[UUID] = None,
        is_read: Optional[bool] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[List[InventoryAlert], int]:
        return await self.repo.get_inventory_alerts(
            user.company_id,
            spare_part_id=spare_part_id,
            is_read=is_read,
            limit=limit,
            offset=offset,
        )

    async def consume_spare_part_for_work_order(
        self,
        user: User,
        spare_part_id: UUID,
        work_order_id: Optional[UUID],
        quantity: int,
        reference: Optional[str] = None,
        performed_by: Optional[UUID] = None,
    ) -> StockMovementResponse:
        spare_part = await self.get_spare_part(user, spare_part_id)
        if quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than zero.")
        if spare_part.current_stock < quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock for spare part.")

        quantity_before = spare_part.current_stock
        spare_part.current_stock -= quantity
        spare_part.current_stock = int(max(0, spare_part.current_stock))
        await self.repo.update_spare_part(spare_part)

        unit_cost = spare_part.unit_cost or Decimal("0")
        total_cost = calculate_total_cost(quantity, unit_cost)
        movement = StockMovement(
            company_id=user.company_id,
            spare_part_id=spare_part.id,
            work_order_id=work_order_id,
            movement_type="out",
            quantity_before=quantity_before,
            quantity=quantity,
            quantity_after=spare_part.current_stock,
            reference=reference,
            unit_cost=unit_cost,
            total_cost=total_cost,
            performed_by=performed_by or user.id,
        )
        await self.repo.create_stock_movement(movement)

        if should_create_stock_alert(spare_part):
            alert = build_stock_alert(spare_part)
            await self.repo.create_inventory_alert(alert)

        await self.db.commit()
        return StockMovementResponse.from_orm(movement)
