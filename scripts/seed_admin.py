import asyncio
import os

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.role import Role
from app.models.user import User
from app.utils.user_name import display_name_from_parts, split_display_name


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
        fn, ln = split_display_name(name)
        display = display_name_from_parts(fn, ln)
        if existing:
            existing.login_as = "admin"
            existing.role_id = admin_role.id
            existing.is_active = True
            if existing.name != display:
                existing.first_name = fn
                existing.last_name = ln
                existing.name = display
            if not existing.hashed_password:
                existing.hashed_password = get_password_hash(password)
        else:
            session.add(
                User(
                    first_name=fn,
                    last_name=ln,
                    name=display,
                    email=email,
                    phone=None,
                    country=None,
                    latitude=None,
                    longitude=None,
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
