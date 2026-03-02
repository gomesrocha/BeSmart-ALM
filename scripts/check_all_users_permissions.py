#!/usr/bin/env python3
"""Check permissions for all test users."""

import asyncio
import httpx

async def check_user(email: str, password: str):
    """Check user permissions."""
    
    print(f"\n{'='*60}")
    print(f"👤 User: {email}")
    print(f"{'='*60}")
    
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
                print(f"   Response: {response.text}")
                return
            
            token = response.json().get('access_token')
            print(f"✅ Login successful")
            
            # Get permissions
            response = await client.get(
                "http://localhost:8086/api/v1/auth/permissions",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            data = response.json()
            
            print(f"\n📊 Summary:")
            print(f"   is_super_admin: {data.get('is_super_admin')}")
            print(f"   tenant_id: {data.get('tenant_id')}")
            print(f"   roles: {len(data.get('roles', []))}")
            print(f"   permissions: {len(data.get('permissions', []))}")
            
            if data.get('roles'):
                print(f"\n🎭 Roles:")
                for role in data.get('roles', []):
                    print(f"   - {role.get('name')}")
            
            if data.get('permissions'):
                print(f"\n🔑 Key Permissions:")
                key_perms = [
                    'project:create', 'project:read', 'project:update', 'project:delete',
                    'user:role:assign', 'user:role:remove',
                    'tenant:create', 'tenant:read'
                ]
                for perm in key_perms:
                    has_it = perm in data.get('permissions', [])
                    icon = "✅" if has_it else "❌"
                    print(f"   {icon} {perm}")
            else:
                print(f"\n❌ NO PERMISSIONS!")
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Check all users."""
    
    users = [
        ("gomesrocha@gmail.com", "gomes123456"),
        ("acme@acme.com", "acme1234"),
        ("odair@acme.com", "odair1234"),
    ]
    
    for email, password in users:
        await check_user(email, password)
    
    print(f"\n{'='*60}")
    print("✅ Check complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())
