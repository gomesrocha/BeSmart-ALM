#!/usr/bin/env python3
"""Script para verificar usuários no banco de dados"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import get_session
from services.identity.models import User
from sqlmodel import select

async def main():
    async for db in get_session():
        print("\n=== Usuários no banco de dados ===\n")
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("❌ Nenhum usuário encontrado no banco!")
            return
        
        for user in users:
            print(f"Email: {user.email}")
            print(f"  - ID: {user.id}")
            print(f"  - Nome: {user.full_name}")
            print(f"  - Tenant ID: {user.tenant_id}")
            print(f"  - Superuser: {user.is_superuser}")
            print(f"  - Ativo: {user.is_active}")
            print()
        break

if __name__ == "__main__":
    asyncio.run(main())
