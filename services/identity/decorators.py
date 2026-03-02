"""
Decorators para verificação de permissões no sistema RBAC.

Este módulo fornece decorators que podem ser aplicados a rotas FastAPI
para verificar automaticamente se o usuário tem as permissões necessárias.
"""

from functools import wraps
from typing import List, Optional, Callable
from uuid import UUID
from fastapi import HTTPException

from services.identity.permission_service import PermissionService
from services.identity.models import User


def require_permission(permission: str, project_id_param: Optional[str] = None):
    """Decorator para verificar permissão antes de executar função.

    Args:
        permission: Permissão necessária (ex: 'project.create')
        project_id_param: Nome do parâmetro que contém o project_id (opcional)

    Usage:
        @require_permission("project.create")
        async def create_project(...):
            pass

        @require_permission("workitem.update", project_id_param="project_id")
        async def update_work_item(project_id: UUID, ...):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair dependências dos kwargs
            current_user = kwargs.get("current_user")
            session = kwargs.get("session")

            if not current_user:
                raise HTTPException(
                    status_code=401, detail="Authentication required"
                )

            if not session:
                raise HTTPException(
                    status_code=500, detail="Database session not available"
                )

            # Extrair project_id se especificado
            project_id = None
            if project_id_param:
                project_id = kwargs.get(project_id_param)
                if isinstance(project_id, str):
                    try:
                        project_id = UUID(project_id)
                    except ValueError:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid project_id format: {project_id}",
                        )

            # Verificar permissão
            has_permission = await PermissionService.check_permission(
                user=current_user,
                permission=permission,
                project_id=project_id,
                session=session,
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403, detail=f"Permission denied: {permission}"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_any_permission(
    permissions: List[str], project_id_param: Optional[str] = None
):
    """Decorator para verificar se usuário tem pelo menos uma das permissões.

    Args:
        permissions: Lista de permissões (usuário precisa ter pelo menos uma)
        project_id_param: Nome do parâmetro que contém o project_id (opcional)

    Usage:
        @require_any_permission(["project.read", "project.update"])
        async def get_project(...):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair dependências dos kwargs
            current_user = kwargs.get("current_user")
            session = kwargs.get("session")

            if not current_user:
                raise HTTPException(
                    status_code=401, detail="Authentication required"
                )

            if not session:
                raise HTTPException(
                    status_code=500, detail="Database session not available"
                )

            # Extrair project_id se especificado
            project_id = None
            if project_id_param:
                project_id = kwargs.get(project_id_param)
                if isinstance(project_id, str):
                    try:
                        project_id = UUID(project_id)
                    except ValueError:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid project_id format: {project_id}",
                        )

            # Verificar se tem pelo menos uma permissão
            has_permission = await PermissionService.check_any_permission(
                user=current_user,
                permissions=permissions,
                project_id=project_id,
                session=session,
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: requires one of {permissions}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_all_permissions(
    permissions: List[str], project_id_param: Optional[str] = None
):
    """Decorator para verificar se usuário tem todas as permissões.

    Args:
        permissions: Lista de permissões (usuário precisa ter todas)
        project_id_param: Nome do parâmetro que contém o project_id (opcional)

    Usage:
        @require_all_permissions(["project.read", "workitem.create"])
        async def create_work_item_in_project(...):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair dependências dos kwargs
            current_user = kwargs.get("current_user")
            session = kwargs.get("session")

            if not current_user:
                raise HTTPException(
                    status_code=401, detail="Authentication required"
                )

            if not session:
                raise HTTPException(
                    status_code=500, detail="Database session not available"
                )

            # Extrair project_id se especificado
            project_id = None
            if project_id_param:
                project_id = kwargs.get(project_id_param)
                if isinstance(project_id, str):
                    try:
                        project_id = UUID(project_id)
                    except ValueError:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid project_id format: {project_id}",
                        )

            # Verificar se tem todas as permissões
            has_permission = await PermissionService.check_all_permissions(
                user=current_user,
                permissions=permissions,
                project_id=project_id,
                session=session,
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: requires all of {permissions}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_super_admin():
    """Decorator para verificar se usuário é super admin.

    Usage:
        @require_super_admin()
        async def create_tenant(...):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair current_user dos kwargs
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=401, detail="Authentication required"
                )

            # Verificar se é super admin (campo correto é is_superuser)
            if not getattr(current_user, "is_superuser", False):
                raise HTTPException(
                    status_code=403, detail="Super admin access required"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_tenant_access(tenant_id_param: str = "tenant_id"):
    """Decorator para verificar se usuário tem acesso ao tenant.

    Args:
        tenant_id_param: Nome do parâmetro que contém o tenant_id

    Usage:
        @require_tenant_access("tenant_id")
        async def get_tenant_data(tenant_id: UUID, ...):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair dependências dos kwargs
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=401, detail="Authentication required"
                )

            # Super admin tem acesso a todos os tenants (campo correto é is_superuser)
            if getattr(current_user, "is_superuser", False):
                return await func(*args, **kwargs)

            # Extrair tenant_id do parâmetro
            tenant_id = kwargs.get(tenant_id_param)
            if isinstance(tenant_id, str):
                try:
                    tenant_id = UUID(tenant_id)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid tenant_id format: {tenant_id}",
                    )

            # Verificar se o tenant_id do usuário corresponde
            if current_user.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: different tenant",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
