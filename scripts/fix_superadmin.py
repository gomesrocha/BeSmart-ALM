#!/usr/bin/env python3
"""Fix superadmin users."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.models import User
from services.identity.security import hash_password
from services.shared.database import get_session


async def fix_superadmin():
    """Fix superadmin users."""
    print("🔧 Fixing superadmin users...\n")
    
    async for session in get_session():
        # Check admin@test.com
        result = await session.execute(
            select(User).where(User.email == "admin@test.com")
        )
        admin_test = result.scalar_one_or_none()
        
        if admin_test:
            print(f"✅ Found admin@test.com")
            print(f"   - ID: {admin_test.id}")
            print(f"   - Tenant ID: {admin_test.tenant_id}")
            print(f"   - is_superuser: {admin_test.is_superuser}")
            
            if not admin_test.is_superuser:
                print("   ⚠️  NOT a superuser! Fixing...")
                admin_test.is_superuser = True
                session.add(admin_test)
                await session.commit()
                print("   ✅ Fixed! Now is superuser")
            else:
                print("   ✅ Already a superuser")
        else:
            print("❌ admin@test.com not found")
        
        print()
        
        # Check admin@bsmart.com
        result = await session.execute(
            select(User).where(User.email == "admin@bsmart.com")
        )
        admin_bsmart = result.scalar_one_or_none()
        
        if admin_bsmart:
            print(f"✅ Found admin@bsmart.com")
            print(f"   - ID: {admin_bsmart.id}")
            print(f"   - Tenant ID: {admin_bsmart.tenant_id}")
            print(f"   - is_superuser: {admin_bsmart.is_superuser}")
            
            if not admin_bsmart.is_superuser:
                print("   ⚠️  NOT a superuser! Fixing...")
                admin_bsmart.is_superuser = True
                session.add(admin_bsmart)
                await session.commit()
                print("   ✅ Fixed! Now is superuser")
            else:
                print("   ✅ Already a superuser")
        else:
            print("❌ admin@bsmart.com not found")
        
        print()
        
        # Check gomesrocha@gmail.com
        result = await session.execute(
            select(User).where(User.email == "gomesrocha@gmail.com")
        )
        gomes = result.scalar_one_or_none()
        
        if gomes:
            print(f"✅ Found gomesrocha@gmail.com")
            print(f"   - ID: {gomes.id}")
            print(f"   - Tenant ID: {gomes.tenant_id}")
            print(f"   - is_superuser: {gomes.is_superuser}")
            
            if not gomes.is_superuser:
                print("   ⚠️  NOT a superuser! Fixing...")
                gomes.is_superuser = True
                session.add(gomes)
                await session.commit()
                print("   ✅ Fixed! Now is superuser")
            else:
                print("   ✅ Already a superuser")
        else:
            print("❌ gomesrocha@gmail.com not found")
            print("   Creating new superuser...")
            
            # Get the first tenant (or create one)
            result = await session.execute(select(User).limit(1))
            any_user = result.scalar_one_or_none()
            
            if any_user:
                tenant_id = any_user.tenant_id
            else:
                print("   ❌ No users found in database. Please run seed script first.")
                return
            
            # Create new superuser
            new_admin = User(
                email="gomesrocha@gmail.com",
                hashed_password=hash_password("admin123"),
                full_name="Gomes Rocha",
                is_active=True,
                is_superuser=True,
                tenant_id=tenant_id,
            )
            
            session.add(new_admin)
            await session.commit()
            await session.refresh(new_admin)
            
            print(f"   ✅ Created superuser gomesrocha@gmail.com")
            print(f"   - ID: {new_admin.id}")
            print(f"   - Password: admin123")
            print(f"   - Tenant ID: {new_admin.tenant_id}")
        
        print()
        print("=" * 60)
        print("✅ All superadmin users fixed!")
        print()
        print("You can now login with:")
        print("  - admin@test.com / admin123")
        print("  - admin@bsmart.com / admin123")
        print("  - gomesrocha@gmail.com / admin123")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(fix_superadmin())
