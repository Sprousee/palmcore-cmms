from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.area import Area
from app.models.equipment import Equipment
from app.models.equipment_category import EquipmentCategory
from app.models.equipment_history import EquipmentHistory
from app.models.plant import Plant


class EquipmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_equipment_query(self, company_id: UUID):
        return select(Equipment).filter(
            Equipment.company_id == company_id,
            Equipment.deleted_at.is_(None),
        ).options(
            selectinload(Equipment.plant),
            selectinload(Equipment.area),
            selectinload(Equipment.category),
        )

    async def get_equipment_list(
        self,
        company_id: UUID,
        search: Optional[str] = None,
        plant_id: Optional[UUID] = None,
        area_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        status: Optional[str] = None,
        criticality: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[list[Equipment], int]:
        query = self.get_equipment_query(company_id)

        if search:
            term = f"%{search}%"
            query = query.filter(
                Equipment.code.ilike(term)
                | Equipment.name.ilike(term)
                | Equipment.brand.ilike(term)
                | Equipment.model.ilike(term)
                | Equipment.serial_number.ilike(term)
            )

        if plant_id:
            query = query.filter(Equipment.plant_id == plant_id)
        if area_id:
            query = query.filter(Equipment.area_id == area_id)
        if category_id:
            query = query.filter(Equipment.category_id == category_id)
        if status:
            query = query.filter(Equipment.status == status)
        if criticality:
            query = query.filter(Equipment.criticality == criticality)

        total_stmt = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar_one()

        result = await self.session.execute(query.limit(limit).offset(offset))
        return result.scalars().all(), total

    async def get_equipment_by_id(self, equipment_id: UUID, company_id: UUID) -> Optional[Equipment]:
        statement = (
            select(Equipment)
            .filter(
                Equipment.id == equipment_id,
                Equipment.company_id == company_id,
                Equipment.deleted_at.is_(None),
            )
            .options(
                selectinload(Equipment.plant),
                selectinload(Equipment.area),
                selectinload(Equipment.category),
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create_equipment(self, equipment: Equipment) -> Equipment:
        self.session.add(equipment)
        await self.session.flush()
        return equipment

    async def update_equipment(self, equipment: Equipment) -> Equipment:
        self.session.add(equipment)
        await self.session.flush()
        return equipment

    async def delete_equipment(self, equipment: Equipment) -> None:
        equipment.deleted_at = datetime.utcnow()
        self.session.add(equipment)
        await self.session.flush()

    async def get_plants(self, company_id: UUID) -> list[Plant]:
        statement = select(Plant).filter(Plant.company_id == company_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create_plant(self, plant: Plant) -> Plant:
        self.session.add(plant)
        await self.session.flush()
        return plant

    async def get_plant_by_id(self, plant_id: UUID, company_id: UUID) -> Optional[Plant]:
        statement = select(Plant).filter(
            Plant.id == plant_id,
            Plant.company_id == company_id,
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_area_by_id(self, area_id: UUID, company_id: UUID) -> Optional[Area]:
        statement = (
            select(Area)
            .join(Plant)
            .filter(
                Area.id == area_id,
                Plant.company_id == company_id,
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_areas(self, company_id: UUID) -> list[Area]:
        statement = (
            select(Area)
            .join(Plant)
            .filter(Plant.company_id == company_id)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create_area(self, area: Area) -> Area:
        self.session.add(area)
        await self.session.flush()
        return area

    async def get_category_by_id(self, category_id: UUID, company_id: UUID) -> Optional[EquipmentCategory]:
        statement = select(EquipmentCategory).filter(
            EquipmentCategory.id == category_id,
            EquipmentCategory.company_id == company_id,
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_categories(self, company_id: UUID) -> list[EquipmentCategory]:
        statement = select(EquipmentCategory).filter(EquipmentCategory.company_id == company_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create_category(self, category: EquipmentCategory) -> EquipmentCategory:
        self.session.add(category)
        await self.session.flush()
        return category

    async def create_history(self, history: EquipmentHistory) -> EquipmentHistory:
        self.session.add(history)
        await self.session.flush()
        return history
