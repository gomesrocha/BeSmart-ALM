#!/usr/bin/env python3
"""
Fix architecture enum value in database.
"""
import asyncio
from sqlalchemy import text
from services.shared.database import engine


async def fix_enum():
    """Check and fix architecture enum value."""
    
    print("=" * 80)
    print("🔧 Fixing Architecture Enum Value")
    print("=" * 80)
    
    async with engine.begin() as conn:
        # Check current enum values
        print("\n📊 Checking current enum values...")
        result = await conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid FROM pg_type WHERE typname = 'documentcategory'
            )
            ORDER BY enumlabel;
        """))
        
        values = [row[0] for row in result.fetchall()]
        print(f"Current values: {values}")
        
        # Check if 'architecture' exists
        if 'architecture' in values:
            print("✅ 'architecture' value already exists!")
        else:
            print("⚠️  'architecture' value not found, adding...")
            try:
                await conn.execute(text("""
                    ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'architecture';
                """))
                print("✅ Added 'architecture' value")
            except Exception as e:
                print(f"❌ Failed to add: {e}")
        
        # Verify again
        print("\n📊 Final enum values:")
        result = await conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid FROM pg_type WHERE typname = 'documentcategory'
            )
            ORDER BY enumlabel;
        """))
        
        values = [row[0] for row in result.fetchall()]
        for val in values:
            print(f"  ✓ {val}")
    
    print("\n" + "=" * 80)
    print("✅ Enum check complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(fix_enum())
