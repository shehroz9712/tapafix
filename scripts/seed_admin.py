import asyncio
import os

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.role import Role
from app.models.user import User


async def seed_admin() -> None:
    email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@tapafix.local").strip().lower()
    password = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMe123!")
    name = os.getenv("DEFAULT_ADMIN_NAME", "System Admin").strip()

    async with AsyncSessionLocal() as session:
        role_result = await session.execute(select(Role).where(Role.name == "ADMIN"))
        admin_role = role_result.scalar_one_or_none()
        if not admin_role:
            admin_role = Role(
                name="ADMIN",
                description="System administrator",
                allows_self_registration=False,
            )
            session.add(admin_role)
            await session.flush()

        user_result = await session.execute(select(User).where(User.email == email))
        existing = user_result.scalar_one_or_none()
        if existing:
            existing.login_as = "admin"
            existing.role_id = admin_role.id
            existing.is_active = True
            if existing.name != name:
                existing.name = name
            if not existing.hashed_password:
                existing.hashed_password = get_password_hash(password)
        else:
            session.add(
                User(
                    name=name,
                    email=email,
                    phone=None,
                    hashed_password=get_password_hash(password),
                    provider="email",
                    provider_id=None,
                    avatar_url=None,
                    login_as="admin",
                    role_id=admin_role.id,
                    is_active=True,
                    is_verified=True,
                )
            )
        await session.commit()
    print(f"Admin user is ready: {email}")


if __name__ == "__main__":
    asyncio.run(seed_admin())
