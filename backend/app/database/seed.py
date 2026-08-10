"""Database seed data."""

import asyncio
from datetime import datetime, timedelta
import uuid

from app.database.engine import AsyncSessionLocal
from app.models.user import User
from app.security import password_hasher


async def seed_database():
    """Seed database with initial data."""
    async with AsyncSessionLocal() as session:
        # Check if admin user exists
        existing = await session.execute(
            "SELECT * FROM users WHERE email = 'admin@website2video.com'"
        )
        if not existing.first():
            # Create admin user
            admin = User(
                id=uuid.uuid4(),
                email="admin@website2video.com",
                password_hash=password_hasher.hash_password("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_admin=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(admin)
            await session.commit()
            print("Admin user created: admin@website2video.com / admin123")
        
        # Create demo user
        existing = await session.execute(
            "SELECT * FROM users WHERE email = 'demo@website2video.com'"
        )
        if not existing.first():
            demo = User(
                id=uuid.uuid4(),
                email="demo@website2video.com",
                password_hash=password_hasher.hash_password("demo123"),
                full_name="Demo User",
                is_active=True,
                is_admin=False,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(demo)
            await session.commit()
            print("Demo user created: demo@website2video.com / demo123")


if __name__ == "__main__":
    asyncio.run(seed_database())