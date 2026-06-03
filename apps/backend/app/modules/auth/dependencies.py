from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.modules.auth.repository import AuthRepository
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(token, token_type="access")
    user_id = payload.get("sub")
    company_id = payload.get("company_id")

    if not user_id or not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await AuthRepository(db).get_user_by_id(str(user_id))
    if not user or str(user.company_id) != str(company_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or does not belong to the requested tenant.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )

    return user


def require_permission(permission_name: str):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:
            return user

        for role in user.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission_name}' required.",
        )

    return dependency


def require_role(role_name: str):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:
            return user

        for role in user.roles:
            if role.name == role_name:
                return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role_name}' required.",
        )

    return dependency
