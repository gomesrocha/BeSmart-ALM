#!/usr/bin/env python3
"""
Script de diagnóstico completo do sistema de permissões.

Verifica:
1. Permissões de superadmin (gomesrocha)
2. Permissões de tenant admin (acme)
3. Roles disponíveis em cada tenant
4. Estrutura de user_roles
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def check_user(username):
    """Verifica informações completas de um usuário."""
    print_section(f"USUÁRIO: {username.upper()}")
    
    # 1. Dados básicos do usuário
    user = session.execute(text("""
        SELECT id, username, email, is_superuser, is_active, tenant_id, created_at
        FROM users 
        WHERE username = :username
    """), {"username": username}).fetchone()
    
    if not user:
        print(f"❌ Usuário '{username}' não encontrado!")
        return None
    
    user_id, username, email, is_superuser, is_active, tenant_id, created_at = user
    
    print(f"📋 Dados Básicos:")
    print(f"   ID: {user_id}")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Is Superuser: {is_superuser}")
    print(f"   Is Active: {is_active}")
    print(f"   Tenant ID: {tenant_id}")
    print(f"   Created: {created_at}")
    
    # 2. Tenant info
    if tenant_id:
        tenant = session.execute(text("""
            SELECT name, is_active
            FROM tenants
            WHERE id = :tenant_id
        """), {"tenant_id": tenant_id}).fetchone()
        
        if tenant:
            print(f"\n🏢 Tenant:")
            print(f"   Name: {tenant[0]}")
            print(f"   Active: {tenant[1]}")
    
    # 3. Roles do usuário
    print(f"\n👥 Roles Atribuídos:")
    user_roles = session.execute(text("""
        SELECT r.id, r.name, r.display_name, r.is_system, r.tenant_id, ur.project_id
        FROM user_roles ur
        JOIN roles r ON r.id = ur.role_id
        WHERE ur.user_id = :user_id
        ORDER BY r.name
    """), {"user_id": user_id}).fetchall()
    
    if not user_roles:
        print("   ⚠️ Nenhum role atribuído!")
    else:
        for role in user_roles:
            role_id, name, display_name, is_system, role_tenant_id, project_id = role
            scope = "Global" if not project_id else f"Project {project_id}"
            print(f"   • {name} ({display_name})")
            print(f"     - ID: {role_id}")
            print(f"     - System: {is_system}")
            print(f"     - Tenant: {role_tenant_id}")
            print(f"     - Scope: {scope}")
    
    # 4. Permissões do usuário
    print(f"\n🔐 Permissões:")
    
    if is_superuser:
        print("   ✅ SUPERUSER - Tem TODAS as permissões (*)")
    else:
        permissions = session.execute(text("""
            SELECT DISTINCT p.resource, p.action
            FROM permissions p
            JOIN role_permissions rp ON rp.permission_id = p.id
            JOIN user_roles ur ON ur.role_id = rp.role_id
            WHERE ur.user_id = :user_id
            ORDER BY p.resource, p.action
        """), {"user_id": user_id}).fetchall()
        
        if not permissions:
            print("   ⚠️ Nenhuma permissão encontrada!")
        else:
            # Agrupar por resource
            perms_by_resource = {}
            for perm in permissions:
                resource, action = perm
                if resource not in perms_by_resource:
                    perms_by_resource[resource] = []
                perms_by_resource[resource].append(action)
            
            for resource, actions in sorted(perms_by_resource.items()):
                print(f"   • {resource}:")
                for action in sorted(actions):
                    print(f"     - {action}")
    
    # 5. Verificar permissões específicas importantes
    print(f"\n🎯 Permissões Críticas:")
    critical_perms = [
        'project:create',
        'user:role:assign',
        'user:role:remove',
        'user:role:read',
        'tenant:create',
        'tenant:update',
    ]
    
    for perm in critical_perms:
        resource, action = perm.split(':')
        if is_superuser:
            status = "✅"
        else:
            has_perm = session.execute(text("""
                SELECT COUNT(*)
                FROM permissions p
                JOIN role_permissions rp ON rp.permission_id = p.id
                JOIN user_roles ur ON ur.role_id = rp.role_id
                WHERE ur.user_id = :user_id
                AND p.resource = :resource
                AND p.action = :action
            """), {"user_id": user_id, "resource": resource, "action": action}).scalar()
            status = "✅" if has_perm > 0 else "❌"
        
        print(f"   {status} {perm}")
    
    return user_id, tenant_id

def check_tenant_roles(tenant_id):
    """Verifica roles disponíveis em um tenant."""
    print_section(f"ROLES DO TENANT")
    
    roles = session.execute(text("""
        SELECT id, name, display_name, description, is_system
        FROM roles
        WHERE tenant_id = :tenant_id
        ORDER BY name
    """), {"tenant_id": tenant_id}).fetchall()
    
    if not roles:
        print("   ⚠️ Nenhum role encontrado neste tenant!")
    else:
        for role in roles:
            role_id, name, display_name, description, is_system = role
            print(f"\n   📌 {name} ({display_name})")
            print(f"      ID: {role_id}")
            print(f"      Description: {description}")
            print(f"      System: {is_system}")
            
            # Permissões do role
            perms = session.execute(text("""
                SELECT p.resource, p.action
                FROM permissions p
                JOIN role_permissions rp ON rp.permission_id = p.id
                WHERE rp.role_id = :role_id
                ORDER BY p.resource, p.action
            """), {"role_id": role_id}).fetchall()
            
            if perms:
                print(f"      Permissions ({len(perms)}):")
                for perm in perms[:5]:  # Mostrar apenas primeiras 5
                    print(f"        - {perm[0]}:{perm[1]}")
                if len(perms) > 5:
                    print(f"        ... e mais {len(perms) - 5}")

def check_system_roles():
    """Verifica roles de sistema (globais)."""
    print_section("ROLES DE SISTEMA (GLOBAIS)")
    
    roles = session.execute(text("""
        SELECT id, name, display_name, description, is_system
        FROM roles
        WHERE tenant_id IS NULL
        ORDER BY name
    """)).fetchall()
    
    if not roles:
        print("   ⚠️ Nenhum role de sistema encontrado!")
    else:
        for role in roles:
            role_id, name, display_name, description, is_system = role
            print(f"\n   📌 {name} ({display_name})")
            print(f"      ID: {role_id}")
            print(f"      Description: {description}")
            print(f"      System: {is_system}")

def main():
    print("\n" + "="*80)
    print("  DIAGNÓSTICO COMPLETO DO SISTEMA DE PERMISSÕES")
    print("="*80)
    
    # 1. Verificar superadmin (gomesrocha)
    gomesrocha_data = check_user("gomesrocha")
    
    # 2. Verificar tenant admin (acme)
    acme_data = check_user("acme")
    
    # 3. Verificar roles de sistema
    check_system_roles()
    
    # 4. Verificar roles do tenant ACME (se acme existe)
    if acme_data and acme_data[1]:
        check_tenant_roles(acme_data[1])
    
    # 5. Verificar roles do tenant de gomesrocha (se existe)
    if gomesrocha_data and gomesrocha_data[1]:
        check_tenant_roles(gomesrocha_data[1])
    
    # 6. Resumo final
    print_section("RESUMO E RECOMENDAÇÕES")
    
    print("📊 Estatísticas:")
    total_users = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
    total_roles = session.execute(text("SELECT COUNT(*) FROM roles")).scalar()
    total_permissions = session.execute(text("SELECT COUNT(*) FROM permissions")).scalar()
    total_user_roles = session.execute(text("SELECT COUNT(*) FROM user_roles")).scalar()
    
    print(f"   Total de usuários: {total_users}")
    print(f"   Total de roles: {total_roles}")
    print(f"   Total de permissões: {total_permissions}")
    print(f"   Total de atribuições: {total_user_roles}")
    
    print("\n🔍 Problemas Identificados:")
    
    # Verificar se gomesrocha tem roles
    if gomesrocha_data:
        gomesrocha_roles = session.execute(text("""
            SELECT COUNT(*) FROM user_roles WHERE user_id = :user_id
        """), {"user_id": gomesrocha_data[0]}).scalar()
        
        if gomesrocha_roles == 0:
            print("   ⚠️ Superadmin (gomesrocha) não tem roles atribuídos")
            print("      (Isso é OK se is_superuser=true, mas pode causar problemas)")
    
    # Verificar se acme tem permissões de admin
    if acme_data:
        acme_has_role_assign = session.execute(text("""
            SELECT COUNT(*)
            FROM permissions p
            JOIN role_permissions rp ON rp.permission_id = p.id
            JOIN user_roles ur ON ur.role_id = rp.role_id
            WHERE ur.user_id = :user_id
            AND p.resource = 'user'
            AND p.action = 'role:assign'
        """), {"user_id": acme_data[0]}).scalar()
        
        if acme_has_role_assign == 0:
            print("   ❌ Tenant admin (acme) NÃO tem permissão 'user:role:assign'")
            print("      Isso impede de gerenciar roles no tenant!")
    
    print("\n✅ Diagnóstico completo!")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
