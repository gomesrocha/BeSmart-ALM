#!/usr/bin/env python3
"""
Script para criar roles padrão no sistema RBAC.

Este script cria os perfis de usuário padrão com suas respectivas permissões:
- Super Admin: Acesso total ao sistema
- Company Admin: Gerencia empresa e usuários
- Project Manager: Gerencia projetos e work items
- PO/Analyst: Gerencia requisitos e especificações
- Architect: Gerencia arquitetura
- Developer: Implementa work items
- QA: Testa work items
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import select
from services.shared.database import get_db_session
from services.identity.models import Role, Tenant
from datetime import datetime
from uuid import uuid4


# Definição dos roles e suas permissões
ROLES_DATA = {
    'super_admin': {
        'display_name': 'Super Administrator',
        'description': 'Administrador geral do sistema com acesso total',
        'level': 1,
        'is_system': True,
        'permissions': [
            '*',  # Todas as permissões
            'tenant.create',
            'tenant.read',
            'tenant.update',
            'tenant.delete',
            'tenant.*.all',
        ]
    },
    
    'company_admin': {
        'display_name': 'Company Administrator',
        'description': 'Administrador da empresa, gerencia usuários e projetos',
        'level': 2,
        'is_system': True,
        'permissions': [
            'user.create',
            'user.read',
            'user.update',
            'user.delete',
            'user.role.assign',
            'project.create',
            'project.read',
            'project.update',
            'project.delete',
            'workitem.read',
            'audit.read',
        ]
    },
    
    'project_manager': {
        'display_name': 'Project Manager',
        'description': 'Gerente de projetos, cria e gerencia projetos e work items',
        'level': 3,
        'is_system': True,
        'permissions': [
            'project.create',
            'project.read',
            'project.update',
            'project.member.add',
            'project.member.remove',
            'workitem.create',
            'workitem.read',
            'workitem.update',
            'workitem.delete',
            'workitem.assign',
            'document.read',
        ]
    },
    
    'po_analyst': {
        'display_name': 'Product Owner / Requirements Analyst',
        'description': 'Analista de requisitos, gerencia documentos e especificações',
        'level': 4,
        'is_system': True,
        'permissions': [
            'project.read',
            'document.upload',
            'document.read',
            'document.update',
            'requirements.generate',
            'requirements.approve',
            'requirements.reject',
            'specification.generate',
            'specification.read',
            'specification.update',
            'workitem.read',
            'workitem.create',
        ]
    },
    
    'architect': {
        'display_name': 'Software Architect',
        'description': 'Arquiteto de software, gerencia arquitetura do sistema',
        'level': 5,
        'is_system': True,
        'permissions': [
            'project.read',
            'specification.read',
            'architecture.generate',
            'architecture.update',
            'architecture.read',
            'workitem.read',
            'document.read',
        ]
    },
    
    'developer': {
        'display_name': 'Developer',
        'description': 'Desenvolvedor, implementa work items',
        'level': 6,
        'is_system': True,
        'permissions': [
            'project.read',
            'workitem.read',
            'workitem.update.own',  # Apenas work items atribuídos
            'workitem.status.in_progress',
            'workitem.status.done',
            'document.read',
            'specification.read',
            'architecture.read',
        ]
    },
    
    'qa': {
        'display_name': 'Quality Assurance',
        'description': 'Analista de qualidade, testa work items',
        'level': 7,
        'is_system': True,
        'permissions': [
            'project.read',
            'workitem.read',
            'workitem.update.own',  # Apenas work items atribuídos
            'workitem.status.approved',
            'workitem.status.rejected',
            'workitem.test',
            'document.read',
            'specification.read',
        ]
    },
}


async def get_default_tenant(session):
    """Obtém o tenant padrão ou cria um se não existir."""
    query = select(Tenant).limit(1)
    result = await session.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        print("  ⚠️  Nenhum tenant encontrado, criando tenant padrão...")
        tenant = Tenant(
            id=uuid4(),
            name="Default Company",
            slug="default",
            is_active=True
        )
        session.add(tenant)
        await session.flush()
        print(f"  ✅ Tenant padrão criado: {tenant.name}")
    
    return tenant


async def create_role(session, tenant_id, name: str, data: dict) -> Role:
    """Cria um role no banco de dados."""
    role = Role(
        id=uuid4(),
        tenant_id=tenant_id,
        name=name,
        display_name=data.get('display_name'),
        description=data['description'],
        level=data['level'],
        is_system=data['is_system'],
        permissions=data['permissions'],
    )
    
    session.add(role)
    return role


async def role_exists(session, tenant_id, name: str) -> bool:
    """Verifica se um role já existe."""
    query = select(Role).where(
        Role.tenant_id == tenant_id,
        Role.name == name
    )
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None


async def seed_roles():
    """Cria todos os roles padrão."""
    async with get_db_session() as session:
        # Obter tenant padrão
        tenant = await get_default_tenant(session)
        
        created_count = 0
        skipped_count = 0
        
        for role_name, role_data in ROLES_DATA.items():
            if await role_exists(session, tenant.id, role_name):
                print(f"⏭️  Role '{role_name}' já existe, pulando...")
                skipped_count += 1
                continue
            
            role = await create_role(session, tenant.id, role_name, role_data)
            print(f"✅ Role '{role_name}' criado: {role_data['display_name']}")
            print(f"   Permissões: {len(role_data['permissions'])} permissões")
            created_count += 1
        
        print("")
        print(f"📊 Resumo:")
        print(f"   ✅ Criados: {created_count} roles")
        print(f"   ⏭️  Pulados: {skipped_count} roles")
        print(f"   📋 Total: {len(ROLES_DATA)} roles definidos")


async def list_roles():
    """Lista todos os roles criados."""
    async with get_db_session() as session:
        query = select(Role).order_by(Role.name)
        result = await session.execute(query)
        roles = result.scalars().all()
        
        if not roles:
            print("❌ Nenhum role encontrado")
            return
        
        print("📋 Roles criados:")
        print("")
        
        for role in roles:
            display = getattr(role, 'display_name', role.name)
            level = getattr(role, 'level', 'N/A')
            print(f"🔹 {role.name} ({display})")
            print(f"   Level: {level}")
            print(f"   Permissões: {len(role.permissions)}")
            print(f"   Sistema: {'Sim' if role.is_system else 'Não'}")
            print(f"   Tenant: {role.tenant_id}")
            print("")


async def show_permissions():
    """Mostra todas as permissões por role."""
    async with get_db_session() as session:
        query = select(Role).order_by(Role.name)
        result = await session.execute(query)
        roles = result.scalars().all()
        
        print("🔐 Permissões por Role:")
        print("")
        
        for role in roles:
            display = getattr(role, 'display_name', role.name)
            print(f"📋 {display} ({role.name})")
            print("   Permissões:")
            
            for perm in sorted(role.permissions):
                print(f"     • {perm}")
            
            print("")


async def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciar roles do sistema RBAC')
    parser.add_argument('action', choices=['seed', 'list', 'permissions'], 
                       help='Ação a executar')
    
    args = parser.parse_args()
    
    print("🔐 Gerenciador de Roles RBAC")
    print("")
    
    try:
        if args.action == 'seed':
            print("🌱 Criando roles padrão...")
            await seed_roles()
            
        elif args.action == 'list':
            await list_roles()
            
        elif args.action == 'permissions':
            await show_permissions()
            
        print("")
        print("✅ Operação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
