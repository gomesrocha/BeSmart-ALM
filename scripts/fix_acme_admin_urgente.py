#!/usr/bin/env python3
"""
CORREÇÃO URGENTE: Dar permissões completas para o tenant admin (acme)

Este script:
1. Cria role "Admin" no tenant ACME se não existir
2. Adiciona TODAS as permissões necessárias ao role Admin
3. Atribui o role Admin ao usuário acme
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def main():
    print("="*80)
    print("  CORREÇÃO URGENTE: Permissões do Tenant Admin (acme)")
    print("="*80 + "\n")
    
    # 1. Buscar usuário acme
    print("1. Buscando usuário acme...")
    user = session.execute(text("""
        SELECT id, username, email, tenant_id
        FROM users
        WHERE username = 'acme'
    """)).fetchone()
    
    if not user:
        print("   ❌ Usuário 'acme' não encontrado!")
        return
    
    user_id, username, email, tenant_id = user
    print(f"   ✅ Usuário encontrado:")
    print(f"      ID: {user_id}")
    print(f"      Tenant ID: {tenant_id}")
    
    # 2. Buscar ou criar role "Admin" no tenant
    print("\n2. Verificando role 'Admin' no tenant...")
    role = session.execute(text("""
        SELECT id, name
        FROM roles
        WHERE name = 'Admin' AND tenant_id = :tenant_id
    """), {"tenant_id": tenant_id}).fetchone()
    
    if role:
        role_id = role[0]
        print(f"   ✅ Role 'Admin' já existe (ID: {role_id})")
    else:
        print("   ⚠️ Role 'Admin' não existe, criando...")
        role_id = str(uuid4())
        session.execute(text("""
            INSERT INTO roles (id, name, display_name, description, tenant_id, is_system, created_at, updated_at)
            VALUES (:id, 'Admin', 'Administrator', 'Tenant Administrator with full permissions', :tenant_id, true, NOW(), NOW())
        """), {"id": role_id, "tenant_id": tenant_id})
        session.commit()
        print(f"   ✅ Role 'Admin' criado (ID: {role_id})")
    
    # 3. Buscar todas as permissões necessárias
    print("\n3. Adicionando permissões ao role Admin...")
    
    # Lista de permissões que um tenant admin precisa
    required_permissions = [
        ('project', 'create'),
        ('project', 'read'),
        ('project', 'update'),
        ('project', 'delete'),
        ('work_item', 'create'),
        ('work_item', 'read'),
        ('work_item', 'update'),
        ('work_item', 'delete'),
        ('user', 'read'),
        ('user', 'write'),
        ('user', 'delete'),
        ('user', 'role:assign'),
        ('user', 'role:remove'),
        ('user', 'role:read'),
        ('user', 'role:write'),
        ('role', 'read'),
        ('role', 'write'),
        ('role', 'delete'),
    ]
    
    permissions_added = 0
    for resource, action in required_permissions:
        # Buscar permissão
        perm = session.execute(text("""
            SELECT id FROM permissions
            WHERE resource = :resource AND action = :action
        """), {"resource": resource, "action": action}).fetchone()
        
        if not perm:
            print(f"   ⚠️ Permissão {resource}:{action} não existe no sistema!")
            continue
        
        perm_id = perm[0]
        
        # Verificar se já está associada ao role
        existing = session.execute(text("""
            SELECT id FROM role_permissions
            WHERE role_id = :role_id AND permission_id = :perm_id
        """), {"role_id": role_id, "perm_id": perm_id}).fetchone()
        
        if not existing:
            # Adicionar permissão ao role
            session.execute(text("""
                INSERT INTO role_permissions (id, role_id, permission_id, created_at)
                VALUES (:id, :role_id, :perm_id, NOW())
            """), {"id": str(uuid4()), "role_id": role_id, "perm_id": perm_id})
            permissions_added += 1
    
    session.commit()
    print(f"   ✅ {permissions_added} permissões adicionadas ao role Admin")
    
    # 4. Atribuir role ao usuário acme
    print("\n4. Atribuindo role Admin ao usuário acme...")
    
    # Verificar se já tem o role
    existing_user_role = session.execute(text("""
        SELECT id FROM user_roles
        WHERE user_id = :user_id AND role_id = :role_id
    """), {"user_id": user_id, "role_id": role_id}).fetchone()
    
    if existing_user_role:
        print("   ✅ Usuário já tem o role Admin")
    else:
        session.execute(text("""
            INSERT INTO user_roles (id, user_id, role_id, tenant_id, assigned_at)
            VALUES (:id, :user_id, :role_id, :tenant_id, NOW())
        """), {
            "id": str(uuid4()),
            "user_id": user_id,
            "role_id": role_id,
            "tenant_id": tenant_id
        })
        session.commit()
        print("   ✅ Role Admin atribuído ao usuário acme")
    
    # 5. Verificar permissões finais
    print("\n5. Verificando permissões finais do usuário acme...")
    perms = session.execute(text("""
        SELECT DISTINCT p.resource, p.action
        FROM permissions p
        JOIN role_permissions rp ON rp.permission_id = p.id
        JOIN user_roles ur ON ur.role_id = rp.role_id
        WHERE ur.user_id = :user_id
        ORDER BY p.resource, p.action
    """), {"user_id": user_id}).fetchall()
    
    print(f"   ✅ Total de permissões: {len(perms)}")
    
    # Verificar permissões críticas
    critical_perms = ['project:create', 'user:role:assign', 'user:role:read']
    print("\n   Permissões críticas:")
    for crit in critical_perms:
        resource, action = crit.split(':')
        has_it = any(p[0] == resource and p[1] == action for p in perms)
        status = "✅" if has_it else "❌"
        print(f"      {status} {crit}")
    
    print("\n" + "="*80)
    print("  ✅ CORREÇÃO CONCLUÍDA!")
    print("="*80)
    print("\nPróximos passos:")
    print("1. Faça logout e login novamente com o usuário 'acme'")
    print("2. Verifique se o botão 'New Project' aparece")
    print("3. Verifique se o menu 'User Roles' aparece no sidebar")
    print("4. Tente atribuir um role para outro usuário")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()
