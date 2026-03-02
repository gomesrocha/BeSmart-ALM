#!/usr/bin/env python3
"""
Script para testar o login do gomesrocha e verificar as permissões retornadas
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_and_permissions():
    print("=== TESTE DE LOGIN E PERMISSÕES - GOMESROCHA ===\n")
    
    # 1. Login
    print("1. Fazendo login...")
    login_data = {
        "username": "gomesrocha",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Erro no login: {response.text}")
            return
        
        tokens = response.json()
        access_token = tokens.get("access_token")
        print(f"   ✅ Login bem-sucedido!")
        print(f"   Token: {access_token[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # 2. Buscar informações do usuário
    print("\n2. Buscando informações do usuário (/auth/me)...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Dados do usuário:")
            print(f"      - ID: {user_data.get('id')}")
            print(f"      - Username: {user_data.get('username')}")
            print(f"      - Email: {user_data.get('email')}")
            print(f"      - Is Superuser: {user_data.get('is_superuser')}")
            print(f"      - Tenant ID: {user_data.get('tenant_id')}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Buscar permissões
    print("\n3. Buscando permissões (/auth/permissions)...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/permissions", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            perm_data = response.json()
            print(f"   ✅ Dados de permissões:")
            print(f"      - Is Super Admin: {perm_data.get('is_super_admin')}")
            print(f"      - Roles: {len(perm_data.get('roles', []))}")
            for role in perm_data.get('roles', []):
                print(f"         * {role.get('name')} ({role.get('display_name')})")
            print(f"      - Permissions: {len(perm_data.get('permissions', []))}")
            
            # Verificar se tem project:create
            permissions = perm_data.get('permissions', [])
            has_project_create = 'project:create' in permissions
            print(f"\n   🔍 Tem permissão 'project:create'? {has_project_create}")
            
            if not has_project_create:
                print(f"\n   ⚠️ PROBLEMA ENCONTRADO: Usuário NÃO tem permissão project:create!")
                print(f"   Permissões disponíveis:")
                for perm in sorted(permissions):
                    print(f"      - {perm}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_login_and_permissions()
