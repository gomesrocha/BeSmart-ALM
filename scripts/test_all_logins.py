#!/usr/bin/env python3
"""Test all user logins."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


async def test_login(email: str, password: str, expected_superuser: bool):
    """Test login for a specific user."""
    base_url = "http://localhost:8086"
    
    print(f"\n{'='*60}")
    print(f"Testing: {email}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Login
            response = await client.post(
                f"{base_url}/api/v1/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code != 200:
                print(f"❌ Login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login successful!")
            
            # Get user info
            response = await client.get(
                f"{base_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                is_superuser = user_data.get('is_superuser', False)
                
                print(f"\n📋 User Info:")
                print(f"   - Email: {user_data.get('email')}")
                print(f"   - Name: {user_data.get('full_name')}")
                print(f"   - Tenant ID: {user_data.get('tenant_id')}")
                print(f"   - Is Superuser: {is_superuser}")
                
                if is_superuser == expected_superuser:
                    print(f"\n✅ Superuser status correct!")
                else:
                    print(f"\n❌ Superuser status incorrect!")
                    print(f"   Expected: {expected_superuser}, Got: {is_superuser}")
                
                return True
            else:
                print(f"❌ Failed to get user info: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def main():
    """Test all users."""
    print("\n" + "="*60)
    print("TESTING ALL USER LOGINS")
    print("="*60)
    
    results = []
    
    # Test super admins
    results.append(await test_login("gomesrocha@gmail.com", "gomes1234", True))
    results.append(await test_login("admin@test.com", "admin1234", True))
    
    # Test tenant admin
    results.append(await test_login("acme@acme.com", "acme1234", False))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n✅ Successful logins: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 All logins working correctly!")
    else:
        print("\n⚠️  Some logins failed. Check the output above.")


if __name__ == "__main__":
    asyncio.run(main())
