"""
Serviço de gerenciamento de permissões do sistema RBAC.

Este serviço é responsável por:
- Verificar se um usuário tem uma permissão específica
- Obter todas as permissões de um usuário
- Cache de permissões para performance
- Validação de permissões com contexto (projeto, tenant)
"""

from typing import List, Optional, Set
from uuid import UUID
from sqlmodel import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from cachetools import TTLCache
import fnmatch
from datetime import datetime

from services.identity.models import User, Role, UserRole


class PermissionService:
    """Serviço de gerenciamento de permissões."""

    # Cache de permissões por usuário (TTL de 5 minutos)
    _permission_cache = TTLCache(maxsize=1000, ttl=300)

    @classmethod
    def _get_cache_key(cls, user_id: UUID, project_id: Optional[UUID] = None) -> str:
        """Gera chave do cache para permissões do usuário."""
        if project_id:
            return f"permissions:{user_id}:{project_id}"
        return f"permissions:{user_id}:global"

    @classmethod
    def invalidate_user_permissions(cls, user_id: UUID):
        """Invalida cache de permissões do usuário."""
        # Remove todas as entradas do cache que começam com o user_id
        keys_to_remove = [
            key for key in cls._permission_cache.keys()
            if key.startswith(f"permissions:{user_id}:")
        ]

        for key in keys_to_remove:
            if key in cls._permission_cache:
                del cls._permission_cache[key]

    @classmethod
    async def check_permission(
        cls,
        user: User,
        permission: str,
        project_id: Optional[UUID] = None,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        """Verifica se usuário tem permissão específica.

        Args:
            user: Usuário a verificar
            permission: Permissão no formato 'resource.action' (ex: 'project.create')
            project_id: ID do projeto (para permissões específicas de projeto)
            session: Sessão do banco de dados

        Returns:
            True se usuário tem a permissão, False caso contrário
        """
        # Super admin tem todas as permissões
        if getattr(user, "is_superuser", False):
            return True

        # Obter permissões do usuário
        permissions = await cls.get_user_permissions(
            user=user, project_id=project_id, session=session
        )

        # Verificar permissão exata
        if permission in permissions:
            return True

        # Verificar wildcard '*' (todas as permissões)
        if "*" in permissions:
            return True

        # Verificar wildcards específicos
        for perm in permissions:
            if cls._matches_wildcard(permission, perm):
                return True

        return False

    @classmethod
    def _matches_wildcard(cls, permission: str, pattern: str) -> bool:
        """Verifica se permissão corresponde a um padrão wildcard.

        Exemplos:
        - 'project.*' corresponde a 'project.create', 'project.read', etc
        - 'tenant.*.all' corresponde a 'tenant.create.all', 'tenant.read.all', etc
        """
        return fnmatch.fnmatch(permission, pattern)

    @classmethod
    async def check_any_permission(
        cls,
        user: User,
        permissions: List[str],
        project_id: Optional[UUID] = None,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        """Verifica se usuário tem pelo menos uma das permissões."""
        for permission in permissions:
            if await cls.check_permission(user, permission, project_id, session):
                return True
        return False

    @classmethod
    async def check_all_permissions(
        cls,
        user: User,
        permissions: List[str],
        project_id: Optional[UUID] = None,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        """Verifica se usuário tem todas as permissões."""
        for permission in permissions:
            if not await cls.check_permission(user, permission, project_id, session):
                return False
        return True

    @classmethod
    async def get_user_permissions(
        cls,
        user: User,
        project_id: Optional[UUID] = None,
        session: Optional[AsyncSession] = None,
        use_cache: bool = True,
    ) -> List[str]:
        """Retorna todas as permissões do usuário.

        Args:
            user: Usuário
            project_id: ID do projeto (para incluir permissões específicas)
            session: Sessão do banco de dados
            use_cache: Se deve usar cache

        Returns:
            Lista de permissões do usuário
        """
        # Super admin tem todas as permissões
        if getattr(user, "is_superuser", False):
            return ["*"]

        # Verificar cache
        cache_key = cls._get_cache_key(user.id, project_id)
        if use_cache and cache_key in cls._permission_cache:
            return cls._permission_cache[cache_key]

        # Buscar permissões no banco
        permissions = await cls._load_user_permissions(
            user=user, project_id=project_id, session=session
        )

        # Salvar no cache
        if use_cache:
            cls._permission_cache[cache_key] = permissions

        return permissions

    @classmethod
    async def _load_user_permissions(
        cls,
        user: User,
        project_id: Optional[UUID] = None,
        session: Optional[AsyncSession] = None,
    ) -> List[str]:
        """Carrega permissões do usuário do banco de dados."""
        if not session:
            raise ValueError("Session é obrigatória para carregar permissões")

        permissions: Set[str] = set()

        # Query base para user_roles
        query = select(UserRole).where(UserRole.user_id == user.id).options(
            selectinload(UserRole.role)
        )

        # Filtrar por projeto se especificado
        if project_id:
            # Incluir permissões globais (project_id = None) e específicas do projeto
            query = query.where(
                or_(
                    UserRole.project_id == project_id,
                    UserRole.project_id.is_(None),
                )
            )
        else:
            # Apenas permissões globais
            query = query.where(UserRole.project_id.is_(None))

        result = await session.execute(query)
        user_roles = result.scalars().all()

        # Coletar permissões de todos os roles
        for user_role in user_roles:
            if user_role.role and user_role.role.is_system:
                permissions.update(user_role.role.permissions)

        return list(permissions)

    @classmethod
    async def get_user_roles(
        cls,
        user: User,
        project_id: Optional[UUID] = None,
        session: Optional[AsyncSession] = None,
    ) -> List[Role]:
        """Retorna todos os roles do usuário."""
        if not session:
            raise ValueError("Session é obrigatória")

        # Query para user_roles
        query = select(UserRole).where(UserRole.user_id == user.id).options(
            selectinload(UserRole.role)
        )

        # Filtrar por projeto se especificado
        if project_id:
            query = query.where(
                or_(
                    UserRole.project_id == project_id,
                    UserRole.project_id.is_(None),
                )
            )

        result = await session.execute(query)
        user_roles = result.scalars().all()

        # Retornar apenas roles ativos
        roles = []
        for user_role in user_roles:
            if user_role.role and user_role.role.is_system:
                roles.append(user_role.role)

        return roles

    @classmethod
    async def assign_role(
        cls,
        user: User,
        role_name: str,
        assigned_by: User,
        project_id: Optional[UUID] = None,
        session: Optional[AsyncSession] = None,
    ) -> UserRole:
        """Atribui um role a um usuário.

        Args:
            user: Usuário que receberá o role
            role_name: Nome do role (ex: 'developer')
            assigned_by: Usuário que está atribuindo o role
            project_id: ID do projeto (para roles específicos de projeto)
            session: Sessão do banco de dados

        Returns:
            UserRole criado

        Raises:
            ValueError: Se role não existe ou usuário já tem o role
        """
        if not session:
            raise ValueError("Session é obrigatória")

        # Buscar role
        role_query = select(Role).where(
            Role.name == role_name, Role.tenant_id == user.tenant_id
        )
        role_result = await session.execute(role_query)
        role = role_result.scalar_one_or_none()

        if not role:
            raise ValueError(f"Role '{role_name}' não encontrado")

        if not role.is_system:
            raise ValueError(f"Role '{role_name}' está inativo")

        # Verificar se usuário já tem o role
        existing_query = select(UserRole).where(
            and_(
                UserRole.user_id == user.id,
                UserRole.role_id == role.id,
                UserRole.project_id == project_id,
            )
        )

        existing_result = await session.execute(existing_query)
        existing_user_role = existing_result.scalar_one_or_none()

        if existing_user_role:
            raise ValueError(
                f"Usuário já possui o role '{role_name}' neste contexto"
            )

        # Criar UserRole
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
            project_id=project_id,
        )

        # Adicionar campos extras se existirem
        if hasattr(user_role, "tenant_id"):
            user_role.tenant_id = user.tenant_id
        if hasattr(user_role, "assigned_by"):
            user_role.assigned_by = assigned_by.id
        if hasattr(user_role, "assigned_at"):
            user_role.assigned_at = datetime.utcnow()

        session.add(user_role)
        await session.commit()
        await session.refresh(user_role)

        # Invalidar cache
        cls.invalidate_user_permissions(user.id)

        return user_role

    @classmethod
    async def remove_role(
        cls,
        user: User,
        role_name: str,
        project_id: Optional[UUID] = None,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        """Remove um role de um usuário.

        Returns:
            True se role foi removido, False se não existia
        """
        if not session:
            raise ValueError("Session é obrigatória")

        # Buscar role
        role_query = select(Role).where(
            Role.name == role_name, Role.tenant_id == user.tenant_id
        )
        role_result = await session.execute(role_query)
        role = role_result.scalar_one_or_none()

        if not role:
            return False

        # Buscar UserRole
        user_role_query = select(UserRole).where(
            and_(
                UserRole.user_id == user.id,
                UserRole.role_id == role.id,
                UserRole.project_id == project_id,
            )
        )

        user_role_result = await session.execute(user_role_query)
        user_role = user_role_result.scalar_one_or_none()

        if not user_role:
            return False

        # Remover UserRole
        await session.delete(user_role)
        await session.commit()

        # Invalidar cache
        cls.invalidate_user_permissions(user.id)

        return True

    @classmethod
    def get_cache_stats(cls) -> dict:
        """Retorna estatísticas do cache de permissões."""
        return {
            "size": len(cls._permission_cache),
            "maxsize": cls._permission_cache.maxsize,
            "ttl": cls._permission_cache.ttl,
        }

    @classmethod
    def clear_cache(cls):
        """Limpa todo o cache de permissões."""
        cls._permission_cache.clear()

    @classmethod
    async def get_user_roles(
        cls,
        user: User,
        session: AsyncSession,
        project_id: Optional[UUID] = None,
    ) -> List[Role]:
        """Retorna todos os roles do usuário.

        Args:
            user: Usuário
            session: Sessão do banco de dados
            project_id: ID do projeto (para incluir roles específicos)

        Returns:
            Lista de roles do usuário
        """
        # Query base para user_roles
        query = select(Role).join(UserRole).where(UserRole.user_id == user.id)

        # Filtrar por projeto se especificado
        if project_id:
            query = query.where(
                or_(
                    UserRole.project_id == project_id,
                    UserRole.project_id.is_(None),
                )
            )
        else:
            # Apenas roles globais
            query = query.where(UserRole.project_id.is_(None))

        result = await session.execute(query)
        return list(result.scalars().all())
