from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.equipment.repository import EquipmentRepository
from app.modules.equipment.schema import (
    AreaCreate,
    EquipmentCreate,
    EquipmentResponse,
    EquipmentUpdate,
    EquipmentCategoryCreate,
    PlantCreate,
)
from app.modules.equipment.utils import generate_equipment_qr_code
from app.models.area import Area
from app.models.equipment import Equipment
from app.models.equipment_category import EquipmentCategory
from app.models.equipment_history import EquipmentHistory
from app.models.plant import Plant
from app.models.user import User


class EquipmentService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = EquipmentRepository(db)
        self.db = db

    async def list_equipment(
        self,
        user: User,
        search: Optional[str] = None,
        plant_id: Optional[UUID] = None,
        area_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        status: Optional[str] = None,
        criticality: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ):
        return await self.repo.get_equipment_list(
            user.company_id,
            search=search,
            plant_id=plant_id,
            area_id=area_id,
            category_id=category_id,
            status=status,
            criticality=criticality,
            limit=limit,
            offset=offset,
        )

    async def get_equipment(self, user: User, equipment_id: UUID) -> Equipment:
        equipment = await self.repo.get_equipment_by_id(equipment_id, user.company_id)
        if not equipment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")
        return equipment

    async def create_equipment(self, user: User, payload: EquipmentCreate) -> EquipmentResponse:
        plant = None
        if payload.plant_id:
            plant = await self.repo.get_plant_by_id(payload.plant_id, user.company_id)
            if not plant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found.")

        category = None
        if payload.category_id:
            category = await self.repo.get_category_by_id(payload.category_id, user.company_id)
            if not category:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

        area = None
        if payload.area_id:
            area = await self.repo.get_area_by_id(payload.area_id, user.company_id)
            if not area:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found.")

        if plant and area and area.plant_id != plant.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The selected area does not belong to the selected plant.",
            )

        equipment = Equipment(
            company_id=user.company_id,
            plant_id=payload.plant_id,
            area_id=payload.area_id,
            category_id=payload.category_id,
            code=payload.code,
            name=payload.name,
            description=payload.description,
            brand=payload.brand,
            model=payload.model,
            serial_number=payload.serial_number,
            criticality=payload.criticality,
            status=payload.status,
            installation_date=payload.installation_date,
            photo_url=payload.photo_url,
        )
        await self.repo.create_equipment(equipment)
        equipment.qr_code = generate_equipment_qr_code(equipment.id)
        await self.repo.update_equipment(equipment)

        await self.repo.create_history(
            EquipmentHistory(
                equipment_id=equipment.id,
                action="Equipment created",
                description=f"Equipment '{equipment.name}' was created.",
                performed_by=user.email,
            )
        )
        await self.db.commit()
        return EquipmentResponse.from_orm(equipment)

    async def update_equipment(self, user: User, equipment_id: UUID, payload: EquipmentUpdate) -> EquipmentResponse:
        equipment = await self.get_equipment(user, equipment_id)
        changes = []

        for field, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(equipment, field):
                old_value = getattr(equipment, field)
                setattr(equipment, field, value)
                if value != old_value:
                    changes.append(f"{field} changed from '{old_value}' to '{value}'")

        if not changes:
            return EquipmentResponse.from_orm(equipment)

        await self.repo.update_equipment(equipment)
        await self.repo.create_history(
            EquipmentHistory(
                equipment_id=equipment.id,
                action="Equipment updated",
                description="; ".join(changes),
                performed_by=user.email,
            )
        )
        await self.db.commit()
        return EquipmentResponse.from_orm(equipment)

    async def delete_equipment(self, user: User, equipment_id: UUID) -> None:
        equipment = await self.get_equipment(user, equipment_id)
        await self.repo.delete_equipment(equipment)
        await self.repo.create_history(
            EquipmentHistory(
                equipment_id=equipment.id,
                action="Equipment deleted",
                description=f"Equipment '{equipment.name}' was soft deleted.",
                performed_by=user.email,
            )
        )
        await self.db.commit()

    async def list_plants(self, user: User) -> list[Plant]:
        return await self.repo.get_plants(user.company_id)

    async def create_plant(self, user: User, payload: PlantCreate) -> Plant:
        plant = Plant(
            company_id=user.company_id,
            name=payload.name,
            city=payload.city,
            department=payload.department,
            address=payload.address,
        )
        await self.repo.create_plant(plant)
        await self.db.commit()
        return plant

    async def list_areas(self, user: User) -> list[Area]:
        return await self.repo.get_areas(user.company_id)

    async def create_area(self, user: User, payload: AreaCreate) -> Area:
        plant = await self.repo.get_plant_by_id(payload.plant_id, user.company_id)
        if not plant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found.")

        area = Area(
            plant_id=payload.plant_id,
            name=payload.name,
            description=payload.description,
        )
        await self.repo.create_area(area)
        await self.db.commit()
        return area

    async def list_categories(self, user: User) -> list[EquipmentCategory]:
        return await self.repo.get_categories(user.company_id)

    async def create_category(self, user: User, payload: EquipmentCategoryCreate) -> EquipmentCategory:
        category = EquipmentCategory(
            company_id=user.company_id,
            name=payload.name,
            description=payload.description,
            color=payload.color,
            icon=payload.icon,
        )
        await self.repo.create_category(category)
        await self.db.commit()
        return category
