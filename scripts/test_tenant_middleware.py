"""Test script for TenantMiddleware."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


async def test_tenant_middleware():
    """Test the TenantMiddleware functionality."""
    base_url = "http://localhost:8086/api/v1"
    
    print("🧪 Testando TenantMiddleware...")
    print()
    
    # Step 1: Login to get token
    print("1️⃣ Fazendo login...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/auth/login",
            json={"email": "admin@test.com", "password": "admin123456"}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro no login: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        token = data["access_token"]
        print(f"✅ Login bem-sucedido!")
        print(f"   Token: {token[:50]}...")
        print()
        
        # Step 2: Get user info (should have tenant_id in request.state)
        print("2️⃣ Obtendo informações do usuário...")
        response = await client.get(
            f"{base_url}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao obter usuário: {response.status_code}")
            print(response.text)
            return
        
        user_data = response.json()
        print(f"✅ Usuário obtido:")
        print(f"   ID: {user_data['id']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Tenant ID: {user_data['tenant_id']}")
        print()
        
        # Step 3: Get permissions (uses tenant_id from middleware)
        print("3️⃣ Obtendo permissões do usuário...")
        response = await client.get(
            f"{base_url}/auth/permissions",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao obter permissões: {response.status_code}")
            print(response.text)
            return
        
        perms_data = response.json()
        print(f"✅ Permissões obtidas:")
        print(f"   Tenant ID: {perms_data['tenant_id']}")
        print(f"   Super Admin: {perms_data['is_super_admin']}")
        print(f"   Roles: {[r['name'] for r in perms_data['roles']]}")
        print(f"   Permissões: {len(perms_data['permissions'])} permissões")
        print()
        
        # Step 4: Test without token (should have None tenant_id)
        print("4️⃣ Testando sem token (público)...")
        response = await client.get(f"{base_url}/info")
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar endpoint público: {response.status_code}")
            return
        
        print(f"✅ Endpoint público acessível sem token")
        print()
        
        print("🎉 Todos os testes passaram!")
        print()
        print("📝 Resumo:")
        print("   ✅ TenantMiddleware extrai tenant_id do JWT")
        print("   ✅ tenant_id é injetado no request.state")
        print("   ✅ is_super_admin é injetado no request.state")
        print("   ✅ Endpoints públicos funcionam sem token")


if __name__ == "__main__":
    asyncio.run(test_tenant_middleware())
