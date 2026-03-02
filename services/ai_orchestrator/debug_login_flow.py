#!/usr/bin/env python3
"""Debug login and project loading flow."""

import requests
import json

BASE_URL = "http://localhost:5010"

def debug_flow():
    """Test complete flow with detailed logging."""
    
    print("🔍 DEBUG: Testing complete flow\n")
    
    # Step 1: Login
    print("=" * 60)
    print("STEP 1: Login")
    print("=" * 60)
    
    login_data = {
        "api_url": "http://localhost:8086",
        "email": "gomesrocha@example.com",
        "password": "gomes1234",
        "repo_path": "/home/fabio/organizacao/repository/bsmart-alm"
    }
    
    print(f"POST {BASE_URL}/api/login")
    print(f"Data: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print("❌ Login failed!")
            return
        
        print("✅ Login successful!")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Get Projects
    print("\n" + "=" * 60)
    print("STEP 2: Get Projects")
    print("=" * 60)
    
    print(f"GET {BASE_URL}/api/projects")
    
    try:
        response = requests.get(f"{BASE_URL}/api/projects")
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print("❌ Failed to get projects!")
            return
        
        data = response.json()
        projects = data.get('projects', [])
        print(f"\n✅ Got {len(projects)} projects:")
        for p in projects:
            print(f"   - {p['id']}: {p['name']}")
        
    except Exception as e:
        print(f"❌ Get projects error: {e}")
        return
    
    # Step 3: Select Project
    if projects:
        print("\n" + "=" * 60)
        print("STEP 3: Select Project")
        print("=" * 60)
        
        project_id = projects[0]['id']
        print(f"POST {BASE_URL}/api/select-project")
        print(f"Data: {{'project_id': '{project_id}'}}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/select-project",
                json={"project_id": project_id}
            )
            print(f"\nStatus: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code != 200:
                print("❌ Failed to select project!")
                return
            
            print("✅ Project selected!")
            
        except Exception as e:
            print(f"❌ Select project error: {e}")
            return
    
    # Step 4: Get Work Items
    print("\n" + "=" * 60)
    print("STEP 4: Get Work Items")
    print("=" * 60)
    
    print(f"GET {BASE_URL}/api/work-items")
    
    try:
        response = requests.get(f"{BASE_URL}/api/work-items")
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print("❌ Failed to get work items!")
            return
        
        data = response.json()
        work_items = data.get('work_items', [])
        print(f"\n✅ Got {len(work_items)} work items:")
        for wi in work_items[:5]:
            print(f"   - {wi['id']}: {wi['title']}")
        
    except Exception as e:
        print(f"❌ Get work items error: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✅ ALL STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    debug_flow()
