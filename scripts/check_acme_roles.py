#!/usr/bin/env python3
"""Check acme user roles."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import async_session_maker
from services.identity.models import User, UserRole, Role
from sqlmodel import select

async def main():
    async with async_session_maker() as session:
        # Find acme user
        result = await session.execute(
            select(User).where(User.email == "acme@acme.com")
        )
        acme = result.scalar_one_or_none()
        
        if not acme:
            print("❌ User acme@acme.com not found")
            return
        
        print(f"✅ Found user: {acme.email}")
        print(f"   Tenant ID: {acme.tenant_id}")
        print(f"   is_superuser: {acme.is_superuser}")
        
        # Find user roles
        result = await session.execute(
            select(UserRole).where(UserRole.user_id == acme.id)
        )
        user_roles = result.scalars().all()
        
        print(f"\n📋 User Roles: {len(user_roles)}")
        
        if len(user_roles) == 0:
            print("\n⚠️  No roles assigned to acme@acme.com!")
            print("   This is why the menu doesn't appear.")
            print("\n   Run: uv run python scripts/setup_user_permissions.py")
            return
        
        for ur in user_roles:
            # Get role details
            result = await session.execute(
                select(Role).where(Role.id == ur.role_id)
            )
            role = result.scalar_one_or_none()
            
            if role:
                print(f"\n  ✅ Role: {role.name}")
                print(f"     ID: {role.id}")
                print(f"     Description: {role.description}")
                print(f"     Permissions: {len(role.permissions)} items")
                for perm in role.permissions:
                    print(f"       - {perm}")

if __name__ == "__main__":
    asyncio.run(main())
