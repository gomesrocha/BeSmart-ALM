#!/usr/bin/env python3
"""Reset gomesrocha password."""

import asyncio
from sqlalchemy import select
from services.shared.database import get_session
from services.identity.models import User
from services.identity.security import hash_password

async def reset_password():
    """Reset gomesrocha password."""
    
    async for session in get_session():
        try:
            print("🔧 Resetting gomesrocha password...\n")
            
            # Buscar usuário
            result = await session.execute(
                select(User).where(User.email == "gomesrocha@gmail.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User gomesrocha@gmail.com not found!")
                print("   Creating user...")
                
                # Criar usuário
                user = User(
                    email="gomesrocha@gmail.com",
                    full_name="Gomes Rocha",
                    hashed_password=hash_password("gomes123456"),
                    is_active=True,
                    is_superuser=True,
                    tenant_id=None  # Super admin não tem tenant
                )
                session.add(user)
                await session.commit()
                print("✅ User created!")
            else:
                print(f"✅ Found user: {user.email}")
                print(f"   Current is_superuser: {user.is_superuser}")
                
                # Resetar senha
                user.hashed_password = hash_password("gomes123456")
                user.is_superuser = True
                user.is_active = True
                await session.commit()
                print("✅ Password reset to: gomes123456")
                print("✅ Set as superuser")
            
            print("\n✅ Done! You can now login with:")
            print("   Email: gomesrocha@gmail.com")
            print("   Password: gomes123456")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(reset_password())
