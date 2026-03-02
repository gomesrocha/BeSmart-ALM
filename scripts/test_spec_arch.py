#!/usr/bin/env python3
"""
Script de teste para endpoints de Especificação e Arquitetura
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8086/api/v1"

# Credenciais de teste
TEST_USER = {
    "email": "admin@example.com",
    "password": "admin123"
}

async def login():
    """Faz login e retorna o token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful: {data['user']['email']}")
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None

async def get_projects(token):
    """Lista projetos"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Found {len(projects)} projects")
            return projects
        else:
            print(f"❌ Failed to get projects: {response.status_code}")
            return []

async def test_generate_specification(token, project_id):
    """Testa geração de especificação"""
    print(f"\n🔄 Testing specification generation for project {project_id}...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/specification/generate",
                headers={"Authorization": f"Bearer {token}"},
                json={"project_id": project_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                spec_length = len(data.get('specification', ''))
                print(f"✅ Specification generated successfully!")
                print(f"   - Length: {spec_length} characters")
                print(f"   - Version: {data.get('version', 'N/A')}")
                print(f"\n📄 Preview (first 500 chars):")
                print("-" * 80)
                print(data.get('specification', '')[:500])
                print("-" * 80)
                return True
            else:
                print(f"❌ Failed to generate specification: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during specification generation: {str(e)}")
            return False

async def test_generate_architecture(token, project_id):
    """Testa geração de arquitetura"""
    print(f"\n🔄 Testing architecture generation for project {project_id}...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/specification/architecture/generate",
                headers={"Authorization": f"Bearer {token}"},
                json={"project_id": project_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                arch_length = len(data.get('architecture', ''))
                diagrams = data.get('diagrams', [])
                print(f"✅ Architecture generated successfully!")
                print(f"   - Length: {arch_length} characters")
                print(f"   - Diagrams: {len(diagrams)}")
                print(f"   - Version: {data.get('version', 'N/A')}")
                
                if diagrams:
                    print(f"\n📊 Mermaid Diagrams Found:")
                    for i, diagram in enumerate(diagrams, 1):
                        print(f"   {i}. Diagram {i} ({len(diagram)} chars)")
                
                print(f"\n🏗️ Preview (first 500 chars):")
                print("-" * 80)
                print(data.get('architecture', '')[:500])
                print("-" * 80)
                return True
            else:
                print(f"❌ Failed to generate architecture: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during architecture generation: {str(e)}")
            return False

async def main():
    """Função principal"""
    print("=" * 80)
    print("🧪 Testing Specification and Architecture Endpoints")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)
    
    # 1. Login
    print("\n1️⃣ Step 1: Login")
    token = await login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # 2. Get projects
    print("\n2️⃣ Step 2: Get Projects")
    projects = await get_projects(token)
    if not projects:
        print("\n⚠️ No projects found. Please create a project first.")
        return
    
    # Use first project
    project = projects[0]
    project_id = project['id']
    print(f"\n📁 Using project: {project['name']} (ID: {project_id})")
    
    # 3. Test specification generation
    print("\n3️⃣ Step 3: Generate Specification")
    spec_success = await test_generate_specification(token, project_id)
    
    # 4. Test architecture generation
    print("\n4️⃣ Step 4: Generate Architecture")
    arch_success = await test_generate_architecture(token, project_id)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    print(f"Login: ✅")
    print(f"Get Projects: ✅")
    print(f"Generate Specification: {'✅' if spec_success else '❌'}")
    print(f"Generate Architecture: {'✅' if arch_success else '❌'}")
    print("=" * 80)
    
    if spec_success and arch_success:
        print("\n🎉 All tests passed! System is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    asyncio.run(main())
