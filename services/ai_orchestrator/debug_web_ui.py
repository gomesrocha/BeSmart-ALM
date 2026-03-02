#!/usr/bin/env python3
"""Debug web UI project loading."""

import asyncio
import httpx

async def test_web_ui():
    """Test web UI endpoints."""
    
    base_url = "http://localhost:5010"
    
    print("🔐 Step 1: Login via Web UI...")
    async with httpx.AsyncClient() as client:
        try:
            # Login
            response = await client.post(
                f"{base_url}/api/login",
                json={
                    "api_url": "http://localhost:8086/api/v1",
                    "email": "acme@acme.com",
                    "password": "acme1234",
                    "repo_path": "~/bsmart-repos"
                },
                timeout=10.0
            )
            
            print(f"Login Status: {response.status_code}")
            print(f"Login Response: {response.text[:300]}")
            
            if response.status_code != 200:
                print("❌ Login failed!")
                return
            
            print("✅ Login successful!\n")
            
            # Get projects
            print("📁 Step 2: Get projects...")
            response = await client.get(
                f"{base_url}/api/projects",
                timeout=10.0
            )
            
            print(f"Projects Status: {response.status_code}")
            print(f"Projects Response: {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                projects = data.get('projects', [])
                print(f"\n✅ Found {len(projects)} projects:")
                for p in projects:
                    print(f"  - {p.get('id')}: {p.get('name')}")
            else:
                print(f"❌ Failed to get projects: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🐝 BeeSmart: AI Orchestrator - Debug\n")
    print("Make sure the web UI is running on http://localhost:5010\n")
    asyncio.run(test_web_ui())
