from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.dependencies import get_current_user
from app.modules.equipment.schema import (
    AreaCreate,
    AreaResponse,
    EquipmentCreate,
    EquipmentResponse,
    EquipmentUpdate,
    EquipmentCategoryCreate,
    EquipmentCategoryResponse,
    PlantCreate,
    PlantResponse,
)
from app.modules.equipment.service import EquipmentService
from app.models.user import User


equipment_router = APIRouter()


@equipment_router.get("/equipment", response_model=list[EquipmentResponse])
async def list_equipment(
    search: str | None = Query(None, description="Search equipment by name, code or serial."),
    plant_id: UUID | None = Query(None),
    area_id: UUID | None = Query(None),
    category_id: UUID | None = Query(None),
    status: str | None = Query(None),
    criticality: str | None = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[EquipmentResponse]:
    service = EquipmentService(db)
    equipment, _ = await service.list_equipment(
        current_user,
        search=search,
        plant_id=plant_id,
        area_id=area_id,
        category_id=category_id,
        status=status,
        criticality=criticality,
        limit=limit,
        offset=offset,
    )
    return [EquipmentResponse.from_orm(item) for item in equipment]


@equipment_router.post(
    "/equipment",
    response_model=EquipmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("equipment:write"))],
)
async def create_equipment(
    payload: EquipmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EquipmentResponse:
    service = EquipmentService(db)
    return await service.create_equipment(current_user, payload)


@equipment_router.get("/equipment/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EquipmentResponse:
    service = EquipmentService(db)
    equipment = await service.get_equipment(current_user, equipment_id)
    return EquipmentResponse.from_orm(equipment)


@equipment_router.put(
    "/equipment/{equipment_id}",
    response_model=EquipmentResponse,
    dependencies=[Depends(require_permission("equipment:write"))],
)
async def update_equipment(
    equipment_id: UUID,
    payload: EquipmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EquipmentResponse:
    service = EquipmentService(db)
    return await service.update_equipment(current_user, equipment_id, payload)


@equipment_router.delete(
    "/equipment/{equipment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("equipment:write"))],
)
async def delete_equipment(
    equipment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = EquipmentService(db)
    await service.delete_equipment(current_user, equipment_id)


@equipment_router.get("/plants", response_model=list[PlantResponse])
async def list_plants(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PlantResponse]:
    service = EquipmentService(db)
    plants = await service.list_plants(current_user)
    return [PlantResponse.model_validate(p) for p in plants]


@equipment_router.post(
    "/plants",
    response_model=PlantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("equipment:write"))],
)
async def create_plant(
    payload: PlantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlantResponse:
    service = EquipmentService(db)
    plant = await service.create_plant(current_user, payload)
    return PlantResponse.model_validate(plant)


@equipment_router.get("/areas", response_model=list[AreaResponse])
async def list_areas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AreaResponse]:
    service = EquipmentService(db)
    areas = await service.list_areas(current_user)
    return [AreaResponse.model_validate(area) for area in areas]


@equipment_router.post(
    "/areas",
    response_model=AreaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("equipment:write"))],
)
async def create_area(
    payload: AreaCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AreaResponse:
    service = EquipmentService(db)
    area = await service.create_area(current_user, payload)
    return AreaResponse.model_validate(area)


@equipment_router.get("/categories", response_model=list[EquipmentCategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[EquipmentCategoryResponse]:
    service = EquipmentService(db)
    categories = await service.list_categories(current_user)
    return [EquipmentCategoryResponse.model_validate(category) for category in categories]


@equipment_router.post(
    "/categories",
    response_model=EquipmentCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("equipment:write"))],
)
async def create_category(
    payload: EquipmentCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EquipmentCategoryResponse:
    service = EquipmentService(db)
    category = await service.create_category(current_user, payload)
    return EquipmentCategoryResponse.model_validate(category)
