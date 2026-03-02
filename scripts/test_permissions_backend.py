#!/usr/bin/env python3
"""
Testa o que o backend está retornando para cada tipo de usuário.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
# Converter para async
ASYNC_DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

async def test_user_permissions(username: str):
    """Testa permissões de um usuário."""
    print(f"\n{'='*80}")
    print(f"  TESTANDO: {username}")
    print(f"{'='*80}\n")
    
    # Criar engine async
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Buscar usuário
        result = await conn.execute(
            text("SELECT id, username, email, is_superuser, tenant_id FROM users WHERE username = :username"),
            {"username": username}
        )
        user_row = result.fetchone()
        
        if not user_row:
            print(f"❌ Usuário '{username}' não encontrado!")
            return
        
        user_id, username, email, is_superuser, tenant_id = user_row
        
        print(f"📋 Usuário:")
        print(f"   ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Is Superuser: {is_superuser}")
        print(f"   Tenant ID: {tenant_id}")
        
        # Simular o que o PermissionService faz
        print(f"\n🔍 Simulando PermissionService.get_user_permissions():")
        
        if is_superuser:
            print(f"   ✅ É superuser - retornaria: ['*']")
            permissions = ["*"]
        else:
            # Buscar permissões reais
            result = await conn.execute(text("""
                SELECT DISTINCT p.resource || ':' || p.action as permission
                FROM permissions p
                JOIN role_permissions rp ON rp.permission_id = p.id
                JOIN user_roles ur ON ur.role_id = rp.role_id
                WHERE ur.user_id = :user_id
                ORDER BY permission
            """), {"user_id": user_id})
            
            permissions = [row[0] for row in result.fetchall()]
            print(f"   📋 Permissões do banco: {len(permissions)} permissões")
            if permissions:
                print(f"   Primeiras 10:")
                for perm in permissions[:10]:
                    print(f"      - {perm}")
                if len(permissions) > 10:
                    print(f"      ... e mais {len(permissions) - 10}")
            else:
                print(f"   ⚠️ NENHUMA permissão encontrada!")
        
        # Buscar roles
        result = await conn.execute(text("""
            SELECT r.id, r.name, r.display_name, r.description
            FROM roles r
            JOIN user_roles ur ON ur.role_id = r.id
            WHERE ur.user_id = :user_id
            ORDER BY r.name
        """), {"user_id": user_id})
        
        roles = result.fetchall()
        print(f"\n👥 Roles: {len(roles)} roles")
        for role in roles:
            role_id, name, display_name, description = role
            print(f"   - {name} ({display_name})")
        
        if not roles:
            print(f"   ⚠️ NENHUM role encontrado!")
        
        # Simular resposta do endpoint /auth/permissions
        print(f"\n📤 Resposta simulada do endpoint /auth/permissions:")
        response = {
            "user_id": str(user_id),
            "email": email,
            "tenant_id": str(tenant_id) if tenant_id else None,
            "is_super_admin": is_superuser,
            "permissions": permissions,
            "roles": [
                {
                    "id": str(role[0]),
                    "name": role[1],
                    "display_name": role[2],
                    "description": role[3],
                }
                for role in roles
            ],
        }
        
        import json
        print(json.dumps(response, indent=2))
    
    await engine.dispose()

async def main():
    print("\n" + "="*80)
    print("  TESTE DE PERMISSÕES DO BACKEND")
    print("="*80)
    
    # Testar superadmin
    await test_user_permissions("gomesrocha")
    
    # Testar tenant admin
    await test_user_permissions("acme")
    
    print("\n" + "="*80)
    print("  TESTE COMPLETO")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
