#!/usr/bin/env python3
"""Script para criar roles padrão no banco de dados."""

import asyncio
from uuid import uuid4
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from services.identity.models import Role, Tenant
from services.identity.permissions import DEFAULT_ROLE_PERMISSIONS
from services.shared.config import settings


async def create_default_roles():
    """Cria roles padrão para todos os tenants."""
    # Criar engine e session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Buscar todos os tenants
        result = await session.execute(select(Tenant))
        tenants = result.scalars().all()

        if not tenants:
            print("❌ Nenhum tenant encontrado. Crie um tenant primeiro.")
            return

        for tenant in tenants:
            print(f"\n📦 Criando roles para tenant: {tenant.name}")

            for role_name, permissions in DEFAULT_ROLE_PERMISSIONS.items():
                # Verificar se role já existe
                existing = await session.execute(
                    select(Role).where(
                        Role.tenant_id == tenant.id,
                        Role.name == role_name
                    )
                )
                if existing.scalar_one_or_none():
                    print(f"  ⏭️  Role '{role_name}' já existe")
                    continue

                # Criar role
                role = Role(
                    id=uuid4(),
                    tenant_id=tenant.id,
                    name=role_name,
                    description=get_role_description(role_name),
                    permissions=list(permissions),
                    is_system=True,
                )
                session.add(role)
                print(f"  ✅ Role '{role_name}' criado com {len(permissions)} permissões")

            await session.commit()

        print("\n✅ Roles criados com sucesso!")

    await engine.dispose()


def get_role_description(role_name: str) -> str:
    """Retorna descrição do role."""
    descriptions = {
        "super_admin": "Super Administrator - Full system access",
        "admin": "Administrator - Full tenant access",
        "po": "Product Owner - Product management",
        "dev": "Developer - Development tasks",
        "qa": "QA Engineer - Quality assurance",
        "sec": "Security Engineer - Security tasks",
        "auditor": "Auditor - Read-only access for auditing",
    }
    return descriptions.get(role_name, f"Role: {role_name}")


if __name__ == "__main__":
    asyncio.run(create_default_roles())
