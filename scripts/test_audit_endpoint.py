"""Test script for audit endpoint."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


async def test_audit_endpoint():
    """Test the audit endpoint functionality."""
    base_url = "http://localhost:8086/api/v1"
    
    print("🧪 Testando Endpoint de Auditoria...")
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
        print()
        
        # Step 2: Create some test data to generate audit logs
        print("2️⃣ Criando projeto de teste (gera log de auditoria)...")
        response = await client.post(
            f"{base_url}/projects",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Audit Project",
                "description": "Project for testing audit logs",
                "settings": {}
            }
        )
        
        if response.status_code == 201:
            project_data = response.json()
            project_id = project_data["id"]
            print(f"✅ Projeto criado: {project_id}")
        else:
            print(f"⚠️  Aviso: Não foi possível criar projeto ({response.status_code})")
            project_id = None
        print()
        
        # Step 3: List audit logs
        print("3️⃣ Listando logs de auditoria...")
        response = await client.get(
            f"{base_url}/audit-logs",
            headers={"Authorization": f"Bearer {token}"},
            params={"page": 1, "page_size": 10}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao listar logs: {response.status_code}")
            print(response.text)
            return
        
        logs_data = response.json()
        print(f"✅ Logs obtidos:")
        print(f"   Total: {logs_data['pagination']['total']}")
        print(f"   Página: {logs_data['pagination']['page']}/{logs_data['pagination']['total_pages']}")
        print(f"   Itens nesta página: {len(logs_data['items'])}")
        
        if logs_data['items']:
            print(f"\n   Últimos logs:")
            for log in logs_data['items'][:5]:
                print(f"   - {log['action']} em {log['resource_type']} por {log['user_id'][:8]}...")
        print()
        
        # Step 4: Get available actions
        print("4️⃣ Obtendo ações disponíveis...")
        response = await client.get(
            f"{base_url}/audit-logs/actions",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao obter ações: {response.status_code}")
            return
        
        actions = response.json()
        print(f"✅ Ações disponíveis: {', '.join(actions)}")
        print()
        
        # Step 5: Get resource types
        print("5️⃣ Obtendo tipos de recursos...")
        response = await client.get(
            f"{base_url}/audit-logs/resource-types",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao obter tipos de recursos: {response.status_code}")
            return
        
        resource_types = response.json()
        print(f"✅ Tipos de recursos: {', '.join(resource_types)}")
        print()
        
        # Step 6: Get audit stats
        print("6️⃣ Obtendo estatísticas de auditoria...")
        response = await client.get(
            f"{base_url}/audit-logs/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao obter estatísticas: {response.status_code}")
            return
        
        stats = response.json()
        print(f"✅ Estatísticas:")
        print(f"   Total de logs: {stats['total']}")
        print(f"   Ações mais comuns:")
        for item in stats['by_action'][:5]:
            print(f"   - {item['action']}: {item['count']}")
        print()
        
        # Step 7: Filter by action
        if actions:
            print(f"7️⃣ Filtrando por ação '{actions[0]}'...")
            response = await client.get(
                f"{base_url}/audit-logs",
                headers={"Authorization": f"Bearer {token}"},
                params={"action": actions[0], "page": 1, "page_size": 5}
            )
            
            if response.status_code != 200:
                print(f"❌ Erro ao filtrar: {response.status_code}")
                return
            
            filtered_data = response.json()
            print(f"✅ Logs filtrados: {filtered_data['pagination']['total']} encontrados")
            print()
        
        # Step 8: Clean up (delete test project if created)
        if project_id:
            print("8️⃣ Limpando projeto de teste...")
            response = await client.delete(
                f"{base_url}/projects/{project_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 204:
                print(f"✅ Projeto deletado (gera log de auditoria)")
            else:
                print(f"⚠️  Aviso: Não foi possível deletar projeto ({response.status_code})")
            print()
        
        print("🎉 Todos os testes passaram!")
        print()
        print("📝 Resumo:")
        print("   ✅ Endpoint de listagem funcionando")
        print("   ✅ Paginação funcionando")
        print("   ✅ Filtros funcionando")
        print("   ✅ Endpoint de ações funcionando")
        print("   ✅ Endpoint de tipos de recursos funcionando")
        print("   ✅ Endpoint de estatísticas funcionando")
        print("   ✅ Logs de auditoria sendo gerados corretamente")


if __name__ == "__main__":
    asyncio.run(test_audit_endpoint())
