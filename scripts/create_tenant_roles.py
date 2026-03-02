#!/usr/bin/env python3
"""Create additional roles for tenants."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import async_session_maker
from services.identity.models import Role, Tenant
from sqlmodel import select

async def main():
    async with async_session_maker() as session:
        # Find Acme tenant
        result = await session.execute(
            select(Tenant).where(Tenant.slug.like("%acme%"))
        )
        acme_tenant = result.scalar_one_or_none()
        
        if not acme_tenant:
            print("❌ Tenant Acme not found")
            return
        
        print(f"✅ Found tenant: {acme_tenant.name}")
        print(f"   ID: {acme_tenant.id}")
        
        # Roles to create
        roles_to_create = [
            {
                "name": "Developer",
                "description": "Desenvolvedor - Pode criar e editar projetos e work items",
                "permissions": [
                    "project:read", "project:write", "project:create",
                    "workitem:read", "workitem:write", "workitem:create",
                    "user:read"
                ]
            },
            {
                "name": "Viewer",
                "description": "Visualizador - Pode apenas visualizar projetos e work items",
                "permissions": [
                    "project:read",
                    "workitem:read",
                    "user:read"
                ]
            },
            {
                "name": "Project Manager",
                "description": "Gerente de Projeto - Pode gerenciar projetos e work items",
                "permissions": [
                    "project:read", "project:write", "project:create", "project:delete",
                    "workitem:read", "workitem:write", "workitem:create", "workitem:delete",
                    "user:read"
                ]
            }
        ]
        
        print(f"\n📋 Creating roles for tenant {acme_tenant.name}...\n")
        
        for role_data in roles_to_create:
            # Check if role already exists
            result = await session.execute(
                select(Role).where(
                    Role.tenant_id == acme_tenant.id,
                    Role.name == role_data["name"]
                )
            )
            existing_role = result.scalar_one_or_none()
            
            if existing_role:
                print(f"⚠️  Role '{role_data['name']}' already exists - updating permissions")
                existing_role.description = role_data["description"]
                existing_role.permissions = role_data["permissions"]
                session.add(existing_role)
            else:
                new_role = Role(
                    tenant_id=acme_tenant.id,
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=role_data["permissions"],
                    is_system=False
                )
                session.add(new_role)
                print(f"✅ Created role: {role_data['name']}")
            
            print(f"   Description: {role_data['description']}")
            print(f"   Permissions: {len(role_data['permissions'])} items")
            print(f"   {role_data['permissions']}")
            print()
        
        await session.commit()
        
        print("="*60)
        print("✅ Roles created successfully!")
        print("="*60)
        print(f"\nTenant: {acme_tenant.name}")
        print("\nAvailable Roles:")
        print("  1. Admin - Administrador do tenant (já existia)")
        print("  2. Developer - Pode criar e editar projetos")
        print("  3. Viewer - Pode apenas visualizar")
        print("  4. Project Manager - Gerente de projetos")
        print("\nAgora você pode atribuir essas roles para odair@acme.com!")

if __name__ == "__main__":
    asyncio.run(main())
