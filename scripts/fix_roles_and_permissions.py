#!/usr/bin/env python3
"""Script para corrigir roles e permissões no banco de dados."""

import asyncio
import sys
from uuid import uuid4
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório raiz ao path
sys.path.insert(0, '/home/fabio/organizacao/repository/bsmart-alm')

from services.identity.models import Role, Tenant, User, UserRole
from services.identity.permissions import DEFAULT_ROLE_PERMISSIONS
from services.shared.config import settings


async def main():
    """Função principal."""
    print("🔧 Corrigindo Roles e Permissões\n")
    
    # Criar engine
    engine = create_async_engine(
        str(settings.database_url).replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Limpar roles duplicados
        print("1️⃣ Limpando roles duplicados...")
        await clean_duplicate_roles(session)
        
        # 2. Criar roles padrão
        print("\n2️⃣ Criando roles padrão...")
        await create_default_roles(session)
        
        # 3. Atribuir role admin ao usuário admin@test.com
        print("\n3️⃣ Atribuindo role admin ao usuário...")
        await assign_admin_role(session)
        
        print("\n✅ Correções concluídas com sucesso!")

    await engine.dispose()


async def clean_duplicate_roles(session: AsyncSession):
    """Remove roles duplicados, mantendo apenas o mais antigo."""
    # Buscar todos os roles
    result = await session.execute(select(Role))
    all_roles = result.scalars().all()
    
    # Agrupar por tenant_id + name
    roles_by_key = {}
    for role in all_roles:
        key = (role.tenant_id, role.name)
        if key not in roles_by_key:
            roles_by_key[key] = []
        roles_by_key[key].append(role)
    
    # Deletar duplicados
    deleted_count = 0
    for key, roles in roles_by_key.items():
        if len(roles) > 1:
            # Ordenar por created_at (manter o mais antigo)
            roles.sort(key=lambda r: r.created_at)
            # Deletar todos exceto o primeiro
            for role in roles[1:]:
                await session.delete(role)
                deleted_count += 1
                print(f"  🗑️  Deletado role duplicado: {role.name} (tenant: {role.tenant_id})")
    
    if deleted_count > 0:
        await session.commit()
        print(f"  ✅ {deleted_count} role(s) duplicado(s) removido(s)")
    else:
        print("  ✅ Nenhum role duplicado encontrado")


async def create_default_roles(session: AsyncSession):
    """Cria roles padrão para todos os tenants."""
    # Buscar todos os tenants
    result = await session.execute(select(Tenant))
    tenants = result.scalars().all()
    
    if not tenants:
        print("  ❌ Nenhum tenant encontrado")
        return
    
    created_count = 0
    for tenant in tenants:
        print(f"\n  📦 Tenant: {tenant.name}")
        
        for role_name, permissions in DEFAULT_ROLE_PERMISSIONS.items():
            # Verificar se role já existe
            existing = await session.execute(
                select(Role).where(
                    Role.tenant_id == tenant.id,
                    Role.name == role_name
                )
            )
            if existing.scalar_one_or_none():
                print(f"    ⏭️  Role '{role_name}' já existe")
                continue
            
            # Criar role
            role = Role(
                id=uuid4(),
                tenant_id=tenant.id,
                name=role_name,
                description=get_role_description(role_name),
                permissions=[p.value for p in permissions],
                is_system=True,
            )
            session.add(role)
            created_count += 1
            print(f"    ✅ Role '{role_name}' criado ({len(permissions)} permissões)")
    
    if created_count > 0:
        await session.commit()
        print(f"\n  ✅ {created_count} role(s) criado(s)")
    else:
        print("\n  ✅ Todos os roles já existem")


async def assign_admin_role(session: AsyncSession):
    """Atribui role admin ao usuário admin@test.com."""
    # Buscar usuário
    user_result = await session.execute(
        select(User).where(User.email == 'admin@test.com')
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        print("  ❌ Usuário admin@test.com não encontrado")
        return
    
    print(f"  👤 Usuário encontrado: {user.email}")
    
    # Buscar role admin do mesmo tenant
    role_result = await session.execute(
        select(Role).where(
            Role.tenant_id == user.tenant_id,
            Role.name == 'admin'
        )
    )
    role = role_result.scalar_one_or_none()
    
    if not role:
        print(f"  ❌ Role 'admin' não encontrado para o tenant {user.tenant_id}")
        return
    
    print(f"  🛡️  Role encontrado: {role.name}")
    
    # Verificar se user_role já existe
    existing_ur = await session.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
            UserRole.project_id.is_(None)
        )
    )
    if existing_ur.scalar_one_or_none():
        print("  ⏭️  User role já existe")
        return
    
    # Criar user_role
    user_role = UserRole(
        id=uuid4(),
        user_id=user.id,
        role_id=role.id,
        project_id=None,
    )
    session.add(user_role)
    await session.commit()
    
    print("  ✅ Role 'admin' atribuído ao usuário")


def get_role_description(role_name: str) -> str:
    """Retorna descrição do role."""
    descriptions = {
        "admin": "Administrator - Full tenant access",
        "po": "Product Owner - Product management",
        "dev": "Developer - Development tasks",
        "qa": "QA Engineer - Quality assurance",
        "sec": "Security Engineer - Security tasks",
        "auditor": "Auditor - Read-only access for auditing",
    }
    return descriptions.get(role_name, f"Role: {role_name}")


if __name__ == "__main__":
    asyncio.run(main())
