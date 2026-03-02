#!/usr/bin/env python3
"""Fix acme user issues."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import select
from services.shared.database import async_session_maker
from services.identity.models import User, Tenant
from services.identity.security import hash_password


async def fix_acme_user():
    """Check and fix acme user."""
    async with async_session_maker() as session:
        # Find acme tenant (try different slugs)
        result = await session.execute(
            select(Tenant).where(Tenant.slug.like("acme%"))
        )
        acme_tenant = result.scalar_one_or_none()
        
        if not acme_tenant:
            # Try by name
            result = await session.execute(
                select(Tenant).where(Tenant.name.like("%acme%"))
            )
            acme_tenant = result.scalar_one_or_none()
        
        if not acme_tenant:
            print("❌ Acme tenant not found")
            print("\n📋 Available tenants:")
            result = await session.execute(select(Tenant))
            tenants = result.scalars().all()
            for t in tenants:
                print(f"  - {t.name} (slug: {t.slug}, id: {t.id})")
            return
        
        print(f"✅ Found acme tenant: {acme_tenant.name} (ID: {acme_tenant.id})")
        
        # Find acme user
        result = await session.execute(
            select(User).where(User.tenant_id == acme_tenant.id)
        )
        acme_users = result.scalars().all()
        
        print(f"\n📋 Users in acme tenant: {len(acme_users)}")
        for user in acme_users:
            print(f"  - {user.full_name} ({user.email})")
            print(f"    ID: {user.id}")
            print(f"    Active: {user.is_active}")
            print(f"    Superuser: {user.is_superuser}")
            print(f"    Has password: {bool(user.hashed_password)}")
            print()
        
        if not acme_users:
            print("❌ No users found in acme tenant")
            print("\nCreating acme admin user...")
            
            new_user = User(
                tenant_id=acme_tenant.id,
                email="admin@acme.com",
                hashed_password=hash_password("acme123"),
                full_name="Acme Admin",
                is_active=True,
                is_superuser=False,
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            print(f"✅ Created user: {new_user.email}")
            print(f"   Password: acme123")
            print(f"   ID: {new_user.id}")
        else:
            # Reset password for first user
            user = acme_users[0]
            print(f"\n🔧 Resetting password for {user.email}...")
            
            user.hashed_password = hash_password("acme123")
            user.is_active = True
            session.add(user)
            await session.commit()
            
            print(f"✅ Password reset to: acme123")
            print(f"✅ User activated")
        
        print("\n✅ Done! Try logging in with:")
        print(f"   Email: {acme_users[0].email if acme_users else 'admin@acme.com'}")
        print(f"   Password: acme123")


if __name__ == "__main__":
    asyncio.run(fix_acme_user())
