#!/usr/bin/env python3
"""Test permissions for frontend users."""

import asyncio
import httpx

async def test_user_permissions(email: str, password: str):
    """Test permissions for a user."""
    
    print(f"\n🔐 Testing permissions for: {email}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Login
            response = await client.post(
                "http://localhost:8086/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=10.0
            )
            
            if response.status_code != 200:
                print(f"❌ Login failed: {response.status_code}")
                return
            
            token = response.json().get('access_token')
            print(f"✅ Login successful")
            
            # Get user info
            response = await client.get(
                "http://localhost:8086/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            user_data = response.json()
            print(f"👤 User: {user_data.get('email')}")
            print(f"   is_superuser: {user_data.get('is_superuser')}")
            print(f"   tenant_id: {user_data.get('tenant_id')}")
            
            # Get permissions
            response = await client.get(
                "http://localhost:8086/api/v1/auth/permissions",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            perm_data = response.json()
            print(f"\n📋 Permissions:")
            print(f"   is_super_admin: {perm_data.get('is_super_admin')}")
            print(f"   roles: {len(perm_data.get('roles', []))}")
            
            for role in perm_data.get('roles', []):
                print(f"     - {role.get('name')}: {len(role.get('permissions', []))} permissions")
            
            permissions = perm_data.get('permissions', [])
            print(f"   total permissions: {len(permissions)}")
            
            # Check specific permissions
            key_perms = ['project:create', 'project:read', 'user:role:assign']
            print(f"\n🔑 Key permissions:")
            for perm in key_perms:
                has_it = perm in permissions
                icon = "✅" if has_it else "❌"
                print(f"   {icon} {perm}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Test multiple users."""
    
    users = [
        ("superadmin@bsmart.com", "superadmin123"),
        ("acme@acme.com", "acme1234"),
    ]
    
    for email, password in users:
        await test_user_permissions(email, password)

if __name__ == "__main__":
    asyncio.run(main())
