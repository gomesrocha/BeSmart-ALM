#!/usr/bin/env python3
"""Fix permissions for acme@acme.com user."""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from services.shared.database import get_session
from services.identity.models import User, Role, UserRole
import sys

async def fix_acme_permissions():
    """Fix permissions for acme user."""
    
    async for session in get_session():
        try:
            # Find acme user
            result = await session.execute(
                select(User).where(User.email == "acme@acme.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User acme@acme.com not found")
                return
            
            print(f"✅ Found user: {user.email}")
            print(f"   Tenant ID: {user.tenant_id}")
            
            # Find Tenant Admin role for this tenant
            result = await session.execute(
                select(Role).where(
                    Role.name == "Tenant Admin",
                    Role.tenant_id == user.tenant_id
                )
            )
            tenant_admin_role = result.scalar_one_or_none()
            
            if not tenant_admin_role:
                print("❌ Tenant Admin role not found for this tenant")
                print("   Creating Tenant Admin role...")
                
                # Create Tenant Admin role
                tenant_admin_role = Role(
                    name="Tenant Admin",
                    display_name="Tenant Admin",
                    description="Full access to tenant resources",
                    tenant_id=user.tenant_id,
                    permissions=[
                        "user:create", "user:read", "user:update", "user:delete",
                        "role:create", "role:read", "role:update", "role:delete",
                        "project:create", "project:read", "project:update", "project:delete",
                        "workitem:create", "workitem:read", "workitem:update", "workitem:delete",
                        "user:role:assign", "user:role:remove", "user:role:read", "user:role:write"
                    ]
                )
                session.add(tenant_admin_role)
                await session.flush()
                print(f"✅ Created Tenant Admin role: {tenant_admin_role.id}")
            
            # Check if user already has this role
            result = await session.execute(
                select(UserRole).where(
                    UserRole.user_id == user.id,
                    UserRole.role_id == tenant_admin_role.id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"✅ User already has Tenant Admin role")
            else:
                # Assign role to user
                user_role = UserRole(
                    user_id=user.id,
                    role_id=tenant_admin_role.id
                )
                session.add(user_role)
                print(f"✅ Assigned Tenant Admin role to user")
            
            await session.commit()
            
            # Verify
            result = await session.execute(
                select(Role)
                .join(UserRole, UserRole.role_id == Role.id)
                .where(UserRole.user_id == user.id)
            )
            roles = result.scalars().all()
            
            print(f"\n📋 User now has {len(roles)} role(s):")
            for role in roles:
                print(f"   - {role.name}: {len(role.permissions)} permissions")
                for perm in role.permissions[:5]:
                    print(f"     • {perm}")
                if len(role.permissions) > 5:
                    print(f"     • ... and {len(role.permissions) - 5} more")
            
            print(f"\n✅ Done! User acme@acme.com now has proper permissions")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(fix_acme_permissions())
