#!/usr/bin/env python3
"""Test PermissionService directly."""

import asyncio
from sqlalchemy import select
from services.shared.database import get_session
from services.identity.models import User
from services.identity.permission_service import PermissionService

async def test_service():
    """Test service."""
    
    async for session in get_session():
        try:
            # Get user
            result = await session.execute(
                select(User).where(User.email == "acme@acme.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User not found")
                return
            
            print(f"✅ Found user: {user.email}\n")
            
            # Test get_user_roles
            print("📋 Testing PermissionService.get_user_roles()...")
            roles = await PermissionService.get_user_roles(
                user=user,
                session=session
            )
            
            print(f"✅ Got {len(roles)} roles:")
            for role in roles:
                print(f"   - {role.name}: {len(role.permissions)} permissions")
            
            # Test get_user_permissions
            print(f"\n📋 Testing PermissionService.get_user_permissions()...")
            permissions = await PermissionService.get_user_permissions(
                user=user,
                session=session,
                use_cache=False
            )
            
            print(f"✅ Got {len(permissions)} permissions:")
            for perm in permissions[:10]:
                print(f"   - {perm}")
            if len(permissions) > 10:
                print(f"   ... and {len(permissions) - 10} more")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service())
