#!/usr/bin/env python3
"""Check if roles have is_system flag."""

import asyncio
from sqlalchemy import select
from services.shared.database import get_session
from services.identity.models import Role

async def check_roles():
    """Check roles."""
    
    async for session in get_session():
        try:
            result = await session.execute(
                select(Role).where(Role.name.in_(["Tenant Admin", "Admin"]))
            )
            roles = result.scalars().all()
            
            print(f"📋 Found {len(roles)} roles:\n")
            for role in roles:
                print(f"Role: {role.name}")
                print(f"  ID: {role.id}")
                print(f"  Tenant ID: {role.tenant_id}")
                print(f"  is_system: {getattr(role, 'is_system', 'ATTRIBUTE NOT FOUND')}")
                print(f"  Permissions: {len(role.permissions)}")
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_roles())
