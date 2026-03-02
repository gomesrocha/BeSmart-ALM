#!/usr/bin/env python3
"""Reset password for admin@test.com user."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from services.identity.security import hash_password

# Database connection
DATABASE_URL = "postgresql://bsmart:bsmart@localhost:5437/bsmart_alm"
engine = create_engine(DATABASE_URL)

def reset_password():
    """Reset password for admin@test.com."""
    email = "admin@test.com"
    new_password = "admin123"
    
    print(f"\n🔧 Resetting password for {email}...")
    
    # Hash the new password
    hashed_password = hash_password(new_password)
    
    with engine.connect() as conn:
        # Update password
        result = conn.execute(
            text("""
                UPDATE users 
                SET hashed_password = :hashed_password
                WHERE email = :email
            """),
            {"hashed_password": hashed_password, "email": email}
        )
        conn.commit()
        
        if result.rowcount > 0:
            print(f"✅ Password reset successfully!")
            print(f"\n📋 Login credentials:")
            print(f"   Email: {email}")
            print(f"   Password: {new_password}")
        else:
            print(f"❌ User not found: {email}")

if __name__ == "__main__":
    reset_password()
