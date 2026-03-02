#!/usr/bin/env python3
"""Test API connection and project retrieval."""

import asyncio
import httpx
import sys

async def test_api():
    """Test API connection."""
    
    # Test 1: Login
    print("🔐 Testing login...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8086/api/v1/auth/login",
                json={"email": "acme@acme.com", "password": "acme1234"},
                timeout=10.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                print(f"✅ Login successful! Token: {token[:20]}...")
                
                # Test 2: Get projects
                print("\n📁 Testing projects endpoint...")
                response = await client.get(
                    "http://localhost:8086/api/v1/projects",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
                if response.status_code == 200:
                    projects = response.json()
                    print(f"\n✅ Found {len(projects)} projects:")
                    for p in projects:
                        print(f"  - {p.get('id')}: {p.get('name')}")
                else:
                    print(f"❌ Failed to get projects: {response.status_code}")
            else:
                print(f"❌ Login failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())
