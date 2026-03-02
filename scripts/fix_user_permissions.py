#!/usr/bin/env python3
"""Fix user permissions for testing."""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from services.shared.database import get_session
from services.identity.models import User, Role, UserRole
from services.identity.permission_service import PermissionService

async def fix_permissions():
    """Fix permissions for all users."""
    
    async for session in get_session():
        try:
            print("🔧 Fixing user permissions...\n")
            
            # 1. Verificar gomesrocha (Super Admin)
            print("1️⃣ Checking gomesrocha@gmail.com (Super Admin)...")
            result = await session.execute(
                select(User).where(User.email == "gomesrocha@gmail.com")
            )
            gomes = result.scalar_one_or_none()
            
            if gomes:
                print(f"   ✅ Found: {gomes.email}")
                print(f"   is_superuser: {gomes.is_superuser}")
                
                if not gomes.is_superuser:
                    gomes.is_superuser = True
                    await session.commit()
                    print(f"   ✅ Set as superuser")
            else:
                print(f"   ❌ User not found")
            
            # 2. Verificar acme@acme.com (Tenant Admin)
            print("\n2️⃣ Checking acme@acme.com (Tenant Admin)...")
            result = await session.execute(
                select(User).where(User.email == "acme@acme.com")
            )
            acme = result.scalar_one_or_none()
            
            if acme:
                print(f"   ✅ Found: {acme.email}")
                print(f"   tenant_id: {acme.tenant_id}")
                
                # Buscar roles do usuário
                result = await session.execute(
                    select(Role)
                    .join(UserRole, UserRole.role_id == Role.id)
                    .where(UserRole.user_id == acme.id)
                )
                roles = result.scalars().all()
                
                print(f"   Current roles: {len(roles)}")
                for role in roles:
                    print(f"     - {role.name}")
                    perms = await PermissionService.get_role_permissions(role, session)
                    print(f"       Permissions: {len(perms)}")
                
                # Verificar se tem role de Admin
                has_admin = any(r.name in ['Admin', 'Tenant Admin'] for r in roles)
                if not has_admin:
                    print(f"   ⚠️ Missing Admin role!")
                    
                    # Buscar role Admin do tenant
                    result = await session.execute(
                        select(Role).where(
                            Role.tenant_id == acme.tenant_id,
                            Role.name.in_(['Admin', 'Tenant Admin'])
                        )
                    )
                    admin_role = result.scalar_one_or_none()
                    
                    if admin_role:
                        # Adicionar role
                        user_role = UserRole(user_id=acme.id, role_id=admin_role.id)
                        session.add(user_role)
                        await session.commit()
                        print(f"   ✅ Added {admin_role.name} role")
                    else:
                        print(f"   ❌ Admin role not found for tenant")
            else:
                print(f"   ❌ User not found")
            
            # 3. Verificar odair@acme.com (Project Manager)
            print("\n3️⃣ Checking odair@acme.com (Project Manager)...")
            result = await session.execute(
                select(User).where(User.email == "odair@acme.com")
            )
            odair = result.scalar_one_or_none()
            
            if odair:
                print(f"   ✅ Found: {odair.email}")
                print(f"   tenant_id: {odair.tenant_id}")
                
                # Buscar roles do usuário
                result = await session.execute(
                    select(Role)
                    .join(UserRole, UserRole.role_id == Role.id)
                    .where(UserRole.user_id == odair.id)
                )
                roles = result.scalars().all()
                
                print(f"   Current roles: {len(roles)}")
                for role in roles:
                    print(f"     - {role.name}")
                    perms = await PermissionService.get_role_permissions(role, session)
                    print(f"       Permissions: {len(perms)}")
                
                # Verificar se tem role de Project Manager
                has_pm = any('Project' in r.name or 'Manager' in r.name for r in roles)
                if not has_pm:
                    print(f"   ⚠️ Missing Project Manager role!")
                    
                    # Buscar role Project Manager do tenant
                    result = await session.execute(
                        select(Role).where(
                            Role.tenant_id == odair.tenant_id,
                            Role.name.ilike('%project%')
                        )
                    )
                    pm_role = result.scalar_one_or_none()
                    
                    if pm_role:
                        # Adicionar role
                        user_role = UserRole(user_id=odair.id, role_id=pm_role.id)
                        session.add(user_role)
                        await session.commit()
                        print(f"   ✅ Added {pm_role.name} role")
                    else:
                        print(f"   ⚠️ Project Manager role not found, will use Admin")
                        # Usar Admin como fallback
                        result = await session.execute(
                            select(Role).where(
                                Role.tenant_id == odair.tenant_id,
                                Role.name == 'Admin'
                            )
                        )
                        admin_role = result.scalar_one_or_none()
                        if admin_role:
                            user_role = UserRole(user_id=odair.id, role_id=admin_role.id)
                            session.add(user_role)
                            await session.commit()
                            print(f"   ✅ Added Admin role as fallback")
            else:
                print(f"   ❌ User not found")
            
            print("\n✅ Done!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(fix_permissions())
