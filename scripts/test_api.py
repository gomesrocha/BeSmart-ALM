"""Test API endpoints."""
import asyncio

import httpx


async def test_api() -> None:
    """Test API endpoints."""
    base_url = "http://localhost:8086"

    async with httpx.AsyncClient() as client:
        print("🧪 Testing Bsmart-ALM API")
        print("=" * 60)

        # Test root endpoint
        print("\n1. Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")

        # Test health endpoint
        print("\n2. Testing health endpoint...")
        response = await client.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")

        # Test API info
        print("\n3. Testing API info endpoint...")
        response = await client.get(f"{base_url}/api/v1/info")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")

        # Test login
        print("\n4. Testing login...")
        login_data = {
            "email": "admin@test.com",
            "password": "admin123456",
        }
        response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            tokens = response.json()
            print(f"   ✅ Login successful!")
            print(f"   Access Token: {tokens['access_token'][:50]}...")
            access_token = tokens["access_token"]

            # Test /me endpoint
            print("\n5. Testing /me endpoint...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{base_url}/api/v1/auth/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user = response.json()
                print(f"   User: {user['full_name']} ({user['email']})")
                print(f"   Tenant ID: {user['tenant_id']}")

            # Test list roles
            print("\n6. Testing list roles...")
            response = await client.get(f"{base_url}/api/v1/roles", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                roles = response.json()
                print(f"   Found {len(roles)} roles:")
                for role in roles:
                    print(f"     - {role['name']}: {len(role['permissions'])} permissions")

            # Test list API tokens
            print("\n7. Testing list API tokens...")
            response = await client.get(
                f"{base_url}/api/v1/api-tokens", headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                tokens_list = response.json()
                print(f"   Found {len(tokens_list)} API tokens")

            # Test create API token
            print("\n8. Testing create API token...")
            token_data = {
                "name": "Test Integration Token",
                "scopes": ["project:read", "work_item:read"],
                "expires_in_days": 30,
            }
            response = await client.post(
                f"{base_url}/api/v1/api-tokens", json=token_data, headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                new_token = response.json()
                print(f"   ✅ Token created: {new_token['name']}")
                print(f"   Token: {new_token['token'][:30]}...")
                print(f"   Scopes: {new_token['scopes']}")

        else:
            print(f"   ❌ Login failed: {response.json()}")

        print("\n" + "=" * 60)
        print("✨ API testing complete!")


if __name__ == "__main__":
    asyncio.run(test_api())
