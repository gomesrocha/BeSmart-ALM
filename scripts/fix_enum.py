#!/usr/bin/env python3
"""
Fix documentcategory enum to include 'architecture' value.
"""
import asyncio
from sqlalchemy import text
from services.shared.database import engine


async def fix_enum():
    """Add 'architecture' to documentcategory enum if missing."""
    
    print("=" * 80)
    print("🔧 Fixing documentcategory enum")
    print("=" * 80)
    
    async with engine.begin() as conn:
        # Check current values
        print("\n📋 Current enum values:")
        result = await conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid 
                FROM pg_type 
                WHERE typname = 'documentcategory'
            )
            ORDER BY enumsortorder;
        """))
        
        current_values = [row[0] for row in result.fetchall()]
        for value in current_values:
            print(f"  - {value}")
        
        # Check if 'architecture' exists
        if 'architecture' in current_values:
            print("\n✅ 'architecture' already exists in enum!")
            return
        
        print("\n⚠️  'architecture' NOT found in enum")
        print("🔄 Adding 'architecture' to enum...")
        
        # Add 'architecture'
        try:
            await conn.execute(text("""
                ALTER TYPE documentcategory ADD VALUE 'architecture';
            """))
            print("✅ Successfully added 'architecture' to enum!")
        except Exception as e:
            print(f"❌ Failed to add: {e}")
            raise
        
        # Verify
        print("\n📋 Updated enum values:")
        result = await conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid 
                FROM pg_type 
                WHERE typname = 'documentcategory'
            )
            ORDER BY enumsortorder;
        """))
        
        updated_values = [row[0] for row in result.fetchall()]
        for value in updated_values:
            marker = "✅" if value == 'architecture' else "  "
            print(f"  {marker} {value}")
    
    print("\n" + "=" * 80)
    print("🎉 Enum fix completed!")
    print("=" * 80)
    print("\n💡 Next steps:")
    print("  1. Restart your backend server")
    print("  2. Try generating architecture again")


if __name__ == "__main__":
    asyncio.run(fix_enum())
