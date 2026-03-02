"""Reset database and seed with initial data."""
import asyncio
import sys
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from services.identity.models import Role, Tenant, User
from services.identity.permissions import create_default_roles
from services.identity.security import hash_password
from services.shared.config import settings
from services.shared.database import async_session_maker, init_db


async def drop_all_tables() -> None:
    """Drop all tables from database."""
    print("🗑️  Dropping all tables...")
    
    from sqlmodel import SQLModel
    from services.identity.models import APIToken, Role, Tenant, User, UserRole
    from services.project.models import Project, ProjectMember
    from services.work_item.models import WorkItem, WorkItemApproval, WorkItemHistory, WorkItemLink
    from services.specification.models import ProjectSpecification, ProjectArchitecture
    
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )
    
    async with engine.begin() as conn:
        # Drop all tables using SQLModel metadata
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()
    print("✅ All tables dropped")


async def seed_database() -> None:
    """Seed database with initial test data."""
    print("\n🌱 Seeding database...")

    async with async_session_maker() as session:
        # Create test tenant
        tenant = Tenant(
            id=uuid4(),
            name="Test Organization",
            slug="test-org",
            settings={
                "target_cloud": "AWS",
                "mps_br_level": "G",
            },
            is_active=True,
        )
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
        print(f"✅ Created tenant: {tenant.name} (ID: {tenant.id})")

        # Create default roles
        roles = await create_default_roles(tenant.id, session)
        print(f"✅ Created {len(roles)} default roles")

        # Get roles
        admin_role = next(r for r in roles if r.name == "admin")
        dev_role = next(r for r in roles if r.name == "dev")
        po_role = next(r for r in roles if r.name == "po")

        # Create admin user
        admin_user = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
        )
        session.add(admin_user)
        print(f"✅ Created admin user: {admin_user.email}")

        # Create developer user
        dev_user = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email="dev@example.com",
            hashed_password=hash_password("dev123"),
            full_name="Developer User",
            is_active=True,
            is_superuser=False,
        )
        session.add(dev_user)
        print(f"✅ Created developer user: {dev_user.email}")

        # Create PO user
        po_user = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email="po@example.com",
            hashed_password=hash_password("po123"),
            full_name="Product Owner",
            is_active=True,
            is_superuser=False,
        )
        session.add(po_user)
        print(f"✅ Created PO user: {po_user.email}")

        await session.commit()

        print("\n📋 Test Credentials:")
        print("=" * 60)
        print(f"Admin:    admin@example.com / admin123")
        print(f"Dev:      dev@example.com / dev123")
        print(f"PO:       po@example.com / po123")
        print("=" * 60)
        print(f"\nTenant ID: {tenant.id}")
        print(f"Admin Role ID: {admin_role.id}")
        print(f"Dev Role ID: {dev_role.id}")
        print(f"PO Role ID: {po_role.id}")


async def main() -> None:
    """Main function."""
    print("🚀 Bsmart-ALM Database Reset & Seed")
    print("=" * 60)
    
    try:
        # Drop all tables
        await drop_all_tables()
        
        # Initialize database (create all tables)
        print("\n📦 Creating all tables...")
        await init_db()
        print("✅ All tables created")
        
        # Seed database
        await seed_database()
        
        print("\n✨ Database reset and seeding complete!")
        print("\n🚀 You can now start the backend:")
        print("   cd services")
        print("   uvicorn api_gateway.main:app --reload --port 8086")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
