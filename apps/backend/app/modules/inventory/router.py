from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_permission
from app.modules.inventory.schema import (
    InventoryAlertResponse,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    SparePartCreate,
    SparePartResponse,
    SparePartUpdate,
    StockMovementResponse,
    SupplierCreate,
    SupplierResponse,
)
from app.modules.inventory.service import InventoryService

inventory_router = APIRouter()


@inventory_router.get("/spare-parts", response_model=List[SparePartResponse])
async def list_spare_parts(
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    critical_stock: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[SparePartResponse]:
    service = InventoryService(db)
    spare_parts, _ = await service.list_spare_parts(
        current_user,
        category=category,
        location=location,
        critical_stock=critical_stock,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [SparePartResponse.from_orm(item) for item in spare_parts]


@inventory_router.post(
    "/spare-parts",
    response_model=SparePartResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("inventory:write"))],
)
async def create_spare_part(
    payload: SparePartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SparePartResponse:
    service = InventoryService(db)
    return await service.create_spare_part(current_user, payload)


@inventory_router.get("/spare-parts/{spare_part_id}", response_model=SparePartResponse)
async def get_spare_part(
    spare_part_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SparePartResponse:
    service = InventoryService(db)
    spare_part = await service.get_spare_part(current_user, spare_part_id)
    return SparePartResponse.from_orm(spare_part)


@inventory_router.put(
    "/spare-parts/{spare_part_id}",
    response_model=SparePartResponse,
    dependencies=[Depends(require_permission("inventory:write"))],
)
async def update_spare_part(
    spare_part_id: UUID,
    payload: SparePartUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SparePartResponse:
    service = InventoryService(db)
    return await service.update_spare_part(current_user, spare_part_id, payload)


@inventory_router.delete(
    "/spare-parts/{spare_part_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("inventory:write"))],
)
async def delete_spare_part(
    spare_part_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = InventoryService(db)
    await service.delete_spare_part(current_user, spare_part_id)


@inventory_router.get("/stock-movements", response_model=List[StockMovementResponse])
async def list_stock_movements(
    spare_part_id: Optional[UUID] = Query(None),
    movement_type: Optional[str] = Query(None),
    reference: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[StockMovementResponse]:
    service = InventoryService(db)
    stock_movements, _ = await service.list_stock_movements(
        current_user,
        spare_part_id=spare_part_id,
        movement_type=movement_type,
        reference=reference,
        limit=limit,
        offset=offset,
    )
    return [StockMovementResponse.from_orm(item) for item in stock_movements]


@inventory_router.get("/suppliers", response_model=List[SupplierResponse])
async def list_suppliers(
    search: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[SupplierResponse]:
    service = InventoryService(db)
    suppliers, _ = await service.list_suppliers(
        current_user,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [SupplierResponse.from_orm(item) for item in suppliers]


@inventory_router.post(
    "/suppliers",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("inventory:write"))],
)
async def create_supplier(
    payload: SupplierCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    service = InventoryService(db)
    return await service.create_supplier(current_user, payload)


@inventory_router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    supplier_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[PurchaseOrderResponse]:
    service = InventoryService(db)
    orders, _ = await service.list_purchase_orders(
        current_user,
        supplier_id=supplier_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return [PurchaseOrderResponse.from_orm(item) for item in orders]


@inventory_router.post(
    "/purchase-orders",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("inventory:write"))],
)
async def create_purchase_order(
    payload: PurchaseOrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PurchaseOrderResponse:
    service = InventoryService(db)
    return await service.create_purchase_order(current_user, payload)


@inventory_router.get("/inventory-alerts", response_model=List[InventoryAlertResponse])
async def list_inventory_alerts(
    spare_part_id: Optional[UUID] = Query(None),
    is_read: Optional[bool] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[InventoryAlertResponse]:
    service = InventoryService(db)
    alerts, _ = await service.list_inventory_alerts(
        current_user,
        spare_part_id=spare_part_id,
        is_read=is_read,
        limit=limit,
        offset=offset,
    )
    return [InventoryAlertResponse.from_orm(item) for item in alerts]
