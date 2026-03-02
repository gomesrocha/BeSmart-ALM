#!/usr/bin/env python3
"""Create odair@acme.com user."""

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
        # Find acme tenant
        result = await session.execute(
            select(Tenant).where(Tenant.slug.like("%acme%"))
        )
        acme_tenant = result.scalar_one_or_none()
        
        if not acme_tenant:
            print("❌ Tenant Acme not found")
            return
        
        print(f"✅ Found tenant: {acme_tenant.name}")
        print(f"   ID: {acme_tenant.id}")
        
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == "odair@acme.com")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"\n⚠️  User odair@acme.com already exists")
            print(f"   Resetting password to: odair1234")
            existing_user.hashed_password = hash_password("odair1234")
            existing_user.is_active = True
            session.add(existing_user)
        else:
            # Create user
            new_user = User(
                tenant_id=acme_tenant.id,
                email="odair@acme.com",
                hashed_password=hash_password("odair1234"),
                full_name="Odair",
                is_active=True,
                is_superuser=False
            )
            session.add(new_user)
            print(f"\n✅ Created user: odair@acme.com")
        
        await session.commit()
        
        print(f"\n📋 Credentials:")
        print(f"   Email: odair@acme.com")
        print(f"   Password: odair1234")
        print(f"   Tenant: {acme_tenant.name}")
        print(f"   is_superuser: False")

if __name__ == "__main__":
    asyncio.run(main())
