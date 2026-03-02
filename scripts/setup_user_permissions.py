#!/usr/bin/env python3
"""Setup user permissions correctly."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import async_session_maker
from services.identity.models import User, Role, UserRole, Tenant
from sqlmodel import select

async def main():
    async with async_session_maker() as session:
        print("\n" + "="*60)
        print("CONFIGURANDO PERMISSÕES DE USUÁRIOS")
        print("="*60)
        
        # 1. Configurar gomesrocha@gmail.com como Super Admin Global
        result = await session.execute(
            select(User).where(User.email == "gomesrocha@gmail.com")
        )
        gomes = result.scalar_one_or_none()
        
        if gomes:
            gomes.is_superuser = True
            session.add(gomes)
            print(f"\n✅ gomesrocha@gmail.com → Super Admin Global")
            print(f"   - is_superuser: True")
            print(f"   - Pode gerenciar TODOS os tenants")
        else:
            print(f"\n❌ gomesrocha@gmail.com não encontrado")
        
        # 2. Configurar admin@test.com como Super Admin Global
        result = await session.execute(
            select(User).where(User.email == "admin@test.com")
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            admin.is_superuser = True
            session.add(admin)
            print(f"\n✅ admin@test.com → Super Admin Global")
            print(f"   - is_superuser: True")
            print(f"   - Pode gerenciar TODOS os tenants")
        else:
            print(f"\n❌ admin@test.com não encontrado")
        
        # 3. Configurar acme@acme.com como Admin do Tenant
        result = await session.execute(
            select(User).where(User.email == "acme@acme.com")
        )
        acme = result.scalar_one_or_none()
        
        if acme:
            acme.is_superuser = False
            session.add(acme)
            
            # Buscar tenant acme
            result = await session.execute(
                select(Tenant).where(Tenant.id == acme.tenant_id)
            )
            acme_tenant = result.scalar_one_or_none()
            
            # Buscar ou criar role Admin no tenant
            result = await session.execute(
                select(Role).where(
                    Role.tenant_id == acme.tenant_id,
                    Role.name == "Admin"
                )
            )
            admin_role = result.scalar_one_or_none()
            
            if not admin_role:
                admin_role = Role(
                    tenant_id=acme.tenant_id,
                    name="Admin",
                    description="Administrador do tenant",
                    permissions=[
                        # User permissions
                        "user:read", "user:write", "user:delete",
                        "user:role:read", "user:role:write", "user:role:assign",
                        # Project permissions
                        "project:read", "project:write", "project:delete", "project:create",
                        # Work item permissions
                        "workitem:read", "workitem:write", "workitem:delete",
                        # Role permissions
                        "role:read", "role:write", "role:delete",
                        # Admin permissions (IMPORTANTE!)
                        "admin:manage_users", "admin:manage_roles",
                    ],
                    is_system=True
                )
                session.add(admin_role)
                await session.flush()
                print(f"\n✅ Role 'Admin' criada no tenant {acme_tenant.name if acme_tenant else 'acme'}")
            else:
                # Atualizar permissões da role existente
                admin_role.permissions = [
                    # User permissions
                    "user:read", "user:write", "user:delete",
                    "user:role:read", "user:role:write", "user:role:assign",
                    # Project permissions
                    "project:read", "project:write", "project:delete", "project:create",
                    # Work item permissions
                    "workitem:read", "workitem:write", "workitem:delete",
                    # Role permissions
                    "role:read", "role:write", "role:delete",
                    # Admin permissions (IMPORTANTE!)
                    "admin:manage_users", "admin:manage_roles",
                ]
                session.add(admin_role)
                await session.flush()
                print(f"\n✅ Role 'Admin' atualizada no tenant {acme_tenant.name if acme_tenant else 'acme'}")
            
            # Verificar se já tem a role
            result = await session.execute(
                select(UserRole).where(
                    UserRole.user_id == acme.id,
                    UserRole.role_id == admin_role.id
                )
            )
            existing_user_role = result.scalar_one_or_none()
            
            if not existing_user_role:
                user_role = UserRole(
                    user_id=acme.id,
                    role_id=admin_role.id,
                    project_id=None  # Role global no tenant
                )
                session.add(user_role)
                print(f"\n✅ acme@acme.com → Admin do Tenant '{acme_tenant.name if acme_tenant else 'acme'}'")
                print(f"   - is_superuser: False")
                print(f"   - Role: Admin (no tenant)")
                print(f"   - Pode gerenciar apenas o tenant '{acme_tenant.name if acme_tenant else 'acme'}'")
            else:
                print(f"\n✅ acme@acme.com já é Admin do Tenant '{acme_tenant.name if acme_tenant else 'acme'}'")
        else:
            print(f"\n❌ acme@acme.com não encontrado")
        
        await session.commit()
        
        print("\n" + "="*60)
        print("RESUMO DAS CONFIGURAÇÕES")
        print("="*60)
        print("\n📋 Estrutura de Permissões:")
        print("\n1. Super Admins Globais (is_superuser=True):")
        print("   - gomesrocha@gmail.com / gomes1234")
        print("   - admin@test.com / admin1234")
        print("   → Veem menu 'Tenants'")
        print("   → Podem gerenciar TODOS os tenants")
        
        print("\n2. Admins de Tenant (is_superuser=False + Role Admin):")
        print("   - acme@acme.com / acme1234")
        print("   → NÃO veem menu 'Tenants'")
        print("   → Gerenciam apenas o próprio tenant")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())
