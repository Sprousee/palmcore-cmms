from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.company import Company
from app.models.user import User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schema import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = AuthRepository(db)
        self.db = db

    async def authenticate_user(
        self, email: str, password: str, company_id: str | None = None
    ) -> User:
        user = await self.repo.get_user_by_email(email=email, company_id=company_id)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        return user

    def _build_role_claims(self, user: User) -> tuple[list[str], list[str]]:
        roles = [role.name for role in user.roles]
        permissions = sorted(
            {permission.name for role in user.roles for permission in role.permissions}
        )
        return roles, permissions

    async def login(
        self, email: str, password: str, company_id: str | None = None
    ) -> TokenResponse:
        user = await self.authenticate_user(email, password, company_id)
        roles, permissions = self._build_role_claims(user)

        access_token = create_access_token(
            str(user.id), str(user.company_id), roles=roles, permissions=permissions
        )
        refresh_token = create_refresh_token(str(user.id), str(user.company_id))
        expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        await self.repo.create_refresh_token(refresh_token, str(user.id), expires_at)
        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        token_record = await self.repo.get_refresh_token(refresh_token)
        if not token_record or token_record.is_revoked or token_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or expired.",
            )

        user = await self.repo.get_user_by_id(str(token_record.user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User session is not valid.",
            )

        await self.repo.revoke_refresh_token(token_record)
        roles, permissions = self._build_role_claims(user)

        access_token = create_access_token(
            str(user.id), str(user.company_id), roles=roles, permissions=permissions
        )
        new_refresh_token = create_refresh_token(str(user.id), str(user.company_id))
        expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        await self.repo.create_refresh_token(new_refresh_token, str(user.id), expires_at)
        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    async def logout(self, refresh_token: str) -> None:
        token_record = await self.repo.get_refresh_token(refresh_token)
        if not token_record or token_record.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh token not found.",
            )

        await self.repo.revoke_refresh_token(token_record)
        await self.db.commit()

    async def register_user(self, payload: RegisterUserRequest) -> UserResponse:
        company = None
        if payload.company_id:
            company = await self.repo.get_company_by_id(str(payload.company_id))
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found.",
                )
        elif payload.company_name:
            company = await self.repo.get_company_by_name(payload.company_name)
            if not company:
                company = await self.repo.create_company(payload.company_name)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company ID or company name is required.",
            )

        existing_user = await self.repo.get_user_by_email(payload.email, str(company.id))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists for the selected company.",
            )

        password_hash = hash_password(payload.password)
        user = await self.repo.create_user(
            email=payload.email,
            password_hash=password_hash,
            company_id=str(company.id),
            is_superuser=payload.is_superuser or False,
        )
        await self.db.commit()
        return UserResponse.from_orm(user)
