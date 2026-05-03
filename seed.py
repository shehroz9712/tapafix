import asyncio

from sqlalchemy import func, select

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal, engine
from app.models.category import Category
from app.models.role import Role
from app.models.subcategory import SubCategory
from app.models.user import User
from app.utils.user_name import display_name_from_parts, split_display_name

DEFAULT_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "name": "Admin",
        "country": "US",
        "login_as": "admin",
    },
    {
        "email": "provider@example.com",
        "password": "provider123",
        "name": "Provider",
        "country": "US",
        "login_as": "provider",
    },
    {
        "email": "user@example.com",
        "password": "user123",
        "name": "User",
        "country": "US",
        "login_as": "user",
    },
]

CATEGORY_TREE = {
    "Electronics": ["Mobile", "Laptop"],
    "Vehicles": ["Car", "Bike"],
    "Real Estate": ["Plot", "Apartment"],
}


async def ensure_admin_role(session) -> Role:
    result = await session.execute(
        select(Role).where(func.lower(Role.name) == "admin")
    )
    role = result.scalar_one_or_none()
    if role:
        return role
    role = Role(
        name="ADMIN",
        description="System administrator",
        allows_self_registration=False,
    )
    session.add(role)
    await session.flush()
    return role


async def seed_users(session, admin_role: Role) -> None:
    for item in DEFAULT_USERS:
        email = item["email"].strip().lower()
        result = await session.execute(select(User).where(func.lower(User.email) == email))
        user = result.scalar_one_or_none()

        role_id = admin_role.id if item["login_as"] == "admin" else None
        if user:
            user.login_as = item["login_as"]
            user.role_id = role_id
            user.is_active = True
            user.is_verified = True
            fn, ln = split_display_name(item["name"])
            user.first_name = fn
            user.last_name = ln
            user.name = display_name_from_parts(fn, ln)
            user.country = item.get("country")
            if not user.hashed_password:
                user.hashed_password = get_password_hash(item["password"])
            continue

        fn, ln = split_display_name(item["name"])
        display = display_name_from_parts(fn, ln)
        session.add(
            User(
                first_name=fn,
                last_name=ln,
                name=display,
                email=email,
                phone=None,
                country=item.get("country"),
                latitude=None,
                longitude=None,
                hashed_password=get_password_hash(item["password"]),
                provider="email",
                provider_id=None,
                avatar_url=None,
                login_as=item["login_as"],
                role_id=role_id,
                is_verified=True,
            )
        )
    await session.flush()


async def seed_categories(session) -> None:
    for category_name, sub_names in CATEGORY_TREE.items():
        cat_result = await session.execute(
            select(Category).where(func.lower(Category.name) == category_name.lower())
        )
        category = cat_result.scalar_one_or_none()
        if not category:
            category = Category(
                name=category_name,
                description=None,
                is_active=True,
            )
            session.add(category)
            await session.flush()

        for sub_name in sub_names:
            sub_result = await session.execute(
                select(SubCategory).where(
                    SubCategory.category_id == category.id,
                    func.lower(SubCategory.name) == sub_name.lower(),
                )
            )
            if sub_result.scalar_one_or_none():
                continue
            session.add(
                SubCategory(
                    category_id=category.id,
                    name=sub_name,
                    description=None,
                    is_active=True,
                )
            )
    await session.flush()


async def main() -> None:
    try:
        async with AsyncSessionLocal() as session:
            admin_role = await ensure_admin_role(session)
            await seed_users(session, admin_role)
            await seed_categories(session)
            await session.commit()
        print("Seed completed: users, categories, and subcategories are ready.")
    finally:
        # Prevent aiomysql cleanup on closed event loop during script shutdown.
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
