"""
Serviço de gerenciamento de tenants (empresas).

Este serviço é responsável por:
- Criar novos tenants
- Atualizar informações de tenants
- Consultar tenants
- Gerenciar configurações de tenant
"""

from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.identity.models import Tenant


class TenantService:
    """Serviço de gerenciamento de tenants."""

    @classmethod
    async def create_tenant(
        cls,
        session: AsyncSession,
        name: str,
        slug: str,
        settings: Optional[dict] = None,
    ) -> Tenant:
        """Cria um novo tenant.

        Args:
            session: Sessão do banco de dados
            name: Nome da empresa
            slug: Slug único para a empresa
            settings: Configurações adicionais (opcional)

        Returns:
            Tenant criado

        Raises:
            ValueError: Se slug já existe
        """
        # Verificar se slug já existe
        existing = await cls.get_tenant_by_slug(session, slug)
        if existing:
            raise ValueError(f"Tenant com slug '{slug}' já existe")

        # Criar tenant
        tenant = Tenant(
            id=uuid4(),
            name=name,
            slug=slug,
            settings=settings or {},
            is_active=True,
        )

        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)

        return tenant
        await session.commit()
        await session.refresh(tenant)

        return tenant

    @classmethod
    async def get_tenant(
        cls, session: AsyncSession, tenant_id: UUID
    ) -> Optional[Tenant]:
        """Obtém um tenant por ID.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant

        Returns:
            Tenant ou None se não encontrado
        """
        query = select(Tenant).where(Tenant.id == tenant_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_tenant_by_slug(
        cls, session: AsyncSession, slug: str
    ) -> Optional[Tenant]:
        """Obtém um tenant por slug.

        Args:
            session: Sessão do banco de dados
            slug: Slug do tenant

        Returns:
            Tenant ou None se não encontrado
        """
        query = select(Tenant).where(Tenant.slug == slug)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_tenant_by_domain(
        cls, session: AsyncSession, domain: str
    ) -> Optional[Tenant]:
        """Obtém um tenant por domínio customizado.

        Args:
            session: Sessão do banco de dados
            domain: Domínio do tenant

        Returns:
            Tenant ou None se não encontrado
        """
        # Verificar se o modelo tem o campo domain
        if not hasattr(Tenant, "domain"):
            return None

        query = select(Tenant).where(Tenant.domain == domain)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def list_tenants(
        cls,
        session: AsyncSession,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Tenant]:
        """Lista tenants com filtros.

        Args:
            session: Sessão do banco de dados
            is_active: Filtrar por status ativo (opcional)
            limit: Limite de resultados
            offset: Offset para paginação

        Returns:
            Lista de tenants
        """
        query = select(Tenant)

        if is_active is not None:
            query = query.where(Tenant.is_active == is_active)

        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def update_tenant(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        name: Optional[str] = None,
        settings: Optional[dict] = None,
        is_active: Optional[bool] = None,
        subscription_plan: Optional[str] = None,
        max_users: Optional[int] = None,
        max_projects: Optional[int] = None,
        logo_url: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Optional[Tenant]:
        """Atualiza informações de um tenant.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant
            name: Novo nome (opcional)
            settings: Novas configurações (opcional)
            is_active: Novo status ativo (opcional)
            subscription_plan: Novo plano (opcional)
            max_users: Novo limite de usuários (opcional)
            max_projects: Novo limite de projetos (opcional)
            logo_url: Nova URL do logo (opcional)
            domain: Novo domínio (opcional)

        Returns:
            Tenant atualizado ou None se não encontrado
        """
        tenant = await cls.get_tenant(session, tenant_id)
        if not tenant:
            return None

        # Atualizar campos
        if name is not None:
            tenant.name = name
        if settings is not None:
            tenant.settings = settings
        if is_active is not None:
            tenant.is_active = is_active

        # Atualizar campos extras se existirem
        if subscription_plan is not None and hasattr(tenant, "subscription_plan"):
            tenant.subscription_plan = subscription_plan
        if max_users is not None and hasattr(tenant, "max_users"):
            tenant.max_users = max_users
        if max_projects is not None and hasattr(tenant, "max_projects"):
            tenant.max_projects = max_projects
        if logo_url is not None and hasattr(tenant, "logo_url"):
            tenant.logo_url = logo_url
        if domain is not None and hasattr(tenant, "domain"):
            tenant.domain = domain

        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)

        return tenant

    @classmethod
    async def delete_tenant(
        cls, session: AsyncSession, tenant_id: UUID
    ) -> bool:
        """Desativa um tenant (soft delete).

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant

        Returns:
            True se desativado, False se não encontrado
        """
        tenant = await cls.get_tenant(session, tenant_id)
        if not tenant:
            return False

        tenant.is_active = False
        session.add(tenant)
        await session.commit()

        return True

    @classmethod
    async def get_tenant_stats(
        cls, session: AsyncSession, tenant_id: UUID
    ) -> Optional[dict]:
        """Obtém estatísticas de uso de um tenant.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant

        Returns:
            Dicionário com estatísticas ou None se tenant não encontrado
        """
        tenant = await cls.get_tenant(session, tenant_id)
        if not tenant:
            return None

        # Contar usuários
        from services.identity.models import User

        user_query = select(User).where(User.tenant_id == tenant_id)
        user_result = await session.execute(user_query)
        user_count = len(list(user_result.scalars().all()))

        # Contar projetos
        try:
            from services.project.models import Project

            project_query = select(Project).where(Project.tenant_id == tenant_id)
            project_result = await session.execute(project_query)
            project_count = len(list(project_result.scalars().all()))
        except ImportError:
            project_count = 0

        # Montar estatísticas
        stats = {
            "tenant_id": str(tenant_id),
            "tenant_name": tenant.name,
            "user_count": user_count,
            "project_count": project_count,
            "is_active": tenant.is_active,
        }

        # Adicionar limites se existirem
        if hasattr(tenant, "max_users"):
            stats["max_users"] = tenant.max_users
            stats["users_remaining"] = max(0, tenant.max_users - user_count)

        if hasattr(tenant, "max_projects"):
            stats["max_projects"] = tenant.max_projects
            stats["projects_remaining"] = max(
                0, tenant.max_projects - project_count
            )

        if hasattr(tenant, "subscription_plan"):
            stats["subscription_plan"] = tenant.subscription_plan

        return stats

    @classmethod
    async def check_tenant_limits(
        cls, session: AsyncSession, tenant_id: UUID, resource_type: str
    ) -> bool:
        """Verifica se tenant pode criar mais recursos.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant
            resource_type: Tipo de recurso ('user' ou 'project')

        Returns:
            True se pode criar, False se atingiu o limite
        """
        stats = await cls.get_tenant_stats(session, tenant_id)
        if not stats:
            return False

        if resource_type == "user":
            if "users_remaining" in stats:
                return stats["users_remaining"] > 0
            return True  # Sem limite definido

        if resource_type == "project":
            if "projects_remaining" in stats:
                return stats["projects_remaining"] > 0
            return True  # Sem limite definido

        return True
