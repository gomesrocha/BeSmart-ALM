#!/usr/bin/env python3
"""Check Odair's roles."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import async_session_maker
from services.identity.models import User, UserRole, Role
from sqlmodel import select

async def main():
    async with async_session_maker() as session:
        # Find odair user
        result = await session.execute(
            select(User).where(User.email == "odair@acme.com")
        )
        odair = result.scalar_one_or_none()
        
        if not odair:
            print("❌ User odair@acme.com not found")
            return
        
        print(f"✅ Found user: {odair.email}")
        print(f"   ID: {odair.id}")
        print(f"   Tenant ID: {odair.tenant_id}\n")
        
        # Find user roles
        result = await session.execute(
            select(UserRole).where(UserRole.user_id == odair.id)
        )
        user_roles = result.scalars().all()
        
        print(f"📋 User Roles: {len(user_roles)}\n")
        
        if len(user_roles) == 0:
            print("⚠️  Odair não tem nenhuma role atribuída!")
            print("\nPara atribuir role 'Project Manager':")
            print("1. Login como acme@acme.com")
            print("2. Ir em 'User Roles'")
            print("3. Selecionar 'odair@acme.com'")
            print("4. Clicar em 'Assign Role'")
            print("5. Selecionar 'Project Manager'")
            return
        
        for ur in user_roles:
            # Get role details
            result = await session.execute(
                select(Role).where(Role.id == ur.role_id)
            )
            role = result.scalar_one_or_none()
            
            if role:
                print(f"Role: {role.name}")
                print(f"  ID: {role.id}")
                print(f"  Description: {role.description}")
                print(f"  Project ID: {ur.project_id or 'Global (tenant-wide)'}")
                print(f"  Permissions ({len(role.permissions)}):")
                for perm in role.permissions:
                    print(f"    - {perm}")
                print()

if __name__ == "__main__":
    asyncio.run(main())
