from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.user import User


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_company_by_id(self, company_id: str) -> Optional[Company]:
        statement = select(Company).filter(Company.id == company_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_company_by_name(self, name: str) -> Optional[Company]:
        statement = select(Company).filter(Company.name == name)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create_company(self, name: str) -> Company:
        company = Company(name=name)
        self.session.add(company)
        await self.session.flush()
        return company

    async def get_user_by_email(
        self, email: str, company_id: Optional[str] = None
    ) -> Optional[User]:
        statement = select(User).filter(User.email == email)
        if company_id:
            statement = statement.filter(User.company_id == company_id)
        statement = statement.options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        statement = (
            select(User)
            .filter(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create_user(
        self,
        email: str,
        password_hash: str,
        company_id: str,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            company_id=company_id,
            is_superuser=is_superuser,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def create_refresh_token(
        self, token: str, user_id: str, expires_at: datetime
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        statement = select(RefreshToken).filter(RefreshToken.token == token)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def revoke_refresh_token(self, refresh_token: RefreshToken) -> None:
        refresh_token.is_revoked = True
        self.session.add(refresh_token)
        await self.session.flush()
