#!/usr/bin/env python3
"""Test AI Orchestrator endpoints."""

import requests
import json

BASE_URL = "http://localhost:5010"

def test_select_project():
    """Test select project endpoint."""
    print("🧪 Testing /api/select-project endpoint...")
    
    # First login
    login_data = {
        "api_url": "http://localhost:8086",
        "email": "admin@example.com",
        "password": "admin123",
        "repo_path": "~/bsmart-repos"
    }
    
    print("1️⃣ Logging in...")
    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Login successful")
    else:
        print(f"   ❌ Login failed: {response.text}")
        return
    
    # Select project
    print("\n2️⃣ Selecting project...")
    project_data = {"project_id": "1"}
    response = requests.post(
        f"{BASE_URL}/api/select-project",
        json=project_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Project selected: {data['project']['name']}")
    else:
        print(f"   ❌ Failed: {response.text}")
        return
    
    # Get work items
    print("\n3️⃣ Getting work items...")
    response = requests.get(f"{BASE_URL}/api/work-items")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Got {len(data['work_items'])} work items")
        for wi in data['work_items'][:3]:
            print(f"      - {wi['id']}: {wi['title']}")
    else:
        print(f"   ❌ Failed: {response.text}")

if __name__ == "__main__":
    test_select_project()
