#!/usr/bin/env python3
"""Test tenant creation and role assignment."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


async def test_tenant_and_roles():
    """Test tenant creation and role assignment."""
    base_url = "http://localhost:8000"
    
    # Login as super admin
    print("1. Logging in as super admin...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/auth/token",
            data={
                "username": "admin@bsmart.com",
                "password": "admin123"
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Test tenant creation
        print("\n2. Creating test tenant...")
        tenant_data = {
            "name": "Test Company",
            "slug": "test-company",
            "subscription_plan": "free",
            "max_users": 10,
            "max_projects": 5
        }
        
        response = await client.post(
            f"{base_url}/tenants",
            json=tenant_data,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Tenant created successfully")
            tenant = response.json()
            print(f"Tenant ID: {tenant['id']}")
        else:
            print(f"❌ Tenant creation failed")
        
        # List tenants
        print("\n3. Listing tenants...")
        response = await client.get(
            f"{base_url}/tenants",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            tenants = response.json()
            print(f"✅ Found {len(tenants)} tenants")
            for t in tenants:
                print(f"  - {t['name']} ({t['slug']})")
        
        # List users
        print("\n4. Listing users...")
        response = await client.get(
            f"{base_url}/users",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users")
            for u in users:
                print(f"  - {u['full_name']} ({u['email']})")
            
            if users:
                user_id = users[0]['id']
                
                # List roles
                print("\n5. Listing roles...")
                response = await client.get(
                    f"{base_url}/roles",
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    roles = response.json()
                    print(f"✅ Found {len(roles)} roles")
                    for r in roles:
                        print(f"  - {r['name']}: {r['description']}")
                    
                    if roles:
                        role_id = roles[0]['id']
                        
                        # Assign role to user
                        print(f"\n6. Assigning role {role_id} to user {user_id}...")
                        response = await client.post(
                            f"{base_url}/users/{user_id}/roles",
                            json={"role_id": role_id},
                            headers=headers
                        )
                        
                        print(f"Status: {response.status_code}")
                        print(f"Response: {response.text}")
                        
                        if response.status_code in [200, 201]:
                            print("✅ Role assigned successfully")
                        else:
                            print("❌ Role assignment failed")
                        
                        # Get user roles
                        print(f"\n7. Getting user roles...")
                        response = await client.get(
                            f"{base_url}/users/{user_id}/roles",
                            headers=headers
                        )
                        
                        print(f"Status: {response.status_code}")
                        if response.status_code == 200:
                            user_roles = response.json()
                            print(f"✅ User has {len(user_roles)} roles")
                            for r in user_roles:
                                print(f"  - {r['name']}")


if __name__ == "__main__":
    asyncio.run(test_tenant_and_roles())
