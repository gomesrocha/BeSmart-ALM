"""Seed database with initial data for testing."""
import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from services.identity.models import Role, Tenant, User
from services.identity.permissions import create_default_roles
from services.identity.security import hash_password
from services.shared.database import async_session_maker, init_db


async def seed_database() -> None:
    """Seed database with initial test data."""
    print("🌱 Seeding database...")

    async with async_session_maker() as session:
        # Check if tenant already exists
        from sqlmodel import select
        result = await session.execute(select(Tenant).where(Tenant.slug == "test-org"))
        existing_tenant = result.scalar_one_or_none()
        
        if existing_tenant:
            print(f"✅ Tenant already exists: {existing_tenant.name} (ID: {existing_tenant.id})")
            tenant = existing_tenant
        else:
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

        # Get admin role
        admin_role = next(r for r in roles if r.name == "admin")
        dev_role = next(r for r in roles if r.name == "dev")
        po_role = next(r for r in roles if r.name == "po")

        # Check if users already exist
        result = await session.execute(select(User).where(User.email == "admin@test.com"))
        if result.scalar_one_or_none():
            print("✅ Users already exist")
        else:
            # Create admin user
            admin_user = User(
                id=uuid4(),
                tenant_id=tenant.id,
                email="admin@test.com",
                hashed_password=hash_password("admin123456"),
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
                email="dev@test.com",
                hashed_password=hash_password("dev123456"),
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
                email="po@test.com",
                hashed_password=hash_password("po123456"),
                full_name="Product Owner",
                is_active=True,
                is_superuser=False,
            )
            session.add(po_user)
            print(f"✅ Created PO user: {po_user.email}")

            await session.commit()

        print("\n📋 Test Credentials:")
        print("=" * 50)
        print(f"Admin: admin@test.com / admin123456")
        print(f"Developer: dev@test.com / dev123456")
        print(f"Product Owner: po@test.com / po123456")
        print("=" * 50)
        print(f"\nTenant ID: {tenant.id}")
        print(f"Admin Role ID: {admin_role.id}")
        print(f"Dev Role ID: {dev_role.id}")
        print(f"PO Role ID: {po_role.id}")


async def main() -> None:
    """Main function."""
    print("🚀 Initializing database...")
    await init_db()
    print("✅ Database initialized")

    await seed_database()
    print("\n✨ Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
