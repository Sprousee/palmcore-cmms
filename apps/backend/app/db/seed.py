from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.company import Company
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


def get_default_permissions() -> list[str]:
    return [
        "auth:login",
        "auth:register",
        "auth:refresh",
        "auth:users:read",
        "auth:users:write",
        "auth:roles:read",
        "auth:roles:write",
        "auth:permissions:read",
        "auth:permissions:write",
    ]


async def seed_database(session: AsyncSession) -> None:
    company_name = "PalmCore Holdings"
    admin_email = "admin@palmcore.local"
    admin_password = "Admin123!"

    statement = select(Company).filter(Company.name == company_name)
    result = await session.execute(statement)
    company = result.scalars().first()

    if not company:
        company = Company(name=company_name)
        session.add(company)
        await session.flush()

    permission_names = get_default_permissions()
    permissions = []
    for permission_name in permission_names:
        statement = select(Permission).filter(Permission.name == permission_name)
        result = await session.execute(statement)
        permission = result.scalars().first()
        if not permission:
            permission = Permission(name=permission_name, company_id=company.id)
            session.add(permission)
            await session.flush()
        permissions.append(permission)

    statement = select(Role).filter(Role.name == "SuperAdmin", Role.company_id == company.id)
    result = await session.execute(statement)
    super_role = result.scalars().first()
    if not super_role:
        super_role = Role(name="SuperAdmin", description="Super administrator role", company_id=company.id)
        super_role.permissions = permissions
        session.add(super_role)
        await session.flush()

    statement = select(User).filter(User.email == admin_email, User.company_id == company.id)
    result = await session.execute(statement)
    admin_user = result.scalars().first()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            password_hash=hash_password(admin_password),
            company_id=company.id,
            is_superuser=True,
        )
        admin_user.roles.append(super_role)
        session.add(admin_user)
        await session.flush()

    await session.commit()
