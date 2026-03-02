#!/usr/bin/env python3
"""Test login credentials for AI Orchestrator."""

import asyncio
import httpx
import sys

async def test_login(api_url: str, email: str, password: str):
    """Test login with given credentials."""
    print(f"\n🔐 Testing login...")
    print(f"   API URL: {api_url}")
    print(f"   Email: {email}")
    print(f"   Password: {'*' * len(password)}")
    
    async with httpx.AsyncClient() as client:
        try:
            login_url = f"{api_url}/auth/login"
            print(f"\n📡 POST {login_url}")
            
            response = await client.post(
                login_url,
                json={"email": email, "password": password},
                timeout=10.0
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token', '')
                print(f"\n✅ Login successful!")
                print(f"   Token: {token[:50]}...")
                
                # Test getting projects
                print(f"\n🔍 Testing projects endpoint...")
                projects_url = f"{api_url}/projects"
                print(f"   GET {projects_url}")
                
                projects_response = await client.get(
                    projects_url,
                    headers={'Authorization': f'Bearer {token}'},
                    timeout=10.0
                )
                
                print(f"   Status: {projects_response.status_code}")
                
                if projects_response.status_code == 200:
                    projects = projects_response.json()
                    if isinstance(projects, list):
                        print(f"\n✅ Got {len(projects)} projects!")
                        for p in projects[:3]:  # Show first 3
                            print(f"   - {p.get('name', 'N/A')} (ID: {p.get('id', 'N/A')})")
                    elif isinstance(projects, dict):
                        proj_list = projects.get('data', projects.get('projects', []))
                        print(f"\n✅ Got {len(proj_list)} projects!")
                        for p in proj_list[:3]:
                            print(f"   - {p.get('name', 'N/A')} (ID: {p.get('id', 'N/A')})")
                else:
                    print(f"\n❌ Failed to get projects: {projects_response.text}")
                    
            else:
                print(f"\n❌ Login failed!")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {e}")

async def main():
    """Main function."""
    if len(sys.argv) < 4:
        print("Usage: python test_login_credentials.py <api_url> <email> <password>")
        print("\nExample:")
        print("  python test_login_credentials.py http://localhost:8086/api/v1 admin@example.com admin123")
        sys.exit(1)
    
    api_url = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    await test_login(api_url, email, password)

if __name__ == "__main__":
    asyncio.run(main())
