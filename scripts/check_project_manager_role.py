#!/usr/bin/env python3
"""Check Project Manager role permissions."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import async_session_maker
from services.identity.models import Role, Tenant
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
        print(f"   ID: {acme_tenant.id}\n")
        
        # Find all roles in tenant
        result = await session.execute(
            select(Role).where(Role.tenant_id == acme_tenant.id)
        )
        roles = result.scalars().all()
        
        print(f"📋 Roles in tenant: {len(roles)}\n")
        
        for role in roles:
            print(f"Role: {role.name}")
            print(f"  ID: {role.id}")
            print(f"  Description: {role.description}")
            print(f"  Is System: {role.is_system}")
            print(f"  Permissions ({len(role.permissions)}):")
            for perm in role.permissions:
                print(f"    - {perm}")
            print()

if __name__ == "__main__":
    asyncio.run(main())
