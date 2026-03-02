#!/usr/bin/env python3
"""
Migration script to add new fields to project_document table.
Adds support for generated/editable documents.
"""
import asyncio
from sqlalchemy import text
from services.shared.database import engine


async def migrate():
    """Add new columns to project_document table."""
    
    migrations = [
        # Add is_generated column
        """
        ALTER TABLE project_document 
        ADD COLUMN IF NOT EXISTS is_generated BOOLEAN NOT NULL DEFAULT FALSE;
        """,
        
        # Add generated_from column
        """
        ALTER TABLE project_document 
        ADD COLUMN IF NOT EXISTS generated_from VARCHAR(50);
        """,
        
        # Add is_editable column
        """
        ALTER TABLE project_document 
        ADD COLUMN IF NOT EXISTS is_editable BOOLEAN NOT NULL DEFAULT TRUE;
        """,
        
        # Add version column
        """
        ALTER TABLE project_document 
        ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;
        """,
        
        # Add content column (for generated documents)
        """
        ALTER TABLE project_document 
        ADD COLUMN IF NOT EXISTS content TEXT;
        """,
        
        # Add new document categories (separate commands)
        """
        ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'generated';
        """,
        """
        ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'rag_source';
        """,
        """
        ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'architecture';
        """,
    ]
    
    async with engine.begin() as conn:
        print("🔄 Starting migration...")
        
        for i, migration in enumerate(migrations, 1):
            try:
                print(f"  [{i}/{len(migrations)}] Executing migration...")
                await conn.execute(text(migration))
                print(f"  ✅ Migration {i} completed")
            except Exception as e:
                # Some migrations might fail if already applied
                if "already exists" in str(e) or "duplicate key" in str(e):
                    print(f"  ⚠️  Migration {i} already applied, skipping")
                else:
                    print(f"  ❌ Migration {i} failed: {e}")
                    raise
        
        print("✅ All migrations completed successfully!")


async def verify():
    """Verify that all columns exist."""
    
    query = """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'project_document'
    AND column_name IN ('is_generated', 'generated_from', 'is_editable', 'version', 'content')
    ORDER BY column_name;
    """
    
    async with engine.begin() as conn:
        result = await conn.execute(text(query))
        columns = result.fetchall()
        
        print("\n📊 Verification:")
        print("-" * 80)
        
        if columns:
            for col in columns:
                print(f"  ✅ {col[0]:<20} {col[1]:<15} nullable={col[2]:<5} default={col[3]}")
        else:
            print("  ❌ No new columns found!")
        
        print("-" * 80)


async def main():
    """Main migration function."""
    print("=" * 80)
    print("🔧 Database Migration: Add Generated Document Fields")
    print("=" * 80)
    
    try:
        await migrate()
        await verify()
        
        print("\n" + "=" * 80)
        print("🎉 Migration completed successfully!")
        print("=" * 80)
        print("\n💡 Next steps:")
        print("  1. Restart your backend server")
        print("  2. Test generating specification and architecture")
        print("  3. Check that documents are saved correctly")
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ Migration failed: {e}")
        print("=" * 80)
        raise


if __name__ == "__main__":
    asyncio.run(main())
