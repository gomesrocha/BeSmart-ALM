#!/usr/bin/env python3
"""Test /auth/me endpoint."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


async def test_auth_me():
    """Test auth/me endpoint."""
    base_url = "http://localhost:8086"
    
    # First login
    print("1. Logging in with acme@acme.com...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/api/v1/auth/login",
                json={
                    "email": "acme@acme.com",
                    "password": "acme1234"
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return
            
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login successful!")
            
            # Now test /auth/me
            print("\n2. Testing /auth/me endpoint...")
            response = await client.get(
                f"{base_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print("✅ /auth/me successful!")
                print(f"\nUser Data:")
                print(f"  - ID: {user_data.get('id')}")
                print(f"  - Email: {user_data.get('email')}")
                print(f"  - Name: {user_data.get('full_name')}")
                print(f"  - Tenant ID: {user_data.get('tenant_id')}")
                print(f"  - Is Superuser: {user_data.get('is_superuser')}")
                print(f"  - Is Active: {user_data.get('is_active')}")
            else:
                print("❌ /auth/me failed")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_auth_me())
