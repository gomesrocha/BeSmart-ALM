#!/usr/bin/env python3
"""Create test users."""

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
        # Find or create test tenant
        result = await session.execute(
            select(Tenant).where(Tenant.slug == "test")
        )
        test_tenant = result.scalar_one_or_none()
        
        if not test_tenant:
            test_tenant = Tenant(
                name="Test Company",
                slug="test",
                is_active=True
            )
            session.add(test_tenant)
            await session.commit()
            await session.refresh(test_tenant)
            print(f"✅ Created tenant: {test_tenant.name}")
        else:
            print(f"✅ Found tenant: {test_tenant.name}")
        
        # Create admin@test.com
        result = await session.execute(
            select(User).where(User.email == "admin@test.com")
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            admin_user = User(
                tenant_id=test_tenant.id,
                email="admin@test.com",
                hashed_password=hash_password("admin1234"),
                full_name="Test Admin",
                is_active=True,
                is_superuser=False
            )
            session.add(admin_user)
            print(f"✅ Created user: admin@test.com")
        else:
            admin_user.hashed_password = hash_password("admin1234")
            admin_user.is_active = True
            session.add(admin_user)
            print(f"✅ Updated user: admin@test.com")
        
        # Create gomesrocha@gmail.com
        result = await session.execute(
            select(User).where(User.email == "gomesrocha@gmail.com")
        )
        gomes_user = result.scalar_one_or_none()
        
        if not gomes_user:
            gomes_user = User(
                tenant_id=test_tenant.id,
                email="gomesrocha@gmail.com",
                hashed_password=hash_password("gomes1234"),
                full_name="Gomes Rocha",
                is_active=True,
                is_superuser=False
            )
            session.add(gomes_user)
            print(f"✅ Created user: gomesrocha@gmail.com")
        else:
            gomes_user.hashed_password = hash_password("gomes1234")
            gomes_user.is_active = True
            session.add(gomes_user)
            print(f"✅ Updated user: gomesrocha@gmail.com")
        
        await session.commit()
        
        print("\n" + "="*50)
        print("✅ Users created/updated successfully!")
        print("="*50)
        print(f"\nTenant: {test_tenant.name} ({test_tenant.slug})")
        print(f"Tenant ID: {test_tenant.id}")
        print("\nCredentials:")
        print("  1. admin@test.com / admin1234")
        print("  2. gomesrocha@gmail.com / gomes1234")
        print("  3. acme@acme.com / acme1234 (existing)")

if __name__ == "__main__":
    asyncio.run(main())
