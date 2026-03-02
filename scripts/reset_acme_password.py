#!/usr/bin/env python3
"""Reset acme user password."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import async_session_maker
from services.identity.models import User
from services.identity.security import hash_password
from sqlmodel import select

async def main():
    async with async_session_maker() as session:
        # Find acme user
        result = await session.execute(
            select(User).where(User.email == "acme@acme.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User acme@acme.com not found")
            return
        
        # Reset password
        new_password = "acme1234"
        user.hashed_password = hash_password(new_password)
        user.is_active = True
        
        session.add(user)
        await session.commit()
        
        print(f"✅ Password reset successfully!")
        print(f"   Email: {user.email}")
        print(f"   Password: {new_password}")

if __name__ == "__main__":
    asyncio.run(main())
