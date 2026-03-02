#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carregar .env do diretório raiz
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Verificar usuário gomesrocha
print("=== USUÁRIO GOMESROCHA ===")
user = session.execute(text("""
    SELECT id, username, email, is_superuser, tenant_id 
    FROM users 
    WHERE username = 'gomesrocha'
""")).fetchone()

if user:
    print(f"ID: {user[0]}")
    print(f"Username: {user[1]}")
    print(f"Email: {user[2]}")
    print(f"Is Superuser: {user[3]}")
    print(f"Tenant ID: {user[4]}")
    
    user_id = user[0]
    
    # Verificar roles
    print("\n=== ROLES DO USUÁRIO ===")
    roles = session.execute(text("""
        SELECT r.id, r.name, r.is_system, r.tenant_id
        FROM roles r
        JOIN user_roles ur ON ur.role_id = r.id
        WHERE ur.user_id = :user_id
    """), {"user_id": user_id}).fetchall()
    
    for role in roles:
        print(f"Role: {role[1]} (ID: {role[0]}, is_system: {role[2]}, tenant_id: {role[3]})")
    
    # Verificar permissões
    print("\n=== PERMISSÕES DO USUÁRIO ===")
    perms = session.execute(text("""
        SELECT DISTINCT p.resource, p.action
        FROM permissions p
        JOIN role_permissions rp ON rp.permission_id = p.id
        JOIN user_roles ur ON ur.role_id = rp.role_id
        WHERE ur.user_id = :user_id
        ORDER BY p.resource, p.action
    """), {"user_id": user_id}).fetchall()
    
    for perm in perms:
        print(f"  {perm[0]}:{perm[1]}")
    
    # Verificar especificamente permissão de criar projeto
    print("\n=== PERMISSÃO PROJECT:CREATE ===")
    has_perm = session.execute(text("""
        SELECT COUNT(*)
        FROM permissions p
        JOIN role_permissions rp ON rp.permission_id = p.id
        JOIN user_roles ur ON ur.role_id = rp.role_id
        WHERE ur.user_id = :user_id
        AND p.resource = 'project'
        AND p.action = 'create'
    """), {"user_id": user_id}).scalar()
    
    print(f"Tem permissão project:create? {has_perm > 0}")
else:
    print("Usuário não encontrado!")

session.close()
