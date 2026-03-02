#!/usr/bin/env python3
"""Recreate super admin users."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import async_session_maker
from services.identity.models import User, Tenant
from services.identity.security import hash_password
from sqlmodel import select

async def main():
    async with async_session_maker() as session:
        print("\n" + "="*60)
        print("RECRIANDO SUPER ADMINS")
        print("="*60)
        
        # 1. Buscar ou criar tenant "System" para super admins
        result = await session.execute(
            select(Tenant).where(Tenant.slug == "system")
        )
        system_tenant = result.scalar_one_or_none()
        
        if not system_tenant:
            system_tenant = Tenant(
                name="System",
                slug="system",
                is_active=True,
                settings={"description": "Tenant para super administradores globais"}
            )
            session.add(system_tenant)
            await session.commit()
            await session.refresh(system_tenant)
            print(f"\n✅ Tenant 'System' criado para super admins")
            print(f"   ID: {system_tenant.id}")
        else:
            print(f"\n✅ Tenant 'System' já existe")
            print(f"   ID: {system_tenant.id}")
        
        # 2. Criar/Recriar gomesrocha@gmail.com
        result = await session.execute(
            select(User).where(User.email == "gomesrocha@gmail.com")
        )
        gomes = result.scalar_one_or_none()
        
        if not gomes:
            gomes = User(
                tenant_id=system_tenant.id,
                email="gomesrocha@gmail.com",
                hashed_password=hash_password("gomes1234"),
                full_name="Gomes Rocha",
                is_active=True,
                is_superuser=True
            )
            session.add(gomes)
            print(f"\n✅ Usuário 'gomesrocha@gmail.com' criado")
        else:
            gomes.tenant_id = system_tenant.id
            gomes.is_superuser = True
            gomes.is_active = True
            gomes.hashed_password = hash_password("gomes1234")
            session.add(gomes)
            print(f"\n✅ Usuário 'gomesrocha@gmail.com' atualizado")
        
        print(f"   - Email: gomesrocha@gmail.com")
        print(f"   - Password: gomes1234")
        print(f"   - Tenant: System")
        print(f"   - is_superuser: True")
        
        # 3. Criar/Recriar admin@test.com
        result = await session.execute(
            select(User).where(User.email == "admin@test.com")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                tenant_id=system_tenant.id,
                email="admin@test.com",
                hashed_password=hash_password("admin1234"),
                full_name="Test Admin",
                is_active=True,
                is_superuser=True
            )
            session.add(admin)
            print(f"\n✅ Usuário 'admin@test.com' criado")
        else:
            admin.tenant_id = system_tenant.id
            admin.is_superuser = True
            admin.is_active = True
            admin.hashed_password = hash_password("admin1234")
            session.add(admin)
            print(f"\n✅ Usuário 'admin@test.com' atualizado")
        
        print(f"   - Email: admin@test.com")
        print(f"   - Password: admin1234")
        print(f"   - Tenant: System")
        print(f"   - is_superuser: True")
        
        await session.commit()
        
        print("\n" + "="*60)
        print("RESUMO")
        print("="*60)
        print("\n✅ Super Admins Globais recriados com sucesso!")
        print("\n📋 Credenciais:")
        print("\n1. gomesrocha@gmail.com / gomes1234")
        print("   - Tenant: System")
        print("   - Super Admin Global")
        
        print("\n2. admin@test.com / admin1234")
        print("   - Tenant: System")
        print("   - Super Admin Global")
        
        print("\n3. acme@acme.com / acme1234")
        print("   - Tenant: Acme Corp One")
        print("   - Admin do Tenant")
        
        print("\n💡 Nota: Super admins agora pertencem ao tenant 'System'")
        print("   mas podem gerenciar TODOS os tenants da plataforma.")
        print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())
