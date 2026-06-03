from app.modules.auth.dependencies import get_current_user, require_permission

__all__ = [
    "get_current_user",
    "require_permission",
]


def require_equipment_permission(permission_name: str):
    return require_permission(permission_name)
