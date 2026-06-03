from datetime import date
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.inventory_alert import InventoryAlert
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.spare_part import SparePart
from app.models.stock_movement import StockMovement
from app.models.supplier import Supplier


class InventoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_spare_part_query(self, company_id: UUID):
        return select(SparePart).filter(
            SparePart.company_id == company_id,
            SparePart.deleted_at.is_(None),
        )

    async def get_spare_parts(
        self,
        company_id: UUID,
        category: Optional[str] = None,
        location: Optional[str] = None,
        critical_stock: Optional[bool] = None,
        supplier_id: Optional[UUID] = None,
        movement_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[SparePart], int]:
        query = self.get_spare_part_query(company_id)

        if category:
            query = query.filter(SparePart.category == category)
        if location:
            query = query.filter(SparePart.location == location)
        if critical_stock is not None and critical_stock:
            query = query.filter(SparePart.current_stock <= SparePart.minimum_stock)
        if search:
            term = f"%{search}%"
            query = query.filter(
                SparePart.name.ilike(term)
                | SparePart.part_number.ilike(term)
                | SparePart.brand.ilike(term)
                | SparePart.category.ilike(term)
            )

        total = (await self.session.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
        result = await self.session.execute(query.limit(limit).offset(offset))
        return result.scalars().all(), total

    async def get_spare_part_by_id(self, spare_part_id: UUID, company_id: UUID) -> Optional[SparePart]:
        statement = (
            select(SparePart)
            .filter(
                SparePart.id == spare_part_id,
                SparePart.company_id == company_id,
                SparePart.deleted_at.is_(None),
            )
            .options(joinedload(SparePart.stock_movements), joinedload(SparePart.alerts))
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create_spare_part(self, spare_part: SparePart) -> SparePart:
        self.session.add(spare_part)
        await self.session.flush()
        return spare_part

    async def update_spare_part(self, spare_part: SparePart) -> SparePart:
        self.session.add(spare_part)
        await self.session.flush()
        return spare_part

    async def delete_spare_part(self, spare_part: SparePart) -> None:
        spare_part.deleted_at = func.now()
        self.session.add(spare_part)
        await self.session.flush()

    async def get_stock_movements(
        self,
        company_id: UUID,
        spare_part_id: Optional[UUID] = None,
        movement_type: Optional[str] = None,
        reference: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[StockMovement], int]:
        query = select(StockMovement).filter(
            StockMovement.company_id == company_id,
            StockMovement.deleted_at.is_(None),
        )

        if spare_part_id:
            query = query.filter(StockMovement.spare_part_id == spare_part_id)
        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)
        if reference:
            term = f"%{reference}%"
            query = query.filter(StockMovement.reference.ilike(term))

        total = (await self.session.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
        result = await self.session.execute(query.order_by(StockMovement.created_at.desc()).limit(limit).offset(offset))
        return result.scalars().all(), total

    async def create_stock_movement(self, movement: StockMovement) -> StockMovement:
        self.session.add(movement)
        await self.session.flush()
        return movement

    async def get_suppliers(
        self,
        company_id: UUID,
        search: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[Supplier], int]:
        query = select(Supplier).filter(
            Supplier.company_id == company_id,
            Supplier.deleted_at.is_(None),
        )

        if search:
            term = f"%{search}%"
            query = query.filter(Supplier.name.ilike(term) | Supplier.nit.ilike(term))

        total = (await self.session.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
        result = await self.session.execute(query.limit(limit).offset(offset))
        return result.scalars().all(), total

    async def get_supplier_by_id(self, supplier_id: UUID, company_id: UUID) -> Optional[Supplier]:
        statement = select(Supplier).filter(
            Supplier.id == supplier_id,
            Supplier.company_id == company_id,
            Supplier.deleted_at.is_(None),
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create_supplier(self, supplier: Supplier) -> Supplier:
        self.session.add(supplier)
        await self.session.flush()
        return supplier

    async def get_purchase_orders(
        self,
        company_id: UUID,
        supplier_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[PurchaseOrder], int]:
        query = select(PurchaseOrder).filter(
            PurchaseOrder.company_id == company_id,
            PurchaseOrder.deleted_at.is_(None),
        )

        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)
        if status:
            query = query.filter(PurchaseOrder.status == status)

        total = (await self.session.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
        result = await self.session.execute(query.order_by(PurchaseOrder.purchase_date.desc()).limit(limit).offset(offset))
        return result.scalars().all(), total

    async def create_purchase_order(self, order: PurchaseOrder) -> PurchaseOrder:
        self.session.add(order)
        await self.session.flush()
        return order

    async def create_purchase_order_item(self, item: PurchaseOrderItem) -> PurchaseOrderItem:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_inventory_alerts(
        self,
        company_id: UUID,
        spare_part_id: Optional[UUID] = None,
        is_read: Optional[bool] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[InventoryAlert], int]:
        query = select(InventoryAlert).filter(
            InventoryAlert.company_id == company_id,
            InventoryAlert.deleted_at.is_(None),
        )

        if spare_part_id:
            query = query.filter(InventoryAlert.spare_part_id == spare_part_id)
        if is_read is not None:
            query = query.filter(InventoryAlert.is_read == is_read)

        total = (await self.session.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
        result = await self.session.execute(query.order_by(InventoryAlert.created_at.desc()).limit(limit).offset(offset))
        return result.scalars().all(), total

    async def create_inventory_alert(self, alert: InventoryAlert) -> InventoryAlert:
        self.session.add(alert)
        await self.session.flush()
        return alert
