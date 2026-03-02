#!/usr/bin/env python3
"""Test login directly."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


async def test_login():
    """Test login endpoint."""
    base_url = "http://localhost:8086"
    
    # Test with acme@acme.com
    print("Testing login with acme@acme.com...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/api/v1/auth/login",
                json={
                    "email": "acme@acme.com",
                    "password": "acme1234"
                }
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Login successful!")
                data = response.json()
                print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
                print(f"Token Type: {data.get('token_type', 'N/A')}")
            else:
                print("❌ Login failed")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_login())
