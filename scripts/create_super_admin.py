#!/usr/bin/env python3
"""
Script para criar/atualizar super admin no sistema RBAC.
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import select
from services.shared.database import get_db_session
from services.identity.models import User
from services.identity.security import hash_password


async def create_or_update_super_admin():
    """Cria ou atualiza o super admin."""
    async with get_db_session() as session:
        # Buscar usuário admin
        query = select(User).where(User.email == "admin@test.com")
        result = await session.execute(query)
        admin = result.scalar_one_or_none()
        
        if admin:
            # Atualizar para super admin
            if hasattr(admin, 'is_super_admin'):
                admin.is_super_admin = True
            admin.is_superuser = True
            session.add(admin)
            await session.commit()
            
            print("✅ Super admin atualizado:")
            print(f"   Email: {admin.email}")
            print(f"   Nome: {admin.full_name}")
            print(f"   is_superuser: {admin.is_superuser}")
            print(f"   is_super_admin: {getattr(admin, 'is_super_admin', 'N/A')}")
        else:
            print("❌ Usuário admin@test.com não encontrado")
            print("   Execute: uv run python scripts/seed_db.py")


async def main():
    """Função principal."""
    print("🔐 Configurando Super Admin...")
    print("")
    
    await create_or_update_super_admin()
    
    print("")
    print("📋 Credenciais de Acesso:")
    print("=" * 50)
    print("Super Admin:")
    print("  Email: admin@test.com")
    print("  Senha: admin123456")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
